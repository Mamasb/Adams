import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Security and secret key for sessions
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Consider replacing this with a more secure default for dev environments

    # Database configuration using MySQL (ensure .env has DATABASE_* values)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@"
        f"{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance

    # Email configuration (ensure .env has MAIL_* values)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')  # Default to Gmail SMTP server
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))  # Default to 587 for TLS
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'  # Ensure TLS is enabled
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Set from environment
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Set from environment

    # Ensure .env has the proper variables and do not store sensitive information in the repository.
