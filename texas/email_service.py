import smtplib, ssl
import json


def send_email(body):
    import smtplib
    #with open('credentials.json') as f:
    #    credentials = json.load(f)
    gmail_user = "urap.project@gmail.com"
    gmail_password = "urap2019"

    sent_from = gmail_user
    to = ['harsh@berkeley.edu']
    SUBJECT = '[URGENT] Utility Scrape Error'
    TEXT = body + "\n\n\n Sent from Harsh's laptop."

    email_text = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        print('EMAIL SENT')
    except Exception as e:
        print("Err, something went wrong \n ", e)


