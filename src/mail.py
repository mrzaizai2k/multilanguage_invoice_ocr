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
from email.header import Header

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
                   receivers: list[str] = None, 
                   attachment_paths: Optional[List[str]] = None):
        """
        Function to send email
        email_type: 
        - 'modify_invoice_remind': To remind the employees that the invoices have been extracted, go to website and modify the info
        - 'send_excel': Send email to admin with excel files
        receivers: List of email string
        attachment_paths: List of path to attachment files
        """
        try:
            # Connect to the SMTP server for each email
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.starttls()
            server.login(self.login, self.password)

            if not receivers:
                receivers = self.config["receivers"]    

            message = self._prepare_email(email_type=email_type, receivers=receivers, attachment_paths=attachment_paths)
            server.send_message(message)
            print(f"Email sent successfully to {receivers}")
            if self.logger:
                self.logger.debug(f"Email sent to {receivers}")

        except Exception as e:
            msg = f"Error sending email: {str(e)}"
            print(msg)
            if self.logger:
                self.logger.debug(msg=msg)

        finally:
            # Close the connection after sending the email
            server.quit()

    def _prepare_email(self, email_type: Literal['modify_invoice_remind', 'send_excel'], 
                       receivers: str = None, 
                       attachment_paths: Optional[List[str]] = None):

        config = self.config[email_type]
        subject = config['subject']
        body = config['body']

        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = self.login
        message["To"] = ', '.join(receivers)
        message.attach(MIMEText(body, "plain"))

        # Add attachments
        if attachment_paths:
            self._attach_files(message, attachment_paths=attachment_paths)
            
        return message

    def _attach_files(self, message, attachment_paths):
        for file_path in attachment_paths:
            try:
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)

                # Get the filename and encode it properly
                filename = os.path.basename(file_path)
                encoded_filename = Header(filename).encode()

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename=\"{encoded_filename}\"",
                )
                # Attach each file part to the message
                message.attach(part)

            except FileNotFoundError:
                error_msg = f"File not found: {file_path}. Skipping attachment."
                print(error_msg)
                if self.logger:
                    self.logger.debug(error_msg)

            except Exception as e:
                error_msg = f"Error attaching file {file_path}: {str(e)}. Skipping attachment."
                print(error_msg)
                if self.logger:
                    self.logger.debug(error_msg)


# Example usage:
if __name__ == "__main__":
    from src.Utils.utils import read_config

    config_path = "config/config.yaml"
    config = read_config(path=config_path)
    email_sender = EmailSender(config=config, logger=None)

    email_sender.send_email(
        email_type="modify_invoice_remind",
        receivers=None,
        # attachment_paths=["output/Stdi_08_24.xlsx", "output/1.4437_10578_A3DS GmbH_04_2024 .xlsm"],  # List of file paths
    )
    
    # email_sender.send_email(
    #     email_type="send_excel",
    #     receivers=["mrzaizai2k@gmail.com"],
    #     attachment_paths=["output/Stdi_08_24.xlsx", "output/1.4437_10578_A3DS GmbH_04_2024 .xlsm", "notfoundfile.txt", "output/Tüdi_08_24.xlsx"],  # List of file paths
    # )