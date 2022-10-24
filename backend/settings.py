from dotenv import load_dotenv
import os
 
load_dotenv()
DB_NAME = os.environ.get("DB_NAME")
DB_USER=os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

DB_PATH = 'postgresql://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD,'localhost:5432', DB_NAME)