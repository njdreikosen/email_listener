"""Test suite for the EmailResponder class."""

# Imports from other packages
from imapclient import IMAPClient, SEEN
import os
import pytest
import smtplib
import time
# Imports from this packages
from email_listener.email_responder import EmailResponder
from email_listener import EmailListener


@pytest.fixture
def email_responder():
    """Returns an EmailResponder instance with email and password taken from env."""

    # Email and password are read from environment variables
    email = os.environ['EL_EMAIL']
    app_password = os.environ['EL_APW']

    return EmailResponder(email, app_password)


@pytest.fixture
def email_listener():
    """Returns an EmailListener instance with email and password taken from env."""

    # Email and password are read from environment variables
    email = os.environ['EL_EMAIL']
    app_password = os.environ['EL_APW']
    # Read from the folder 'email_listener'
    folder = "email_listener"
    # Save attachements to a dir saved in env
    attachment_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "attachments")

    return EmailListener(email, app_password, folder, attachment_dir)


def test_init():
    """Test that the EmailResponder is initialized as expected."""

    # Create an example email responder object
    em = EmailResponder("example@email.com", "badpassword")

    # Check that all the initialized values are correct
    assert (em.email == "example@email.com") and (em.app_password == "badpassword")


def test_login(email_responder):
    """Test the login function with the default arguments."""

    # Login with default settings
    email_responder.login()
    check = type(email_responder.server)
    email_responder.logout()

    # Check that the server is initialized
    assert check is smtplib.SMTP_SSL


def test_logout(email_responder):
    """Test the logout function."""

    # Login and logout
    email_responder.login()
    email_responder.logout()

    # Check that the server is no longer initialized
    assert email_responder.server is None


def test_send_singlepart_msg(email_responder, email_listener):
    """Test the send_singlepart_msg function."""

    # Login the email responder
    email_responder.login()
    # Set the recipient to a folder of the sender email
    email = email_responder.email.split('@')
    recipient = "{}+email_listener@{}".format(email[0], email[1])

    # Construct the message and send it
    subject = "EmailResponder Test"
    message = "This is a test."
    email_responder.send_singlepart_msg(recipient, subject, message)
    # Log out the responder
    email_responder.logout()

    # Login the email listener
    email_listener.login()
    # Check that the email is there
    msgs = email_listener.scrape()

    for key in msgs.keys():
        # Test the subject
        sub = msgs[key].get("Subject")
        if sub is None:
            subject_check = bool(sub is not None)
        else:
            subject_check = (sub.strip() == "EmailResponder Test")

        # Test each of the other sections
        if ((msgs[key].get("Plain_HTML") is not None)
                or (msgs[key].get("HTML") is not None)):
            check = False
        elif (msgs[key].get("Plain_Text") is not None):
            plain_text = msgs[key].get("Plain_Text").strip().splitlines()
            if len(plain_text) == 1:
                check = (plain_text[0].strip() == message)
            else:
                check = False
        else:
            check = False

    # Move the email to the trash
    messages = email_listener.server.search("SEEN")
    for uid, message_data in email_listener.server.fetch(messages, 'RFC822').items():
        email_listener.server.set_gmail_labels(uid, "\\Trash")

    # Log out the email listener
    email_listener.logout()

    # Check that there is only 1 new email, that it only has one line, and that
    # that line contains the message.
    assert (len(msgs) == 1) and check


def test_send_multipart_msg_text_only(email_responder, email_listener):
    """Test the send_multipart_msg function, only sending a plain text message."""

    # Login the email responder
    email_responder.login()
    # Set the recipient to a folder of the sender email
    email = email_responder.email.split('@')
    recipient = "{}+email_listener@{}".format(email[0], email[1])

    # Construct the message and send it
    subject = "EmailResponder Test"
    message = "This is a plain text multipart test.\nThis is another line.\n"
    email_responder.send_multipart_msg(recipient, subject, message)
    # Log out the responder
    email_responder.logout()

    # Give the email time to send
    time.sleep(10)

    # Login the email listener
    email_listener.login()
    # Check that the email is there
    msgs = email_listener.scrape()

    for key in msgs.keys():
        # Test the subject
        sub = msgs[key].get("Subject")
        if sub is None:
            subject_check = bool(sub is not None)
        else:
            subject_check = (sub.strip() == "EmailResponder Test")

        if ((msgs[key].get("Plain_HTML") is not None)
                or (msgs[key].get("HTML") is not None)):
            check = False
        elif (msgs[key].get("Plain_Text") is not None):
            plain_text = msgs[key].get("Plain_Text").strip().splitlines()
            if len(plain_text) == 2:
                check = (plain_text[0].strip() == "This is a plain text multipart test."
                        and plain_text[1].strip() == "This is another line.")
            else:
                check = ( len(plain_text) == 2 )
        else:
            check = ( msgs[key].get("Plain_Text") is not None )

    # Move the email to the trash
    seen = email_listener.server.search("SEEN")
    for uid, message_data in email_listener.server.fetch(seen, 'RFC822').items():
        email_listener.server.set_gmail_labels(uid, "\\Trash")

    # Log out the email listener
    email_listener.logout()

    # Check that there is only 1 new email and that it has the correct contents
    assert ( len(msgs) == 1 ) and subject_check and check


def test_send_multipart_msg_all(email_responder, email_listener):
    """Test the send_multipart_msg function, using every input."""

    # Login the email responder
    email_responder.login()
    # Set the recipient to a folder of the sender email
    email = email_responder.email.split('@')
    recipient = "{}+email_listener@{}".format(email[0], email[1])

    # Construct the message and send it
    subject = "EmailResponder Test"
    # Create the plain text message
    text = "This is the plain text message.\nThis is another line.\n"
    # Create the HTML message
    html = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            '  <head>\n'
            '    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
            '\n'
            '    <title>EmailListener Test</title>\n'
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
            '\n'
            '  </head>\n'
            '  <body>\n'
            '    <img src="cid:image0" alt="Penguin"/>\n'
            '    <p>This is the HTML message.<br/>This is another line.<br/></p>\n'
            '  </body>\n'
            '</html>')
    images = [os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "linux_penguin.png")]
    attachments = [os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "EmailListener_test.txt")]
    email_responder.send_multipart_msg(recipient, subject, text, html=html,
            images=images, attachments=attachments)

    # Log out the responder
    email_responder.logout()

    # Give the email time to send
    time.sleep(10)

    # Login the email listener
    email_listener.login()
    # Check that the email is there
    messages = email_listener.scrape()

    # Go through each return message and make sure they contain what they should
    for key in messages.keys():
        # Test the subject
        sub = messages[key].get("Subject")
        if sub is None:
            subject_check = bool(sub is not None) 
        else:
            subject_check = (sub.strip() == "EmailResponder Test")

        # Test the plain text message
        plain_text = messages[key].get("Plain_Text")
        if plain_text is None:
            plain_text_check = bool(plain_text is not None)
        else:
            # Split the message up by lines, and remove extra whitespace
            plain_text = plain_text.strip().splitlines()
            # There will be two lines if the message isn't blank
            if len(plain_text) == 2:
                plain_text_check = ((plain_text[0].strip() ==
                        "This is the plain text message.")
                        and (plain_text[1].strip() == "This is another line."))
            else:
                plain_text_check = bool(len(plain_text) == 2)

        # Test the plain text version of the html message
        plain_html = messages[key].get("Plain_HTML")
        if plain_html is None:
            plain_html_check = bool(plain_html is not None)
        else:
            # Split the message up by lines, and remove extra whitespace
            plain_html = plain_html.strip().splitlines()
            # There will be two lines if the message isn't blank
            if len(plain_html) == 4:
                plain_html_check = ((plain_html[0].strip() == "![Penguin](cid:image0)")
                        and (plain_html[1].strip() == "")
                        and (plain_html[2].strip() == "This is the HTML message.")
                        and (plain_html[3].strip() == "This is another line."))
            else:
                plain_html_check = bool(len(plain_html) == 4)

        # Test the pure html message
        pure_html = messages[key].get("HTML")
        pure_html_check = True
        if pure_html is None:
            pure_html_check = bool(pure_html is not None)
        else:
            test_html = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
                    '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
                    '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                    '  <head>\n'
                    '    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
                    '\n'
                    '    <title>EmailListener Test</title>\n'
                    '    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
                    '\n'
                    '  </head>\n'
                    '  <body>\n'
                    '    <img src="cid:image0" alt="Penguin"/>\n'
                    '    <p>This is the HTML message.<br/>This is another line.<br/></p>\n'
                    '  </body>\n'
                    '</html>')
            # Split the html up by line for comparison
            html_lines = pure_html.splitlines()
            test_html_lines = html.splitlines()
            # Go through the html line by line and compare
            if (len(html_lines) == len(test_html_lines)):
                for i in range(len(html_lines)):
                    pure_html_check = (pure_html_check and
                            ( html_lines[i].strip() == test_html_lines[i].strip() ))
            else:
                pure_html_check = (len(html_lines) == len(test_html_lines))

        # Test any attachments
        attach = messages[key].get("attachments")
        if attach is None:
            attachment_check = bool(attach is not None)
        else:
            if len(attach) == 1:
                # If there is a file, open it and check the contents
                if os.path.exists(attach[0]):
                    with open(attach[0], 'r') as file:
                        msg = file.readlines()
                        attachment_check = ((msg[0].strip() ==
                                "This is the attachment message.")
                                and (msg[1].strip() == "This is another line."))
                    # Delete the attachment
                    os.remove(attach[0])
                # If the file doesn't exist, fail
                else:
                    attachment_check = bool(os.path.exists(attachments))
            else:
                attachment_check = bool(len(attachments) == 1)

    # Check for the messages again, which should now be seen
    seen = email_listener.server.search("SEEN")
    # Move emails back to original folder
    for uid, message_data in email_listener.server.fetch(seen, 'RFC822').items():
        email_listener.server.set_gmail_labels(uid, "\\Trash")

    # Logout
    email_listener.logout()

    # Check that there is only 1 new email and that it has the correct contents
    assert ( len(messages) == 1 ) and subject_check and plain_text_check and plain_html_check and pure_html_check and attachment_check

