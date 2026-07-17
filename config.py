import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")

    # MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    # USDA API
    USDA_API_KEY = os.getenv("USDA_API_KEY")
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
