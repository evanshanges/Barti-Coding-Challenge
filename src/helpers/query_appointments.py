from src.models.Appointment import Appointment
from sqlalchemy import or_, and_

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