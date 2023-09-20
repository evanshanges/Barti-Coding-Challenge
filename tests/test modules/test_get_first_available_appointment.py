from http import HTTPStatus
from datetime import datetime, timedelta
from tests.conftest import setup_database, client

class TestGetFirstAvailableAppointment:

    # Helper function to call the api to create appointments
    def call_create_appointment_endpoint(self, setup_database, client, start, end):
        doctor_id = setup_database['doctor_who'].id
        data = {
            'doctor_id': doctor_id,
            'start_time': start.isoformat(" ", "minutes"),
            'end_time': end.isoformat(" ", "minutes")
        }

        return client.post('/appointments', json=data)

    def test_get_first_available_appointment(self, setup_database, client):
        # Doctor who works from 8-4pm
        doctor_id = setup_database['doctor_who'].id
        # Create 5 consecutive appointments starting at 9:00am at 60 min increments
        num_apptmts = 5
        for x in range(num_apptmts):
            start_time = datetime(2023, 10, 9, 9+x)
            end_time = start_time + timedelta(minutes=60)
            self.call_create_appointment_endpoint(setup_database, client, start_time, end_time)
        
        # Test to see if the next available appointment will be right after the 4th appointment at 2PM
        desired_start = datetime(2023, 10, 9, 9)
        duration = 60

        response = client.get(f'/appointments/first_available?doctor_id={doctor_id}&duration={duration}&desired_start={desired_start}')
        assert response.status_code == HTTPStatus.OK
        
        next_available_time = response.get_json()
        assert next_available_time == "2023-10-09 14:00"
    
    def test_get_first_inbetween_appointments(self, setup_database, client):
        # Create another appointment 1 hour after the intial 4 appointments
        doctor_id = setup_database['doctor_who'].id
        start_time = datetime(2023, 10, 9, 15) 
        end_time = datetime(2023, 10, 9, 16)
        self.call_create_appointment_endpoint(setup_database, client, start_time, end_time)

        # Test to see if the next available appointment will be right after the 4th appointment and before the 5th
        desired_start = datetime(2023, 10, 9, 9)
        duration = 60

        response = client.get(f'/appointments/first_available?doctor_id={doctor_id}&duration={duration}&desired_start={desired_start}')
        assert response.status_code == HTTPStatus.OK

        next_available_time = response.get_json()
        assert next_available_time == "2023-10-09 14:00"
    
    # Test to see if the next available appointment will be the next day by setting the duration > 60 mintues
    def test_get_first_appointment_duration(self, setup_database, client):
        doctor_id = setup_database['doctor_who'].id
        desired_start = datetime(2023, 10, 9, 9)
        duration = 90

        response = client.get(f'/appointments/first_available?doctor_id={doctor_id}&duration={duration}&desired_start={desired_start}')
        assert response.status_code == HTTPStatus.OK
        
        next_available_time = response.get_json()
        assert next_available_time == "2023-10-10 08:00"
    
    # Test to if there is no doctor sepcified in the request
    def test_get_first_appointment_all_doctors(self, setup_database, client):
        num_apptmts = 5
        for x in range(num_apptmts):
            start_time = datetime(2023, 10, 16, 9+x)
            end_time = start_time + timedelta(minutes=60)
            data = {
                'doctor_id': setup_database['doctor_strange'].id,
                'start_time': start_time.isoformat(" ", "minutes"),
                'end_time': end_time.isoformat(" ", "minutes")
            }
            client.post('/appointments', json=data)

            start_time = datetime(2023, 10, 16, 8+x)
            end_time = start_time + timedelta(minutes=60)
            data = {
                'doctor_id': setup_database['doctor_who'].id,
                'start_time': start_time.isoformat(" ", "minutes"),
                'end_time': end_time.isoformat(" ", "minutes")
            }
            client.post('/appointments', json=data)

        desired_start = datetime(2023, 10, 16, 8)
        duration = 60

        response = client.get(f'/appointments/first_available?duration={duration}&desired_start={desired_start}')
        assert response.status_code == HTTPStatus.OK

        next_available_time = response.get_json()
        assert next_available_time == "2023-10-16 13:00"