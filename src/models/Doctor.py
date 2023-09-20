from src.extensions import db
from sqlalchemy import Column, Integer, String

class Doctor(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    start_time = Column(Integer, nullable=False)  # Start/end times will be in 24 hours format
    end_time = Column(Integer, nullable=False)
    available_days = Column(String, nullable=False) # To be "mon,tues,wed,thurs,fri"

    def is_available(self, selected_start: int, selected_end: int, selected_day: str) -> bool:
        """
        :return: Checks if the doctor is available at the selected start/end times
        """
        available_days = self.available_days.split(",") # Converts into a list
        selected_day = selected_day
        if (
            selected_end >= selected_start
            and selected_start >= self.start_time
            and selected_end <= self.end_time
            and selected_day in available_days
        ):
            return True
        return False