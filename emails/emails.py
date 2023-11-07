import os
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from utils.config import config


class Emails(object):
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.port = config.SMTP_PORT

    def _send_email(self, sender, to: list, email_content, cc: list = None, bcc: list = None):
        receivers = [item for sublist in (to, cc, bcc) if sublist is not None for item in sublist]
        print(f"Will send email to {', '.join(receivers)}")
        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                send_errs = server.sendmail(from_addr=sender, to_addrs=receivers, msg=email_content.as_string())
            if not send_errs:
                print(f"Successfully sent email to {', '.join(receivers)}")
            else:
                for key, value in send_errs.items():
                    if key == os.getenv('RETURN_EMAIL_CC'):
                        continue
                    code, message = value
                    error_message = message.decode('utf-8')
                    print(f'Failed to send email to {key}: {code} - {error_message}')

        except smtplib.SMTPRecipientsRefused as e:
            for recipient, (code, message) in e.recipients.items():
                error_message = message.decode('utf-8')
                print(f'Failed to send email to {recipient}: {code} - {error_message}')

    def _attach_excel(self, excel_file):
        with open(excel_file.path, 'rb') as attachment:
            execl = MIMEBase("application", "octet-stream")
            execl.set_payload(attachment.read())
        encoders.encode_base64(execl)
        execl.add_header('Content-Disposition', 'attachment', filename=Header(excel_file.name, 'utf-8').encode())
        return execl

    def send_temp_employee_email(self, excel_file):
        sender = config.TEMP_EMPLOYEE_EMAIL_SENDER
        bcc = config.TEMP_EMPLOYEE_EMAIL_BCC
        with open(os.path.join(os.path.dirname(__file__), 'signature.png'), 'rb') as file:
            signature_img = file.read()
        with open(os.path.join(os.path.dirname(__file__), 'template.html'), 'r', encoding='UTF-8') as file:
            html = file.read()
        message = MIMEMultipart("alternative")
        message["Subject"] = config.TEMP_EMPLOYEE_EMAIL_SUBJECT
        message["From"] = sender
        message["To"] = sender
        html_part = MIMEMultipart("related")
        html = html.replace('${DATE}', config.CST_NOW.strftime('%Y-%m-%d'))
        html = html.replace('${IT_SUPPORT_EMAIL}', config.TEMP_EMPLOYEE_EMAIL_IT_SUPPORT_MAILBOX)
        html_part.attach(MIMEText(html, "html"))
        signature_image = MIMEImage(signature_img)
        signature_image.add_header('Content-ID', '<signature>')
        html_part.attach(signature_image)
        message.attach(html_part)
        message.attach(self._attach_excel(excel_file))

        self._send_email(sender=sender, to=[sender], bcc=[bcc], email_content=message)
