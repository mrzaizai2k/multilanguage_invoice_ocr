import sys
sys.path.append("") 

import sys
import os
import smtplib
from dotenv import load_dotenv
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from typing import Literal, Optional, List
from email.mime.text import MIMEText

load_dotenv()

class EmailSender:
    def __init__(self, config: dict, logger=None):
        self.config = config['mail']
        self.smtp_server = self.config['smtp_server']
        self.port = self.config['port']
        self.login = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.logger = logger

    def send_email(self, email_type: Literal['modify_invoice_remind', 'send_excel'], 
                   receiver: str, 
                   attachment_paths: Optional[List[str]] = None):
        try:
            # Connect to the SMTP server for each email
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.starttls()
            server.login(self.login, self.password)

            message = self._prepare_email(email_type=email_type, receiver=receiver, attachment_paths=attachment_paths)
            server.send_message(message)
            print(f"Email sent successfully to {receiver}")
            if self.logger:
                self.logger.debug(f"Email sent to {receiver}")

        except Exception as e:
            msg = f"Error sending email: {str(e)}"
            print(msg)
            if self.logger:
                self.logger.debug(msg=msg)

        finally:
            # Close the connection after sending the email
            server.quit()

    def _prepare_email(self, email_type: Literal['modify_invoice_remind', 'send_excel'], 
                   receiver: str, 
                   attachment_paths: Optional[List[str]] = None):
        
        config = self.config[email_type]
        subject = config['subject']
        body = config['body']

        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = self.login
        message["To"] = receiver

        message.attach(MIMEText(body, "plain"))

        # Add attachments
        if attachment_paths:
            part = self._prepare_attached_files(attachment_paths=attachment_paths)
            message.attach(part)
        return message

    def _prepare_attached_files(self, attachment_paths):
        for file_path in attachment_paths:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)

            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(file_path)}",
            )
        return part


# Example usage:
if __name__ == "__main__":
    from src.Utils.utils import read_config

    config_path = "config/config.yaml"
    config = read_config(path=config_path)
    email_sender = EmailSender(config=config, logger=None)

    email_sender.send_email(
        email_type="modify_invoice_remind",
        receiver="mrzaizai2k@gmail.com",
        # attachment_paths=["output/Stdi_08_24.xlsx", "output/1.4437_10578_A3DS GmbH_04_2024 .xlsm"],  # List of file paths
    )
    

    email_sender.send_email(
        email_type="send_excel",
        receiver="mrzaizai2k@gmail.com",
        attachment_paths=["output/Stdi_08_24.xlsx"],  # List of file paths
    )