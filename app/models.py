from flask_sqlalchemy import SQLAlchemy
import re
from datetime import time

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)  # renamed from username to name
    type = db.Column(db.String, nullable=False)  # student, teacher
    password = db.Column(db.String(128))  
    # Relationships for teachers
    taught_courses = db.relationship('Course', back_populates='teacher', cascade='all')

    # Relationships for students
    enrollments = db.relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')
    def __repr__(self):
        return self.name

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)  # Using String for simplicity
    capacity = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    @property
    def enrolled_count(self):
        return db.session.query(Enrollment).filter_by(course_id=self.id).count()
    @property
    def student_count(self):
        return Enrollment.query.filter_by(course_id=self.id).count()
    # Relationship
    teacher = db.relationship('User', back_populates='taught_courses')
    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')

    def serialize(self):
        return {
            'id': self.id,
            'class_name': self.class_name,
            'time': self.time,
            'capacity': self.capacity,
            'teacher_id': self.teacher_id,
            'enrolled_count': self.enrolled_count
        }

    def __repr__(self):
        return self.class_name


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)

    # Relationships
    student = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')


def parse_time(time_str):
    import re
    from datetime import time

    # Extract day abbreviations
    day_abbreviations = ['M', 'T', 'W', 'R', 'F']
    days = [day for day in day_abbreviations if day in time_str]

    # Extract the time
    time_range_match = re.search(r'(\d+:\d+ [APM]+)-(\d+:\d+ [APM]+)', time_str)

    if time_range_match is None:
        raise ValueError(f"Invalid time format: {time_str}")

    start_time_str = time_range_match.group(1)
    end_time_str = time_range_match.group(2)

    start_hour, start_minute = map(int, start_time_str[:-6].split(":"))
    end_hour, end_minute = map(int, end_time_str[:-6].split(":"))

    if 'PM' in start_time_str and start_hour != 12:
        start_hour += 12
    if 'PM' in end_time_str and end_hour != 12:
        end_hour += 12

    return days, time(start_hour, start_minute), time(end_hour, end_minute)
