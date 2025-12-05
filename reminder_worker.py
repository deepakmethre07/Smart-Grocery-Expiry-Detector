# reminder_worker.py
from apscheduler.schedulers.blocking import BlockingScheduler
from db import list_items
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()


EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_APP_PASSWORD = os.getenv