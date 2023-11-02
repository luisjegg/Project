from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
from .models import db, User, Course, Enrollment
from .models import parse_time

views = Blueprint('views', __name__)

# Authentication decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Teacher Routes

@views.route('/teacher')
@login_required
def teacher_dashboard():
    return render_template('teacher/teacher_landing.html')

@views.route('/teacher/courses', methods=['GET'])
@login_required
def get_teacher_courses():
    teacher_id = session.get('user_id')
    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    return jsonify([course.serialize() for course in courses])

@views.route('/teacher/course/<int:course_id>/students', methods=['GET'])
@login_required
def get_students_in_course(course_id):
    enrollments = Enrollment.query.filter_by(course_id=course_id).join(User).all()
    return jsonify([{
        'student_name': enrollment.student.name,
        'grade': enrollment.grade,
        'student_id': enrollment.student_id
    } for enrollment in enrollments])

@views.route('/teacher/course/<int:course_id>/update_grade', methods=['POST'])
@login_required
def update_student_grade(course_id):
    student_id = request.form.get('student_id')
    grade = request.form.get('grade')
    enrollment = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first()
    if enrollment:
        enrollment.grade = grade
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

# Student Routes

@views.route('/student')
@login_required
def student_dashboard():
    student_id = session.get('user_id')
    
    # Get classes student is enrolled in
    enrolled_classes = Enrollment.query.filter_by(student_id=student_id).join(Course).all()
    
    # Get all classes that the student hasn't enrolled in
    enrolled_course_ids = [enrollment.course_id for enrollment in enrolled_classes]
    available_classes = Course.query.filter(~Course.id.in_(enrolled_course_ids)).all()

    # UPDATED LINE BELOW
    return render_template('student/student_landing.html', enrollments=enrolled_classes, courses=available_classes, grades=[e.grade for e in enrolled_classes])

@views.route('/student/my_classes', methods=['GET'])
@login_required
def my_classes():
    student_id = session.get('user_id')
    enrollments = Enrollment.query.filter_by(student_id=student_id).join(Course).all()

    # Seems like there's an oversight in your code here, there were two return statements.
    # I'm using the one which seems more appropriate for the route. 
    return jsonify([{
        'course_id': enrollment.course_id,
        'class_name': enrollment.course.class_name,
        'time': enrollment.course.time
    } for enrollment in enrollments])

@views.route('/student/all_classes', methods=['GET'])
@login_required
def all_classes():
    courses = Course.query.all()
    return jsonify([course.serialize() for course in courses])

@views.route('/student/enroll', methods=['POST'])
@login_required
def enroll_class():
    student_id = session.get('user_id')
    course_id = request.form.get('course_id')
    
    student = User.query.get(student_id)  # Fetch the student object

    for enrollment in student.enrollments:
        existing_course = enrollment.course
        days1, start1, end1 = parse_time(existing_course.time)
        days2, start2, end2 = parse_time(course_to_enroll.time)

        if check_overlap(days1, start1, end1, days2, start2, end2):
            # Handle the overlap. E.g., show an error message and redirect.
            return "You have a time conflict with another class!", 400

    # Check if student is already enrolled
    existing_enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing_enrollment:
        return jsonify({'status': 'error', 'message': 'Already enrolled'}), 400
    
    # Check if the class has reached its capacity
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'status': 'error', 'message': 'Invalid course'}), 400

    if course.enrolled_count >= course.capacity:
        return jsonify({'status': 'error', 'message': 'Class has reached its capacity'}), 400
    
    # Enroll the student
    new_enrollment = Enrollment(student_id=student_id, course_id=course_id, grade=0)  # Assuming a default grade of 0
    db.session.add(new_enrollment)
    db.session.commit()
    
    return redirect(url_for('views.student_dashboard'))



@views.route('/student/remove_class/<int:course_id>', methods=['POST'])  # Changed from enrollment_id to course_id for clarity
@login_required
def remove_class(course_id):
    student_id = session.get('user_id')
    
    enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if not enrollment:
        return jsonify({'status': 'error', 'message': 'Invalid enrollment'}), 400

    if enrollment.student_id != session.get('user_id'):
        return jsonify({'status': 'error', 'message': 'Not authorized'}), 403

    db.session.delete(enrollment)
    db.session.commit()
    
    return redirect(url_for('views.student_dashboard'))
