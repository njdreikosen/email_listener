"""Test suite for the EmailResponder class."""

# Imports from other packages
from imapclient import IMAPClient
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
    # Read from the folder 'email_listener2'
    folder = "email_listener2"
    # Save attachements to a dir saved in env
    attachment_dir = os.environ['EL_FOLDER']

    return EmailListener(email, app_password, folder, attachment_dir)


def test_init():
    """Test that the EmailResponder is initialized as expected."""

    # Create an example email responder object
    em = EmailResponder("example@email.com", "badpassword")

    # Check that all the initialized values are correct
    assert (em.email == "example@email.com") and (em.app_password == "badpassword")


def test_login_default(email_responder):
    """Test the login function with the default arguments."""

    # Login with default settings
    email_responder.login()
    check = type(email_responder.server)
    email_responder.logout()

    # Check that the server is initialized
    assert check is smtplib.SMTP_SSL


def test_login_gmail(email_responder):
    """Test the login function with gmail host and port."""

    # Login with Gmail required host and port
    email_responder.login(host="smtp.gmail.com", port="465")
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
    recipient = "{}+email_listener2@{}".format(email[0], email[1])

    # Construct the message and send it
    subject = "EmailResponder Test"
    message = "This is a test."
    email_responder.send_singlepart_msg(recipient, subject, message)
    # Log out the responder
    email_responder.logout()

    # Give the email time to send
    time.sleep(30)

    # Login the email listener
    email_listener.login()
    # Check that the email is there
    msg_list = email_listener.scrape()
    check1 = (len(msg_list) == 1)
    # Open the file, and ensure it contains what we sent
    fp = open(msg_list[0], 'r')
    msg = fp.readlines()
    check2 = (len(msg) == 1)
    check3 = (msg[0].strip() == "This is a test.")
    fp.close()
    # Remove the file, and ensure it is removed
    os.remove(msg_list[0])
    if os.path.exists(msg_list[0]):
        print("ERROR: FILE EXISTS")
        check3 = False

    # Move the email to the trash
    messages = email_listener.server.search("UNSEEN")
    for uid, message_data in email_listener.server.fetch(messages, 'RFC822').items():
        email_listener.server.set_gmail_labels(uid, "\\Trash")

    # Log out the email listener
    email_listener.logout()

    # Check that there is only 1 new email, that it only has one line, and that
    # that line contains the message.
    assert check1 and check2 and check3


#def test_send_multipart_msg_text_only(email_responder, email_listener):
#    """ """
#
#    # Login the email responder
#    email_responder.login()
#    # Set the recipient to a folder of the sender email
#    email = email_responder.email.split('@')
#    recipient = "{}+email_listener2@{}".format(email[0], email[1])
#
#    # Construct the message and send it
#    subject = "EmailResponder Test"
#    message = "This is a plain text multipart test."
#    email_responder.send_multipart_msg(recipient, subject, message)
#    # Log out the responder
#    email_responder.logout()
#
#    # Give the email time to send
#    time.sleep(60)
#
#    # Login the email listener
#    email_listener.login()
#    # Check that the email is there
#    msg_list = email_listener.scrape("Trash")
#    print(msg_list)
#    check1 = (len(msg_list) == 1)
#    # Open the file, and ensure it contains what we sent
#    fp = open(msg_list[0], 'r')
#    msg = fp.readlines()
#    check2 = (len(msg) == 1)
#    check3 = (msg[0].strip() == "This is a plain text multipart test.")
#    fp.close()
#    # Remove the file, and ensure it is removed
#    os.remove(msg_list[0])
#    if os.path.exists(msg_list[0]):
#        print("ERROR: FILE EXISTS")
#        check3 = False
#
#    # Check that there is only 1 new email, that it only has one line, and that
#    # that line contains the message.
#    assert check1 and check2 and check3


#def test_send_multipart_msg_text_html(email_responder):
#    pass

#def test_send_multipart_msg_text_html_images(email_responder):
#    pass

#def test_send_multipart_msg_attachments(email_responder):
#    pass

#def test_send_multipart_msg_all(email_responder):
#    pass


