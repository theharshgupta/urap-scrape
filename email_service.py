import json
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from os.path import basename
from email.mime.text import MIMEText
from email.utils import formatdate


def send_email(body: str, files: list):
    with open('credentials.json') as f:
        credentials = json.load(f)
    gmail_user = credentials['email']
    gmail_password = credentials['password']

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = ', '.join(["harsh@berkeley.edu"])
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = '[URGENT] Utility Scrape Error'

    text = body + "\n\n\n Sent from Harsh's laptop."
    msg.attach(MIMEText(text))
    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, ["harsh@berkeley.edu"], msg.as_string())
        server.close()
        print('EMAIL SENT')
    except Exception as e:
        print("Err, something went wrong \n ", e)
