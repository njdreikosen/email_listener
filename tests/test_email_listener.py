"""Test suit for EmailListener class."""

# Imports from other packages
from imapclient import IMAPClient, SEEN
import os
import pytest
from subprocess import Popen, PIPE
import smtplib, ssl
# Imports from this package
from email_listener import EmailListener
from email_listener.email_responder import EmailResponder
from email_listener.helpers import get_time


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
def singlepart_email():
    """Send a singlepart test email with only plain text."""

    # Create an email responder
    email = os.environ['EL_EMAIL']
    app_password = os.environ['EL_APW']
    email_responder = EmailResponder(email, app_password)
    email_responder.login()

    # Set the recipient as this email, in the email_listener folder
    recipient_parts = email_responder.email.split('@')
    recipient = "{}+email_listener@{}".format(recipient_parts[0], recipient_parts[1])

    # Create the test email
    subject = "EmailListener Test"
    text = "This is the plain text message.\nThis is another line.\n"
    # Send the message
    email_responder.send_singlepart_msg(recipient, subject, text)
    email_responder.logout()

    # Run the other fixtures and test
    yield


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
    subject = "EmailListener Test"
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
    attachments_path = os.path.dirname(os.path.abspath(__file__))
    attachments = [os.path.join(attachments_path, "EmailListener_test.txt"),
            os.path.join(attachments_path, "EmailListener_test2.txt")]
    email_responder.send_multipart_msg(recipient, subject, text, html=html,
            attachments=attachments)
    email_responder.logout()

    # Run the other fixtures and test
    yield


@pytest.fixture
def no_subject_email():
    """Send a singlepart test email with no subject."""

    # Create an email responder
    email = os.environ['EL_EMAIL']
    app_password = os.environ['EL_APW']
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
    server.login(email, app_password)

    # Set the recipient as this email, in the email_listener folder
    recipient_parts = email.split('@')
    recipient = "{}+email_listener@{}".format(recipient_parts[0], recipient_parts[1])

    # Create the test email
    text = "This is the plain text message.\nThis is another line.\n"
    # Send the message
    server.sendmail(email, recipient, text)

    # Log out
    server.quit()
    server = None
    # Run the other fixtures and test
    yield


@pytest.fixture
def cleanup():
    """EmailListener test suite teardown, moves the test email to the Trash."""

    # Let the other fixtures and the test run
    yield

    # Create an email listener
    email = os.environ['EL_EMAIL']
    app_password = os.environ['EL_APW']
    server = IMAPClient('imap.gmail.com')
    server.login(email, app_password)
    server.select_folder("email_listener", readonly=False)
    messages = server.search("UNSEEN")
    for uid, message_data in server.fetch(messages, 'RFC822').items():
        print("uid: {}".format(uid))
        server.set_gmail_labels(uid, "\\Trash")
    server.logout()

    # Delete any downloaded attachments
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attachments")
    for file in os.listdir(download_dir):
        file_ext = file.split('.')[-1]
        if (file_ext == "txt"):
            full_path = os.path.join(download_dir, file)
            os.remove(full_path)


def test_init():
    """Test that the EmailListener is initialized as expected."""

    # Create an example email listener object
    el = EmailListener("example@email.com", "badpassword", "Inbox", "/fake/path")
    # Check that all the values are initialized correctly
    check1 = (el.email == "example@email.com")
    check2 = (el.app_password == "badpassword")
    check3 = (el.folder == "Inbox")
    check4 = (el.attachment_dir == "/fake/path")
    check5 = (el.server is None)

    # Check that all the initialized values are correct
    assert check1 and check2 and check3 and check4 and check5


def test_login(email_listener):
    """Test the login function."""

    # Get an imap connection
    email_listener.login()
    check = type(email_listener.server)
    email_listener.logout()

    # Check that the server is initialized
    assert check is IMAPClient


def test_logout(email_listener):
    """Test the logout function."""

    # Get an imap connection
    email_listener.login()

    # Logout of the connection
    email_listener.logout()

    # Check that the sserver is no longer initialized
    assert email_listener.server is None


def test_scrape_invalid_server(email_listener):
    """Check that scrape() raises a ValueError when EmailListener isn't logged in."""

    # Check that the error is raised
    with pytest.raises(ValueError) as err:
        email_listener.scrape()


def test_scrape_singlepart(email_listener, singlepart_email, cleanup):
    """Test the scraping functionality of scrape() for singlepart emails."""

    # Login
    email_listener.login()

    # Scrape the emails, but don't move them
    messages = email_listener.scrape()

    # Go through each return message and make sure they contain what they should
    checks = []
    for key in messages.keys():
        # Test the subject
        subject = messages[key].get("Subject")
        if subject is None:
            checks.append( bool(subject is not None) )
        else:
            checks.append(subject.strip() == "EmailListener Test")

        # Test the plain text message
        plain_text = messages[key].get("Plain_Text")
        if plain_text is None:
            checks.append( bool(plain_text is not None) )
        else:
            # Split the message up by lines, and remove extra whitespace
            plain_text = plain_text.strip().splitlines()
            # There will be two lines if the message isn't blank
            if len(plain_text) == 2:
                checks.append((plain_text[0].strip() == "This is the plain text message.")
                        and (plain_text[1].strip() == "This is another line."))
            else:
                checks.append( bool(len(plain_text) == 2) )

        # Make sure there is no html or attachments
        plain_html = messages[key].get("Plain_HTML")
        html = messages[key].get("HTML")
        attachments = messages[key].get("attachments")
        checks.append( (plain_html is None) and (html is None) and (attachments is None) )

    # Check for the messages again, which should now be seen
    seen = email_listener.server.search("SEEN")
    # Move emails back to original folder
    for uid, message_data in email_listener.server.fetch(seen, 'RFC822').items():
        email_listener.server.remove_flags(uid, [SEEN])

    # Logout
    email_listener.logout()

    # Check that the correct number of emails is found, each section
    # contains what it should, each of the emails is marked as seen, and
    # are still in the same folder.
    assert (len(messages) == 1) and all(checks) and (len(seen) == 1)


def test_scrape_multipart(email_listener, multipart_email, cleanup):
    """Test the scraping functionality of scrape() for multipart emails."""

    # Login
    email_listener.login()

    # Scrape the emails, but don't move them
    messages = email_listener.scrape()

    # Go through each return message and make sure they contain what they should
    checks = []
    for key in messages.keys():
        # Test the subject
        subject = messages[key].get("Subject")
        if subject is None:
            checks.append( bool(subject is not None) )
        else:
            checks.append(subject.strip() == "EmailListener Test")

        # Test the plain text message
        plain_text = messages[key].get("Plain_Text")
        if plain_text is None:
            checks.append( bool(plain_text is not None) )
        else:
            # Split the message up by lines, and remove extra whitespace
            plain_text = plain_text.strip().splitlines()
            # There will be two lines if the message isn't blank
            if len(plain_text) == 2:
                checks.append((plain_text[0].strip() == "This is the plain text message.")
                        and (plain_text[1].strip() == "This is another line."))
            else:
                checks.append( bool(len(plain_text) == 2) )

        # Test the plain text version of the html message
        plain_html = messages[key].get("Plain_HTML")
        if plain_html is None:
            checks.append( bool(plain_html is not None) )
        else:
            # Split the message up by lines, and remove extra whitespace
            plain_html = plain_html.strip().splitlines()
            html = messages[key].get("HTML")
            # There will be two lines if the message isn't blank
            if len(plain_html) == 2:
                checks.append((plain_html[0].strip() == "This is the HTML message.")
                        and (plain_html[1].strip() == "This is another line."))
            else:
                checks.append( bool(len(plain_html) == 2) )

        # Test the pure html message
        html = messages[key].get("HTML")
        if html is None:
            checks.append( bool(html is not None) )
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
                    '    <p>This is the HTML message.<br/>This is another line.<br/></p>\n'
                    '  </body>\n'
                    '</html>')
            # Split the html up by line for comparison
            html_lines = html.splitlines()
            test_html_lines = html.splitlines()
            # Go through the html line by line and compare
            if (len(html_lines) == len(test_html_lines)):
                for i in range(len(html_lines)):
                    checks.append( html_lines[i].strip() == test_html_lines[i].strip() )
            else:
                checks.append( len(html_lines) == len(test_html_lines) )

        # Test any attachments
        attachments = messages[key].get("attachments")
        if attachments is None:
            checks.append( bool(attachments is not None) )
        else:
            if len(attachments) == 2:
                for attachment in attachments:
                    # If there is a file, open it and check the contents
                    if os.path.exists(attachment):
                        with open(attachment, 'r') as file:
                            msg = file.readlines()
                            checks.append((msg[0].strip() ==
                                    "This is the attachment message.")
                                    and (msg[1].strip() == "This is another line."))
                        # Delete the attachment
                        os.remove(attachment)
                    # If the file doesn't exist, fail
                    else:
                        checks.append( bool(os.path.exists(attachment)) )
            else:
                checks.append( bool(len(attachments) == 2) )

    # Check for the messages again, which should now be seen
    seen = email_listener.server.search("SEEN")
    # Move emails back to original folder
    for uid, message_data in email_listener.server.fetch(seen, 'RFC822').items():
        email_listener.server.remove_flags(uid, [SEEN])

    # Logout
    email_listener.logout()

    # Check that the correct number of emails is found, each section
    # contains what it should, each of the emails is marked as seen, and are
    # still in the same folder.
    assert (len(messages) == 1) and all(checks) and (len(seen) == 1)


def test_scrape_no_subject(email_listener, no_subject_email, cleanup):
    """Test the scraping functionality of scrape() for emails with no subject."""

    # Login
    email_listener.login()

    # Scrape the emails, but don't move them
    messages = email_listener.scrape()

    # Go through each return message and make sure they contain what they should
    checks = []
    for key in messages.keys():
        # Test the subject
        subject = messages[key].get("Subject")
        if subject is None:
            checks.append( bool(subject is not None) )
        else:
            checks.append(subject.strip() == "No Subject")

        # Test the plain text message
        plain_text = messages[key].get("Plain_Text")
        if plain_text is None:
            checks.append( bool(plain_text is not None) )
        else:
            # Split the message up by lines, and remove extra whitespace
            plain_text = plain_text.strip().splitlines()
            # There will be two lines if the message isn't blank
            if len(plain_text) == 2:
                checks.append((plain_text[0].strip() == "This is the plain text message.")
                        and (plain_text[1].strip() == "This is another line."))
            else:
                checks.append( bool(len(plain_text) == 2) )

        # Make sure there is no html or attachments
        plain_html = messages[key].get("Plain_HTML")
        html = messages[key].get("HTML")
        attachments = messages[key].get("attachments")
        checks.append( (plain_html is None) and (html is None) and (attachments is None) )

    # Check for the messages again, which should now be seen
    seen = email_listener.server.search("SEEN")
    # Move emails back to original folder
    for uid, message_data in email_listener.server.fetch(seen, 'RFC822').items():
        email_listener.server.remove_flags(uid, [SEEN])

    # Logout
    email_listener.logout()

    # Check that the correct number of emails is found, each section
    # contains what it should, each of the emails is marked as seen, and
    # are still in the same folder.
    assert (len(messages) == 1) and all(checks) and (len(seen) == 1)


def test_scrape_options(email_listener, singlepart_email, cleanup):
    """Test the optional inputs for the scrape function."""

    # Login
    email_listener.login()

    # Check for whether the email_listener2 folder exists
    folder_check = bool(not email_listener.server.folder_exists("email_listener2"))

    # Scrape the emails, moving them to a new folder, and removing the 'seen' flag
    messages = email_listener.scrape(move="email_listener2", unread=True)
    folder_check = folder_check and email_listener.server.folder_exists("email_listener2")

    # Switch folders
    email_listener.server.select_folder("email_listener2", readonly=False)
    # Scrape again, this time deleting the emails
    messages2 = email_listener.scrape(delete=True)

    # Ensure the emails were deleted
    messages3 = email_listener.scrape(unread=True)

    # Remove the email_listener2 folder
    email_listener.server.select_folder("email_listener", readonly=False)
    email_listener.server.delete_folder("email_listener2")
    folder_check = (folder_check and not
            email_listener.server.folder_exists("email_listener2"))

    # Logout
    email_listener.logout()

    # Delete the downloaded attachment
    for key in messages.keys():
        attachments = messages[key].get("attachments")
        if attachments is not None:
            for attachment in attachments:
                if os.path.exists(attachment):
                    os.remove(attachment)

    # Check that the correct number of emails is found, that each of the emails
    # is found in the new folder not marked as seen, and that each of the emails
    # was deleted.
    assert (len(messages) == 1) and (len(messages2) == 1) and (len(messages3) == 0) and folder_check


def test_listen_invalid_server(email_listener):
    """Check that listen() raises a ValueError when EmailListener isn't logged in."""

    # Check that the error is raised
    with pytest.raises(ValueError) as err:
        email_listener.listen(5)


def test_listen(email_listener):
    """Test the liste function."""

    # Spawn a subprocess to send an email in a couple minutes
    subproc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "send_delayed_message.py")
    subproc = Popen(["python3", "{}".format(subproc_path)], stdout=PIPE)

    # Login
    email_listener.login()
    # Set the timeout to a minute (will timeout in 5 minutes)
    timeout = 1

    # Get the starting time
    start_time = get_time()

    # Start the listening process
    email_listener.listen(timeout, delete=True)

    # Get the ending time
    end_time = get_time()

    # Calculate how long it took listen to timeout
    t_out = end_time - start_time

    # Get the list of written files
    written_files = os.listdir(email_listener.attachment_dir)
    for file in written_files:
        # If it isn't a text file, ignore it
        file_ext = file.split('.')[-1]
        if (file_ext != "txt"):
            continue

        # Open the file, and check what's in it
        file_path = os.path.join(email_listener.attachment_dir, file)
        with open(file_path, 'r') as fp:
            msg = fp.readlines()
            msg_check = ((msg[0].strip() == "Subject")
                    and (msg[1].strip() == "")
                    and (msg[2].strip() == "Listen Test")
                    and (msg[3].strip() == "")
                    and (msg[4].strip() == "")
                    and (msg[5].strip() == "Plain_Text")
                    and (msg[6].strip() == "")
                    and (msg[7].strip() == "Received during listen function."))
        # Remove the file
        os.remove(file_path)

    # Check that exactly one file is written (plus provided .gitignore), that
    # the contents of the file are as expected, and that listen() times out
    # after 5 minutes.
    assert (len(written_files) == 2) and msg_check and ((t_out >= 5*60) and (t_out <= (5*60)+30))

