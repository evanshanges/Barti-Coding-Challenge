from http import HTTPStatus
from datetime import datetime, timedelta
from tests.conftest import setup_database, client

class TestCreateAppointment:
    # Helper function to call the api to create appointments
    def call_create_appointment_endpoint(self, setup_database, client, start, end):
        doctor_id = setup_database['doctor_strange'].id
        data = {
            'doctor_id': doctor_id,
            'start_time': start.isoformat(" ", "minutes"),
            'end_time': end.isoformat(" ", "minutes")
        }
        return client.post('/appointments', json=data)

    # Create a general appointment
    def test_create_appointment(self, setup_database, client):
        print("hello")
        start_time = datetime(2023, 10, 19, 9, 30) 

        end_time = start_time + timedelta(minutes = 60)

        response = self.call_create_appointment_endpoint(setup_database, client, start_time, end_time)
        assert response.status_code == HTTPStatus.CREATED
    
    #Create another appointment where there is a conflict by submitting the same times
    def test_create_same_appointment(self, setup_database, client):
        start_time = datetime(2023, 10, 19, 9, 30) 
        end_time = start_time + timedelta(minutes = 60)
        
        response = self.call_create_appointment_endpoint(setup_database, client, start_time, end_time)
        assert response.status_code == HTTPStatus.CONFLICT
    
    # Create another appointment where there is overlap
    def test_create_overlap_appointment(self, setup_database, client):
        start_time = datetime(2023, 10, 19, 10, 00) 
        end_time = start_time + timedelta(minutes = 60)
        
        response = self.call_create_appointment_endpoint(setup_database, client, start_time, end_time)
        assert response.status_code == HTTPStatus.CONFLICT

    # Create another appointment where the doctor is unavailable (hours)
    def test_create_appointment_unavailable_hours(self, setup_database, client):
        start_time = datetime(2023, 10, 20, 9, 15) # 9:15AM
        end_time = datetime(2023, 10, 20, 18, 15) # 6:15PM

        response = self.call_create_appointment_endpoint(setup_database, client, start_time, end_time)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    # Create another appointment where the doctor is unavailable (day)
    def test_create_appointment_unavailable_day(self, setup_database, client):
        start_time = datetime(2023, 10, 22, 9, 15) 
        end_time = start_time + timedelta(minutes = 60)

        response = self.call_create_appointment_endpoint(setup_database, client, start_time, end_time)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    # Create another appointment for a past time
    def test_create_appointment_past(self, setup_database, client):
        start_time = datetime(2023, 9, 10, 9, 15) 
        end_time = start_time + timedelta(minutes = 60)

        response = self.call_create_appointment_endpoint(setup_database, client, start_time, end_time)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    # Create appointments with errors in the request
    def test_create_appointment_with_errors(self, setup_database, client):
        # Create another appointment but doctor does not exist
        start_time = datetime(2023, 10, 19, 9, 30) 
        end_time = start_time + timedelta(minutes = 60)
        data = {
            'doctor_id': 21,
            'start_time': start_time.isoformat(" ", "minutes"),
            'end_time': end_time.isoformat(" ", "minutes")
        }
        response = client.post('/appointments', json=data)
        assert response.status_code == HTTPStatus.NOT_FOUND

        # Create another appointment but params have errors
        start_time = datetime(2023, 10, 19, 9, 30) 
        end_time = start_time + timedelta(minutes = 60)
        data = {
            # 'doctor_id': "string", 
            # 'start_time': start_time.isoformat(" ", "minutes"),
            # 'end_time': end_time.isoformat(" ", "minutes")
            # 'doctor_id': 2, 
            # 'start_time': "asd",
            # 'end_time': end_time.isoformat(" ", "minutes")
            'doctor_id': 12, 
            'start_time': start_time.isoformat(" ", "minutes"),
            'end_time': 123412312
        }
        response = client.post('/appointments', json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST

        # Create another appointment but params have null values
        start_time = datetime(2023, 10, 19, 9, 30) 
        end_time = start_time + timedelta(minutes = 60)
        data = {
            # 'doctor_id': "string", 
            # 'start_time': start_time.isoformat(" ", "minutes"),
            # 'end_time': end_time.isoformat(" ", "minutes")
            # 'doctor_id': 2, 
            # 'start_time': "asd",
            # 'end_time': end_time.isoformat(" ", "minutes")
            'doctor_id': None, 
            'start_time': start_time.isoformat(" ", "minutes"),
            'end_time': end_time.isoformat(" ", "minutes")
        }
        response = client.post('/appointments', json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST