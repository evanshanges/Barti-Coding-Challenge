from src.extensions import db
from sqlalchemy import Column, Integer, DateTime, ForeignKey

class Appointment(db.Model):
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctor.id'), nullable=True)
    
    def to_dict(self) -> str:
        """ 
        :return: Serializes this object to a dict
        """
        return {
                'id': self.id,
                'doctor_id': self.doctor_id,
                'start_time': self.start_time.isoformat(),
                "end_time": self.end_time.isoformat()
                }