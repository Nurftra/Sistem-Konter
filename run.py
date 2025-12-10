import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app, db
import app.cli

app = create_app()

with app.app_context():
    db.create_all()
    print("Tabel berhasil dibuat!")

if __name__ == '__main__':
    # Use environment variable for debug mode, default to False if not set
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
