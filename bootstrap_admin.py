from app import create_app, db
from app.models.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    username = "admin"
    email = "chris.tanton86@gmail.com"
    password = "Password123"

    existing = User.query.filter_by(username=username).first()
    if existing:
        print("Updating existing admin user...")
        existing.email = email
        existing.password_hash = generate_password_hash(password)
        existing.is_admin = True
    else:
        print("Creating new admin user...")
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=True
        )
        db.session.add(user)

    db.session.commit()
    print("Admin user bootstrap complete.")
