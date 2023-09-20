from flask import Blueprint, jsonify, request
from http import HTTPStatus
from src.extensions import db
from src.models.Doctor import Doctor
from src.models.Appointment import Appointment
from webargs import fields
from webargs.flaskparser import use_args
from datetime import datetime, timedelta
from sqlalchemy import or_, and_


home = Blueprint('/', __name__)

# Helpful documentation:
# https://webargs.readthedocs.io/en/latest/framework_support.html
# https://flask.palletsprojects.com/en/2.0.x/quickstart/#variable-rules


# @home.route('/')
# def index():
#     doctors: Doctors = Doctors.query.all()
#     doc_data = [{'id': doc.id, 'name': doc.name, 'start_time': doc.start_time, 'end_time': doc.end_time} for doc in doctors]
#     print(doc_data)
#     # return jsonify([doctor.json() for doctor in doctors])
#     return jsonify(doc_data)

# Helper function (only using 1 helper, easier to keep it her for now)
def query_appointments(doctor_id, start, end):
    # This query will contain all appointments within the time window (including overlapping boundries)
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        or_(
            and_(Appointment.start_time >= start, Appointment.start_time < end),
            and_(Appointment.end_time > start, Appointment.end_time <= end),
            and_(Appointment.start_time < start, Appointment.end_time > end)
        )
    ).all()
    return appointments


@home.route("/appointments", methods=["POST"])
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
            print("hello")
            return jsonify({'error': 'Conflict'}), HTTPStatus.CONFLICT

        # Check if the doctor is available for the appointment time
        start_hour = start_time.hour
        # We need to add another hour if the time goes beyond the exact hour eg. 5:30 PM
        end_hour = end_time.hour + 1 if end_time.minute > 0 else end_time.hour
        if doctor.is_available(start_hour, end_hour, start_time.strftime("%a")):
            appointment: Appointment = Appointment(
                doctor = doctor,
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
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@home.route('/appointments', methods=['GET'])
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
        return jsonify([appt for appt in appointments]), HTTPStatus.OK
    
    except (ValueError, TypeError, KeyError) as e:
        # Handle value, type, and key errors
        print(str(e))
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@home.route('/appointments/first_available', methods=['GET'])
def get_first_available_appointment():
    doctor_id = request.args.get('doctor_id')
    desired_start = datetime.fromisoformat(request.args.get('desired_start'))
    duration = int(request.args.get('duration'))

    # If doctor id is provided then it will look for the first available time for that specific doctor
    if doctor_id:
        doctor = Doctor.query.get(doctor_id)
        first_available_time = get_docotor_first_available_time(doctor, desired_start, duration)
        print(first_available_time)
        return jsonify(first_available_time), HTTPStatus.OK
    
    # If doctor id is not provided then it will look for the first available time for all docotors 
    # in the database, compile a list and then return the earliest time.
    else:
        doctors = Doctor.query.all()
        available_times = []
        for doctor in doctors:
            available_times.append(get_docotor_first_available_time(doctor, desired_start, duration))
        
        return jsonify(min(available_times)), HTTPStatus.OK

def get_docotor_first_available_time(doctor: Doctor, desired_start: datetime, duration: int) -> datetime:
    # Get doctor details
    doctor_id = doctor.id
    available_days = doctor.available_days
    start_hour = doctor.start_time
    end_hour = doctor.end_time

    # Current day to query appointments for
    curr_day = desired_start 
    apptmt_len = timedelta(minutes=duration)

    # Since this function will always return a time, we can set this to run until we return a value
    while True:
        # Get the previous end / current day docotor start times 
        # this will be the hours that the doctor was not working and we will set it as a time
        # where they aren't available for a new appointment
        prev_end = datetime(curr_day.year, curr_day.month, curr_day.day-1, end_hour)
        curr_start = datetime(curr_day.year, curr_day.month, curr_day.day, start_hour)

        # An unavailable time will be in this format (start_time, end_time)
        unavail_times = [(prev_end, curr_start)]

        # Check if the desired appointment is within the doctor's working hours
        if curr_day.strftime("%a") in available_days:
            # Get the current day's end time of the docotors shift
            curr_end = prev_end + timedelta(days=1)

            # Query all appointments in the current day and add it to the doctor's unavailable times
            appointments = query_appointments(doctor_id, curr_start, curr_end)
            for apptmt in appointments:
                unavail_times.append((apptmt.start_time, apptmt.end_time))
            
            # Get the next off shift of the doctors from the end of the day to the start of the next working hour
            next_start = curr_day + timedelta(days=1)
            unavail_times.append((curr_end, next_start))

            print(unavail_times)

            for i in range(1, len(unavail_times)):
                # Checks if the time and the duration can be sloted between the current unavailable time and the previous unavialable time
                if(unavail_times[i][0] >= desired_start + apptmt_len) and (unavail_times[i][0] - unavail_times[i-1][1] >= apptmt_len):
                    # Check for earliest valid time
                    if(unavail_times[i-1][1] < desired_start):
                        return desired_start.strftime('%Y-%m-%d %H:%M')
                    return unavail_times[i-1][1].strftime('%Y-%m-%d %H:%M')
        curr_day += timedelta(days=1)