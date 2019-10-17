import smtplib, ssl


def send():
    import smtplib

    gmail_user = "hmgcapital@gmail.com"
    gmail_password = 'S1ll1c0nv@ll3y'

    sent_from = gmail_user
    to = ['harsh@berkeley.edu']
    SUBJECT = 'Pythonic Email Bru'
    TEXT = 'Hey, whaddup dawg?'

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


def send_email():
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "waspgirl20@gmail.com"
    password = "qaqaQAQA1212"

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        receiver_email = "hmgcapital@gmail.com"
        message = """\
        Subject: Hi there

        This message is sent from Harsh's py script!"""

        server.sendmail(sender_email, receiver_email, message)

    except Exception as e:
        # Print any error messages to stdout
        print(e)


send()
