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
from email_listener.email_processing import (
    write_to_file
)


@pytest.fixture
def email_listener():
    """Returns an EmailListener instance with email and password taken from env."""

    # Email and password are read from environment variables
    email = os.environ['EL_EMAIL']
    app_password = os.environ['EL_APW']
    # Read from the folder 'email_listener'
    folder = "email_listener"
    # Save attachments to a dir saved in env
    attachment_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "attachments")

    return EmailListener(email, app_password, folder, attachment_dir)


@pytest.fixture
def multipart_email():
    """Send a MIME Multipart test email with plain text, html, and attachment elements."""

    # Create an email responder and login
    email = os.environ['EL_EMAIL']
    app_password = os.environ['EL_APW']
    email_responder = EmailResponder(email, app_password)
    email_responder.login()

    # Set the recipient as this email, in the email_listener folder
    recipient_parts = email_responder.email.split('@')
    recipient = "{}+email_listener@{}".format(recipient_parts[0], recipient_parts[1])

    # Create the test email
    subject = "Email Processing Test"
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
            '    <p>This is the HTML message.<br/>This is another line.<br/></p>\n'
            '  </body>\n'
            '</html>')
    attachments = [os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "EmailListener_test.txt")]
    email_responder.send_multipart_msg(recipient, subject, text, html=html,
            attachments=attachments)
    email_responder.logout()

    # Run the other fixtures and test
    yield


def test_write_to_file(email_listener, multipart_email):
    """Test write_to_file used in the scrape function."""

    # Login the email listener
    email_listener.login()
    # Check that the email is there
    msgs = email_listener.scrape()
    file_list = write_to_file(email_listener, msgs)

    # Move the email to the trash
    seen = email_listener.server.search("SEEN")
    for uid, message_data in email_listener.server.fetch(seen, 'RFC822').items():
        email_listener.server.set_gmail_labels(uid, "\\Trash")

    # Log out the email listener
    email_listener.logout()

    # Make sure the length of the file list is 1
    if (len(file_list) != 1):
        assert len(file_list) == 1

    # Get the file, and make sure it exists
    file = file_list[0]
    if not os.path.exists(file):
        assert os.path.exists(file)
    else:
        # Open the file
        with open(file, 'r') as fp:
            # Read in the lines
            lines = fp.readlines()
            index = 0
            # Loop through the lines
            while (index < len(lines)):
                # Current line
                line = lines[index].strip()

                # If the line is empty, go to the next one
                if (line == ""):
                    index += 1

                elif (line == "Subject"):
                    # For saving lines to be tested
                    test_arr = []
                    index += 1
                    while (index < len(lines)):
                        line = lines[index].strip()
                        if ( (line == "Plain_Text") or (line == "Plain_HTML")
                                or (line == "HTML") or (line == "attachments") ):
                            break
                        if (line != ""):
                            test_arr.append(line)
                        # Go to the next line
                        index += 1
                    # Check that the test array contains what it should
                    if (len(test_arr) != 1):
                        subject_check = (len(test_arr) == 1)
                    else:
                        subject_check = (test_arr[0] == "Email Processing Test")

                # If the line is the plain text section header
                elif(line == "Plain_Text"):
                    # For saving lines to be tested
                    test_arr = []
                    # Go to the next line
                    index += 1
                    # Loop through the lines and save them
                    while (index < len(lines)):
                        line = lines[index].strip()
                        if ( (line == "Plain_HTML") or (line == "HTML")
                                or (line == "attachments") ):
                            break
                        if (line != ""):
                            test_arr.append(line)
                        # Go to the next line
                        index += 1
                    # Check that the test array contains what it should
                    if (len(test_arr) != 2):
                        plain_text_check = (len(test_arr) == 2)
                    else:
                        plain_text_check = (
                                (test_arr[0] == "This is the plain text message.")
                                and (test_arr[1] == "This is another line."))

                # If the line is the plain html section header
                elif(line == "Plain_HTML"):
                    # For saving lines to be tested
                    test_arr = []
                    # Go to the next line
                    index += 1
                    # Loop through the lines and save them
                    while (index < len(lines)):
                        line = lines[index].strip()
                        if ( (line == "Plain_Text") or (line == "HTML")
                                or (line == "attachments") ):
                            break
                        if (line != ""):
                            test_arr.append(line)
                        # Go to the next line
                        index += 1
                    # Check that the test array contains what it should
                    if (len(test_arr) != 2):
                        plain_html_check = (len(test_arr) == 2)
                    else:
                        plain_html_check = (
                                (test_arr[0] == "This is the HTML message.")
                                and (test_arr[1] == "This is another line."))

                # If the line is the pure html section header
                elif(line == "HTML"):
                    # For saving lines to be tested
                    test_arr = []
                    # Go to the next line
                    index += 1
                    # Loop through the lines and save them
                    while (index < len(lines)):
                        line = lines[index].strip()
                        if ( (line == "Plain_Text") or (line == "Plain_HTML")
                                or (line == "attachments") ):
                            break
                        if (line != ""):
                            test_arr.append(line)
                        # Go to the next line
                        index += 1
                    # Check that the test array contains what it should
                    html = ('<!DOCTYPE html PUBLIC '
                            '"-//W3C//DTD XHTML 1.0 Transitional//EN" '
                            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
                            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                            '  <head>\n'
                            '    <meta http-equiv="Content-Type" content="text/html; '
                            'charset=UTF-8" />'
                            '\n'
                            '    <title>EmailListener Test</title>\n'
                            '    <meta name="viewport" content="width=device-width, '
                            'initial-scale=1.0"/>'
                            '\n'
                            '  </head>\n'
                            '  <body>\n'
                            '    <p>This is the HTML message.<br/>This is another line.'
                            '<br/></p>\n'
                            '  </body>\n'
                            '</html>')
                    test_html = html.splitlines()
                    if (len(test_arr) != len(test_html)):
                        html_check = (len(test_arr) == len(test_html))
                    else:
                        html_check = True
                        for i in range(len(test_arr)):
                            html_check = (html_check
                                    and (test_arr[i].strip() == test_html[i].strip()))

                # If the line is the attachments section
                elif(line == "attachments"):
                    # For saving lines to be tested
                    test_arr = []
                    # Go to the next line
                    index += 1
                    # Loop through the lines and save them
                    while (index < len(lines)):
                        line = lines[index].strip()
                        if ( (line == "Plain_Text") or (line == "Plain_HTML")
                                or (line == "HTML") ):
                            break
                        if (line != ""):
                            test_arr.append(line)
                        # Go to the next line
                        index += 1
                    # Check that the test array contains what it should
                    if (len(test_arr) != 1):
                        attachments_check = (len(test_arr) == 1)
                    else:
                        attachment_path = os.path.join(os.path.join(os.path.dirname(
                                os.path.abspath(__file__)), "attachments"),
                                "EmailListener_test.txt")
                        print(attachment_path)
                        print(test_arr[0].strip())
                        attachments_check = (test_arr[0].strip()==attachment_path.strip())

                # If an unexpected section is found
                else:
                    assert (line == "")

    # Delete any downloaded attachments
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attachments")
    for file in os.listdir(download_dir):
        full_path = os.path.join(download_dir, file)
        os.remove(full_path)

    # Check that there is only 1 new email, that it only has one line, and that
    # that line contains the message.
    assert subject_check and plain_text_check and plain_html_check and html_check and attachments_check

