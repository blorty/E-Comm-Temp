from dotenv import load_dotenv
load_dotenv()

from app import app, db

import os

db_encryption_key = os.environ.get('DB_ENCRYPTION_KEY')

if __name__ == '__main__':
    app.run(debug=True)
