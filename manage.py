
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.models import User

app = create_app()

@app.cli.command("create-user")
@click.argument("username")
@click.argument("password")
@with_appcontext
def create_user(username, password):
    "Create a new user: flask create-user <username> <password>"
    if User.query.filter_by(username=username).first():
        print("Error: User already exists.")
        return
    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    print(f"User '{username}' created successfully.")

@app.cli.command("db-init")
@with_appcontext
def db_init():
    "Initialize the database"
    db.create_all()
    print("Database initialized.")

if __name__ == "__main__":
    app.run()
