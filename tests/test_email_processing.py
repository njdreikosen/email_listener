"""Test suite for the EmailResponder class."""

# Imports from other packages
import json
import os
import pytest
# Imports from this packages
from email_listener.email_responder import EmailResponder
from email_listener import EmailListener
from email_listener.email_processing import (
    write_txt_file,
    send_basic_reply,
    write_json_file
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


def test_write_txt_file(email_listener, multipart_email):
    """Test write_txt_file used in the scrape function."""

    # Login the email listener
    email_listener.login()
    # Check that the email is there
    msgs = email_listener.scrape()
    file_list = write_txt_file(email_listener, msgs)

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
        file_ext = file.split('.')[-1]
        if (file_ext == "txt"):
            full_path = os.path.join(download_dir, file)
            os.remove(full_path)

    # Check that there is only 1 new email, that it only has one line, and that
    # that line contains the message.
    assert subject_check and plain_text_check and plain_html_check and html_check and attachments_check


def test_write_txt_file_file_exists(email_listener, capsys):
    """Test write_txt_file when a file already exists."""

    # Get the attachments directory, and create a test file
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attachments")
    test_file = os.path.join(download_dir, "file_exists.txt")
    with open(test_file, 'w+') as file:
        file.write("This is the original text.")

    # Create a sample message dictionary (like the return value of scrape())
    msgs = {'file_exists': {'Subject': 'Do not write', 'Plain_Text': 'Do not write'}}
    # Clear any previous stdout output
    captured = capsys.readouterr()

    # Call the function
    file_list = write_txt_file(email_listener, msgs)
    # Ensure the correct message is printed out
    captured = capsys.readouterr()
    test_out = captured.out.strip()

    with open(test_file, 'r') as file:
        lines = file.readlines()

    # Delete any downloaded attachments
    for file in os.listdir(download_dir):
        file_ext = file.split('.')[-1]
        if (file_ext == "txt"):
            full_path = os.path.join(download_dir, file)
            os.remove(full_path)

    # Ensure the file has the correct number of lines
    if len(lines) != 1:
        assert(len(lines) == 1)

    # Check that the correct output is printed, and that the file still contains
    # the original contents.
    assert (test_out == "File has already been created.") and (lines[0].strip() == "This is the original text.")


def test_send_basic_reply(email_listener):
    """Test the send_basic_reply function."""

    # Set the recipient as this email, in the email_listener folder
    recipient_parts = email_listener.email.split('@')
    recipient = "{}+email_listener@{}".format(recipient_parts[0], recipient_parts[1])

    # Create the sample message key
    msg_key = "608_{}".format(recipient)
    # Create a sample message dictionary (like the return value of scrape())
    msgs = {}
    msgs[msg_key] = {'Subject': 'Basic Reply Test',
            'Plain_Text': 'This is a test message.'}

    # Send the automated reply
    file_list = send_basic_reply(email_listener, msgs)

    # There should be exactly one file written
    if (len(file_list) != 1):
        assert (len(file_llist) == 1)

    # Read the file and check its contents
    with open(file_list[0], 'r') as file:
        lines = file.readlines()
        file_check = ((lines[0].strip() == "Subject")
            and (lines[1].strip() == "")
            and (lines[2].strip() == "Basic Reply Test")
            and (lines[3].strip() == "")
            and (lines[4].strip() == "")
            and (lines[5].strip() == "Plain_Text")
            and (lines[6].strip() == "")
            and (lines[7].strip() == "This is a test message."))

    # Delete the written file
    os.remove(file_list[0])

    # Login and scrape the email
    email_listener.login()
    msg_dict = email_listener.scrape(delete=True)

    # Check that the correct info was scraped
    for key in msg_dict.keys():
        # Test the subject
        sub = msg_dict[key].get("Subject")
        if sub is None:
            subject_check = bool(sub is not None)
        else:
            subject_check = (sub.strip() == "Thank you!")

        # Test the plain text message
        plain_text = msg_dict[key].get("Plain_Text")
        if plain_text is None:
            plain_text_check = bool(plain_text is not None)
        else:
            # Split the message up by lines, and remove extra whitespace
            plain_text = plain_text.strip().splitlines()
            # There should be one line
            if len(plain_text) == 1:
                plain_text_check = (plain_text[0].strip()
                        == "Thank you for your email, your request is being processed.")
            else:
                plain_text_check = bool(len(plain_text) == 1)

    # Check that the written file has the correct contents, that only one message
    # was sent, and that the message contained the correct contents.
    assert file_check and (len(msg_dict) == 1) and subject_check and plain_text_check


def test_write_json_file(email_listener, multipart_email):
    """Test write_txt_file when a file already exists."""

    # Login the email listener
    email_listener.login()
    # Check that the email is there
    msgs = email_listener.scrape()
    file_list = write_json_file(email_listener, msgs)

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
            json_dict = json.load(fp)
            if (type(json_dict) != dict):
                assert type(json_dict) == dict

            # Test the subject
            subject = json_dict.get("Subject")
            if (subject is None):
                subject_check = (subject is not None)
            else:
                subject = subject.strip().splitlines()
                if len(subject) == 1:
                    subject_check = (subject[0].strip() == "Email Processing Test")
                else:
                    subject_check = bool(len(subject) == 1)

            # Test the plain text version
            plain_text = json_dict.get("Plain_Text")
            if (plain_text is None):
                plain_text_check = (plain_text is not None)
            else:
                plain_text = plain_text.strip().splitlines()
                if len(plain_text) == 2:
                    plain_text_check = ((plain_text[0].strip()
                            == "This is the plain text message.")
                            and (plain_text[1].strip() == "This is another line."))
                else:
                    plain_text_check = bool(len(plain_text) == 2)

            # Test the plain html version
            plain_html = json_dict.get("Plain_HTML")
            if (plain_html is None):
                plain_html_check = (plain_html is not None)
            else:
                plain_html = plain_html.strip().splitlines()
                if len(plain_html) == 2:
                    plain_html_check = ((plain_html[0].strip()
                            == "This is the HTML message.")
                            and (plain_html[1].strip() == "This is another line."))
                else:
                    plain_html_check = bool(len(plain_html) == 2)

            # Test the pure html version
            pure_html = json_dict.get("HTML")
            if (pure_html is None):
                pure_html_check = (pure_html is not None)
            else:
                pure_html = pure_html.strip().splitlines()
                test_html = ('<!DOCTYPE html PUBLIC '
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
                        '</html>').splitlines()
                if (len(pure_html) == len(test_html)):
                    pure_html_check = True
                    for i in range(len(pure_html)):
                        pure_html_check = (pure_html_check and
                                (pure_html[i].strip() == test_html[i].strip()))
                else:
                    pure_html_check = (len(pure_html) == len(test_html))

            # Test the attachments
            attachments = json_dict.get("attachments")
            if attachments is None:
                attachment_check = bool(attachments is not None)
            else:
                if len(attachments) == 1:
                    # If there is a file, open it and check the contents
                    if os.path.exists(attachments[0]):
                        with open(attachments[0], 'r') as file:
                            msg = file.readlines()
                            print(msg)
                            if (len(msg) == 3):
                                attachment_check = ((msg[0].strip() ==
                                        "This is the attachment message.")
                                        and (msg[1].strip() == "This is another line."))
                            else:
                                attachment_check = bool(len(msg) == 3)
                        # Delete the attachment
                        os.remove(attachments[0])
                    # If the file doesn't exist, fail
                    else:
                        attachment_check = bool(os.path.exists(attachments[0]))
                else:
                    attachment_check = bool(len(attachments) == 1)

    # Delete any downloaded attachments
    download_dir = email_listener.attachment_dir
    for file in os.listdir(download_dir):
        file_ext = file.split('.')[-1]
        if (file_ext == "json"):
            full_path = os.path.join(download_dir, file)
            os.remove(full_path)

    # Check that there is only 1 new email, that it only has one line, and that
    # that line contains the message.
    assert subject_check and plain_text_check and plain_html_check and pure_html_check and attachment_check


def test_write_json_file_file_exists(email_listener, capsys):
    """Test write_txt_file when a file already exists."""

    # Get the attachments directory, and create a test file
    download_dir = email_listener.attachment_dir
    test_file = os.path.join(download_dir, "file_exists.json")
    with open(test_file, 'w+') as file:
        file.write(json.dumps(
                {"Subject": "File Exists", "Plain_Text": "This file exists."}, indent=4))

    # Create a sample message dictionary (like the return value of scrape())
    msgs = {'file_exists': {'Subject': 'Do not write', 'Plain_Text': 'Do not write'}}
    # Clear any previous stdout output
    captured = capsys.readouterr()

    # Call the function
    file_list = write_json_file(email_listener, msgs)
    # Ensure the correct message is printed out
    captured = capsys.readouterr()
    test_out = captured.out.strip()

    with open(test_file, 'r') as file:
        json_obj = json.load(file)

    # Test the subject
    subject = json_obj.get("Subject")
    if subject is None:
        subject_check = (subject is not None)
    else:
        subject_check = (subject.strip() == "File Exists")

    # Test the plain text
    plain_text = json_obj.get("Plain_Text")
    if plain_text is None:
        plain_text_check = (plain_text is not None)
    else:
        plain_text_check = (plain_text.strip() == "This file exists.")

    # Delete any downloaded attachments
    for file in os.listdir(download_dir):
        file_ext = file.split('.')[-1]
        if (file_ext == "json"):
            full_path = os.path.join(download_dir, file)
            os.remove(full_path)

    # Check that the correct output is printed, and that the file still contains
    # the original contents.
    assert (test_out == "File has already been created.") and subject_check and plain_text_check

