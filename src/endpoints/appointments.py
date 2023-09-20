from flask import Blueprint, jsonify, request
from http import HTTPStatus
from datetime import datetime

from src.extensions import db
from src.models.Doctor import Doctor
from src.models.Appointment import Appointment

from src.helpers.get_doctors_first_available_time import get_doctors_first_available_time
from src.helpers.query_appointments import query_appointments

appointment = Blueprint('/', __name__)

@appointment.route("/appointments", methods=["POST"])
def create_appointment():
    try:
        data = request.get_json()

        # Check for missing or none values in the request data
        # Seperated for clearer messages to the caller
        if 'doctor_id' not in data or data['doctor_id'] is None:
            raise KeyError("doctor_id is missing")
        if 'start_time' not in data or data['start_time'] is None:
            raise KeyError("start_time is missing")
        if 'end_time' not in data or data['end_time'] is None:
            raise KeyError("end_time is missing")
        
        # Check if the type errors
        if not isinstance(data["doctor_id"], int):
            raise TypeError("doctor_id must be an integer.")
        if not isinstance(data['start_time'], str):
            raise TypeError("start_time must be a string.")
        if not isinstance(data['end_time'], str):
            raise TypeError("end_time must be a string.")

        doctor_id = data["doctor_id"]
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])

        # Check that endtime is later than start_time
        if not end_time > start_time:
            raise ValueError("end_time must be later than start_time")

        # Check if appointment for a past time
        current_time = datetime.now()
        if start_time < current_time:
            return jsonify({'error': 'Unavailable'}), HTTPStatus.BAD_REQUEST

        # Check if the doctor exists
        if not isinstance(doctor_id, int):
            raise TypeError("Value must be an integer.")
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Not Found'}), HTTPStatus.NOT_FOUND

        # Check for appointment conflicts
        existing_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time
        ).all()
        if existing_appointments:
            return jsonify({'error': 'Conflict'}), HTTPStatus.CONFLICT

        # Check if the doctor is available for the appointment time
        start_hour = start_time.hour
        # We need to add another hour if the time goes beyond the exact hour eg. 5:30 PM
        end_hour = end_time.hour + 1 if end_time.minute > 0 else end_time.hour
        if doctor.is_available(start_hour, end_hour, start_time.strftime("%a")):
            appointment: Appointment = Appointment(
                doctor_id = doctor.id,
                start_time = start_time,
                end_time = end_time
            )
            db.session.add(appointment)
            db.session.commit()
            return jsonify({'message': 'Created'}), HTTPStatus.CREATED
        else:
            return jsonify({'error': 'Unavailable'}), HTTPStatus.BAD_REQUEST
        
    except (ValueError, TypeError, KeyError) as e:
        # Handle value, type, and key errors
        print(str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
@appointment.route('/appointments', methods=['GET'])
def get_appointments():
    try:
        doctor_id = request.args.get('doctor_id')
        window_start = datetime.fromisoformat(request.args.get('window_start'))
        window_end = datetime.fromisoformat(request.args.get('window_end'))

        # Check if the doctor exists
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'message': 'Not Found'}), HTTPStatus.NOT_FOUND
        
        # This query will contain all appointments within the time window (including overlapping boundries)
        appointments = query_appointments(doctor_id, window_start, window_end)
        return jsonify([appt.to_dict() for appt in appointments]), HTTPStatus.OK
    
    except (ValueError, TypeError, KeyError) as e:
        # Handle value, type, and key errors
        print(str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
@appointment.route('/appointments/first_available', methods=['GET'])
def get_first_available_appointment():
    doctor_id = request.args.get('doctor_id')
    desired_start = datetime.fromisoformat(request.args.get('desired_start'))
    duration = int(request.args.get('duration'))

    # If desired_start does not have a value we can just sure current time
    # if desired_start is None:
    #     desired_start = datetime.now()

    # If doctor id is provided then it will look for the first available time for that specific doctor
    if doctor_id:
        doctor = Doctor.query.get(doctor_id)
        first_available_time = get_doctors_first_available_time(doctor, desired_start, duration)
        print(first_available_time)
        return jsonify(first_available_time), HTTPStatus.OK
    
    # If doctor id is not provided then it will look for the first available time for all docotors 
    # in the database, compile a list and then return the earliest time.
    else:
        doctors = Doctor.query.all()
        available_times = []
        for doctor in doctors:
            available_times.append(get_doctors_first_available_time(doctor, desired_start, duration))
        return jsonify(min(available_times)), HTTPStatus.OK