# from src.extensions import db
# from flask import jsonify
# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from datetime import datetime
# from enum import Enum 

# class DummyModel(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     value = db.Column(db.String, nullable=False)

#     def json(self) -> str:
#         """ 
#         :return: Serializes this object to JSON
#         """
#         return jsonify({'id': self.id, 'value': self.value})

# class Doctors(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     start_time = Column(Integer, nullable=False)  # Start/end times will be in 24 hours format
#     end_time = Column(Integer, nullable=False)
#     available_days = Column(String, nullable=False) # To be "mon,tues,wed,thurs,fri"
#     appointments = db.relationship('Appointments', back_populates='doctor')

#     def is_available(self, selected_start, selected_end, selected_day) -> bool:
#         """
#         :return: Checks if the doctor is available at the selected start/end times
#         """
#         available_days = self.available_days.split(",") # Converts into a list
#         selected_day = selected_day
#         if (
#             selected_end >= selected_start
#             and selected_start >= self.start_time
#             and selected_end <= self.end_time
#             and selected_day in available_days
#         ):
#             return True
#         return False
    
#     def to_dict(self) -> str:
#         """ 
#         :return: Serializes this object to a dict
#         """
#         return {
#                 'id': self.id, 
#                 'name': self.name,
#                 'start_time': self.start_time,
#                 'end_time': self.end_time,
#                 'available_days': self.available_days}
    
# class Appointments(db.Model):
#     id = Column(Integer, primary_key=True)
#     start_time = Column(DateTime, nullable=False)
#     end_time = Column(DateTime, nullable=False)
#     doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=True)
#     doctor = db.relationship('Doctors', back_populates='appointments')

#     def to_dict(self) -> str:
#         """ 
#         :return: Serializes this object to a dict
#         """
#         return {
#                 'id': self.id,
#                 'doctor_id': self.doctor_id,
#                 'start_time': self.start_time.isoformat(),
#                 "end_time": self.end_time.isoformat()
#                 }