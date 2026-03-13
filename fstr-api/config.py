import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv('FSTR_DB_HOST', 'localhost')
    DB_PORT = os.getenv('FSTR_DB_PORT', '5432')
    DB_LOGIN = os.getenv('FSTR_DB_LOGIN', 'postgres')
    DB_PASS = os.getenv('FSTR_DB_PASS', '')
    DB_NAME = os.getenv('FSTR_DB_NAME', 'fstr_db')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_LOGIN}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False