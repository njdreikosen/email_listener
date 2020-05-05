"""email_listener: Listen in an email folder and process incoming emails."""
import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, ssl

from .helpers import (
    calc_timeout,
    get_time,
)

class EmailResponder:
    def __init__(self, email, app_password):
        self.email = email
        self.app_password = app_password
        self.server = None


    def login(self, host="smtp.gmail.com", port=465):
        context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(host, port, context=context)
        self.server.login(self.email, self.app_password)


    def logout(self):
        self.server.quit()
        self.server = None


    def send_singlepart_msg(self, recipient, subject, message):
        msg = "{}\n\n{}".format(subject, message)
        server.sendmail(self.email, recipient, msg)


    def send_multipart_msg(self, recipient, subject, text, html=None, images=None,
                            attachments=None):
        # Overall message object
        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = recipient

        # Create the body
        if (text is not None) or (html is not None):
            msg_body = MIMEMultipart("alternative")

            # If there is a plain text part, attach it
            if text is not None:
                msg_body.attach(MIMEText(text, "plain"))

            # If there is an html part, attach it
            if html is not None:
                # Create a new multipart section
                msg_html = MIMEMultipart("related")
                # Attach the html text
                msg_html.attach(MIMEText(html, "html"))

                # If there are images, include them
                for i in range(len(images)):
                    # Open the image, read it, and name it so that it can be
                    # referenced by name in the html as:
                    # <img src="cid:image[i]">
                    # where [i] is the index of the image in images
                    with open(images[i], 'rb') as fp:
                        img = MIMEImage(fp.read())
                        img.add_header('Content-ID', "<image{}>".format(i))
                    # Attach the image to the html part
                    msg_html.attach(img_data)

                # Attach the html section to the alternative section
                msg_body.attach(msg_html)

            msg.attach(msg_body)

        for file in attachments or []:
            with open(file, "rb") as f:
                part = MIMEApplication(f.read())
                part.add_header('Content-Disposition',
                        "attachment; filename={}".format(os.path.basename(file))
                msg.attach(part)

        self.server.sendmail(self.email, recipient, msg.as_string())

