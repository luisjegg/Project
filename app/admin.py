from flask import redirect, url_for, request, session
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from .models import db, User, Course, Enrollment
from wtforms import SelectField
from werkzeug.security import generate_password_hash
from wtforms.fields import StringField, PasswordField
from wtforms.validators import ValidationError

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if 'logged_in' in session and session['is_admin']:
            return super().index()
        return redirect(url_for('auth.login'))

    @expose('/logout/')
    def logout_view(self):
        session.clear()
        return redirect(url_for('auth.login'))

class UserModelView(ModelView):
    column_list = ('name', 'type')
    form_extra_fields = {
        'type': SelectField('Type', choices=[
            ('student', 'Student'),
            ('teacher', 'Teacher'),
            ('admin', 'Admin')
        ]),
        'password': PasswordField('Password'),
        'name': StringField('Name')
    }

    def is_accessible(self):
        return session.get('is_admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

    def on_model_change(self, form, model, is_created):
        if is_created or form.password.data:
            model.password = generate_password_hash(form.password.data)

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.type.choices = [
            ('student', 'Student'),
            ('teacher', 'Teacher'),
            ('admin', 'Admin')
        ]
        return form_class

class CourseModelView(ModelView):
    column_list = ('class_name', 'teacher', 'time', 'capacity', 'enrolled_students')
    form_columns = ('class_name', 'teacher', 'time', 'capacity')
    form_args = {
        'teacher': {
            'query_factory': lambda: User.query.filter_by(type='teacher')
        }
    }

    def _enrolled_students(view, context, model, name):
        return model.enrolled_count

    column_formatters = {
        'enrolled_students': _enrolled_students
    }
    def is_accessible(self):
        return session.get('is_admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))
    def on_model_change(self, form, model, is_created):
        existing_course = Course.query.filter_by(class_name=model.class_name).first()
        if existing_course and existing_course.id != model.id:
            raise ValidationError('Class with this name already exists.')

            
class EnrollmentModelView(ModelView):
    column_list = ('student', 'course', 'grade')  
    
    form_args = {
        'student': {
            'query_factory': lambda: User.query.filter_by(type='student')
        }
    }

    def is_accessible(self):
        return session.get('is_admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

    def on_model_change(self, form, model, is_created):
        # Check if the student is already enrolled in the given course
        existing_enrollment = Enrollment.query.filter_by(student_id=model.student_id, course_id=model.course_id).first()
        if existing_enrollment and existing_enrollment.id != model.id:
            raise ValidationError('Student is already enrolled in this class.')

        # Only perform the capacity check for new enrollments
        if is_created:
            course = model.course
            current_enrollments = db.session.query(Enrollment).filter_by(course_id=course.id).count()
            

            if (current_enrollments + 1) > (course.capacity + 1):
                
                raise ValidationError(f"Cannot enroll more students. {course.class_name} has reached its capacity.")
               

        
admin = Admin(name='School Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
admin.add_view(UserModelView(User, db.session))
admin.add_view(CourseModelView(Course, db.session))
admin.add_view(EnrollmentModelView(Enrollment, db.session))
