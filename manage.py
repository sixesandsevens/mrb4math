from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.models import User

app = create_app()
cli = FlaskGroup(app)

@cli.command("create-user")
def create_user():
    """Create a new user via input prompts."""
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email: ")

    if User.query.filter_by(username=username).first():
        print("Error: User already exists.")
        return

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=True  # You can toggle this
    )
    db.session.add(user)
    db.session.commit()
    print(f"User '{username}' created successfully.")

if __name__ == "__main__":
    cli()
