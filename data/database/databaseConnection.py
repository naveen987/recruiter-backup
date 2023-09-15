from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv('DATABASE_USER')
PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_Name')

if not USERNAME or not PASSWORD:
    raise ValueError("Missing DATABASE_USER or DATABASE_PASSWORD environment variables")

HOST = 'localhost'
PORT = '5432'
DB_URL = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"

engine = create_engine(DB_URL)

def save_to_database(data, table_name="processed_data"):
    data.to_sql(table_name, engine, if_exists='replace', index=False)
    print("Data has been saved in the database.")
