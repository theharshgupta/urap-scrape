import smtplib, ssl


def send_email(error, receiver = "michael.li.gb@berkeley.edu"):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    password = input("Type your password and press enter: ")
    sender =  "michael.li.gb@gmail.com"
    # Create a secure SSL context
    context = ssl.create_default_context()

    SUBJECT = 'CT Scrape Error'
    TEXT = error + "\n\n\n Testing"

    email_text = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.starttls(context=context)  # Secure the connection
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, receiver, email_text)
        server.close()
        print('EMAIL SENT')
    except Exception as e:
        print("Err, something went wrong \n ", e)

send_email("test")