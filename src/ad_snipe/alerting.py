from os.path import isfile
from typing import List
from smtplib import SMTP_SSL


class EmailClient:

    def __init__(self, email_address: str, password: str, mail_list: List[str], smtp_server: str,
                 smtp_port: int) -> None:
        self.from_address = email_address
        self.password = password
        self.mail_to = mail_list
        self.server = smtp_server
        self.port = smtp_port

    def send(self, subject: str, message: str) -> None:
        server = SMTP_SSL(self.server, self.port)
        server.ehlo()
        server.login(self.from_address, self.password)
        msg = f"From: {self.from_address}\nTo: {','.join(self.mail_to)}\nSubject: {subject}\n\n{message}"
        server.sendmail(self.from_address, self.mail_to, msg)
        server.close()


def log(data: str) -> None:
    if not isfile('log'):
        with open('log', 'w') as logfile:
            logfile.write("LOGGED EVENTS")
    with open('log') as logfile:
        logs = logfile.readlines()
    logs.append(data)
    with open('log', 'w') as logfile:
        logfile.write('\n'.join(logs))


def email_alert(email_client: EmailClient, event_description: str, content: str) -> None:
    subject = f'Snipe-IT AD Sync alert: {event_description}'
    body = f'{event_description}\n{content}'
    email_client.send(subject, body)
