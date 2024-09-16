import sys
sys.path.append("") 

import os
import smtplib
from socket import gaierror
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailSender:
    def __init__(self):
        # Initialize with login credentials
        self.smtp_server = "smtp.gmail.com"
        self.port = 587
        self.login = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASSWORD')

        # Log in to the SMTP server
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.port)
            self.server.starttls()  # Secure the connection
            self.server.login(self.login, self.password)  # Log in
            print("Logged in successfully!")
        except (gaierror, ConnectionRefusedError):
            print("Failed to connect to the server. Bad connection settings?")
        except smtplib.SMTPServerDisconnected:
            print("Failed to connect to the server. Wrong user/password?")
        except smtplib.SMTPException as e:
            print(f"SMTP error occurred: {str(e)}")

    def send_email(self, subject, body, sender, receiver):
        # Create the email message
        message = f"""\
Subject: {subject}
To: {receiver}
From: {sender}

{body}"""

        # Send the email
        try:
            self.server.sendmail(sender, receiver, message)
            print('Email sent successfully!')
        except smtplib.SMTPException as e:
            print(f"SMTP error occurred: {str(e)}")

    def close_connection(self):
        # Close the SMTP connection
        try:
            self.server.quit()
            print("SMTP server connection closed.")
        except smtplib.SMTPServerDisconnected:
            print("Server already disconnected.")
        except smtplib.SMTPException as e:
            print(f"Error closing SMTP connection: {str(e)}")

# Example usage:
if __name__ == "__main__":
    email_sender = EmailSender()
    email_sender.send_email(
        subject="Test Email", 
        body="This is a test message sent from Python! chat 3.5", 
        sender=email_sender.login,  # The sender will be the logged-in email address
        receiver="mrzaizai2k@gmail.com"  # The recipient's email address
    )
    
    # Explicitly close the connection when done
    email_sender.close_connection()
