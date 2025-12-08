import click
import os
from flask.cli import with_appcontext
from app import db
from app.models import User

@click.group()
def seed():
    """Add seed data to the database."""
    pass

@seed.command()
@with_appcontext
def superadmin():
    """Create the initial superadmin user."""
    if User.query.filter_by(username='superadmin').first():
        click.echo('Superadmin user already exists.')
        return

    superadmin_password = os.environ.get('SUPERADMIN_PASSWORD')
    if not superadmin_password:
        click.echo('WARNING: SUPERADMIN_PASSWORD environment variable is not set.')
        click.echo('Please set the SUPERADMIN_PASSWORD environment variable before running this command.')
        click.echo('Example: set SUPERADMIN_PASSWORD=your_secure_password')
        return

    user = User(username='superadmin', role='superadmin')
    user.set_password(superadmin_password)
    db.session.add(user)
    db.session.commit()
    click.echo('Superadmin user created successfully!')
