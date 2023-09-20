from http import HTTPStatus
from datetime import datetime, timedelta
from tests.conftest import setup_database, client

class TestGetAppointments:
    # Test a 5 day window to search for appointments
    def test_get_appointments(self, setup_database, client):
        doctor_id = setup_database['doctor_who'].id
        window_start = datetime(2023, 10, 2)
        window_end = window_start + timedelta(days=5)

        # Create 1 appointment each day for 5 consecutive days
        num_apptmts = 5
        for x in range(num_apptmts):
            start_time = datetime(2023, 10, 2 + x, 9, 30)
            end_time = start_time + timedelta(hours=1)
            data = {
                'doctor_id': doctor_id,
                'start_time': start_time.isoformat(" ", "minutes"),
                'end_time': end_time.isoformat(" ", "minutes")
            }
            client.post('/appointments', json=data)

        # Create a window where all 5 appointments are inbewteen
        response = client.get(f'/appointments?doctor_id={doctor_id}&window_start={window_start}&window_end={window_end}')
        assert response.status_code == HTTPStatus.OK

        #Make sure we got all the appointments
        appointments = response.get_json()
        assert len(appointments) == num_apptmts

        # Make sure all the start/end times are between the window times
        for apptmt in appointments:
            assert apptmt['doctor_id'] == doctor_id
            assert datetime.fromisoformat(apptmt['start_time']) >= window_start
            assert datetime.fromisoformat(apptmt['end_time']) <= window_end

    # Test a different window frame where only the first 3 days are included
    def test_get_appointments_small_window(self, setup_database, client):
        doctor_id = setup_database['doctor_who'].id
        window_start = datetime(2023, 10, 2, 10, 30)
        window_end = window_start + timedelta(days=3)

        response = client.get(f'/appointments?doctor_id={doctor_id}&window_start={window_start}&window_end={window_end}')
        assert response.status_code == HTTPStatus.OK
        
        appointments = response.get_json()
        assert len(appointments) == 3
        
        for apptmt in appointments:
            assert apptmt['doctor_id'] == doctor_id
            assert datetime.fromisoformat(apptmt['start_time']) >= window_start
            assert datetime.fromisoformat(apptmt['end_time']) <= window_end

    # Test a different window frame where there are 0 appointments
    def test_get_appointments_bad_window(self, setup_database, client):
        doctor_id = setup_database['doctor_who'].id
        window_start = datetime(2023, 10, 31)
        window_end = window_start + timedelta(days=5)

        response = client.get(f'/appointments?doctor_id={doctor_id}&window_start={window_start}&window_end={window_end}')
        assert response.status_code == HTTPStatus.OK
        
        appointments = response.get_json()
        assert len(appointments) == 0
    
    # Test a window where the start or end is between an appointment
    # In this case the appointment should still be returned
    # Since the appointment is from 9:30 to 10:30 everyday then the
    # window start will be at the end of an appointment so it's not included, the window end will
    # be in between so the appointment  will be included, plus the 2 on the days in between, yielding a total of 3
    def test_get_appointments_between_window(self, setup_database, client):
        doctor_id = setup_database['doctor_who'].id
        window_start = datetime(2023, 10, 2, 10, 30)
        window_end = datetime(2023, 10, 5, 9, 45)

        response = client.get(f'/appointments?doctor_id={doctor_id}&window_start={window_start}&window_end={window_end}')
        assert response.status_code == HTTPStatus.OK

        appointments = response.get_json()
        assert len(appointments) == 3