import pytest
from src.app import create_app
from src.extensions import db
from src.models.Doctor import Doctor

app = create_app()

# Fixture for database setup
@pytest.fixture(scope='module')
def setup_database():
    with app.app_context():
        db.create_all()
        
        doctor_strange = Doctor(name="Strange", start_time=9, end_time=17, available_days="Mon,Tue,Wed,Thu,Fri")
        doctor_who = Doctor(name="Who", start_time=8, end_time=16, available_days="Mon,Tue,Wed,Thu,Fri")
        db.session.add_all([doctor_strange, doctor_who])
        db.session.commit()

        data = {'doctor_strange': doctor_strange, 'doctor_who':doctor_who}

        yield data
       
        db.session.remove()
        db.drop_all()

# Fixture for the Flask app client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client