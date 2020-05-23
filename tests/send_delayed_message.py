"""email_responder: Log into an email and send emails."""


# Imports from other packages
import os
import smtplib, ssl
import time


# Give the listener a chance to start listening
time.sleep(60)

# Login to an smtp server
email = os.environ['EL_EMAIL']
password = os.environ['EL_APW']
context = ssl.create_default_context()
server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
server.login(email, password)

# Set the recipient as this email, in the email_listener folder
recipient_parts = email.split('@')
recipient = "{}+email_listener@{}".format(recipient_parts[0], recipient_parts[1])

# Create the email
msg = "Subject: Listen Test\n\nReceived during listen function."
server.sendmail(email, recipient, msg)

# Exit the smpt server
server.quit()

