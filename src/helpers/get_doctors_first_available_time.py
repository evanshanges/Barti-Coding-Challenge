from src.extensions import db
from src.models.Doctor import Doctor
from datetime import datetime, timedelta
from src.helpers.query_appointments import query_appointments

def get_doctors_first_available_time(doctor: Doctor, desired_start: datetime, duration: int) -> datetime:
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