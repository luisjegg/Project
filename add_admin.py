from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()


with app.app_context():
    admin_name = 'admin'  # Renamed from admin_username to admin_name
    admin_password = 'adminpassword'
    admin_type = 'admin'

    # Check if the admin user already exists
    existing_admin = User.query.filter_by(name=admin_name).first()  # Change filter_by to use 'name'
    if existing_admin is None:
        # Create new admin user
        admin = User(
            name=admin_name,  # Changed from username to name
            password=generate_password_hash(admin_password),
            type=admin_type
        )
        db.session.add(admin)
        db.session.commit()
        print(f'Admin user {admin_name} added successfully.')
    else:
        print(f'Admin user {admin_name} already exists.')
