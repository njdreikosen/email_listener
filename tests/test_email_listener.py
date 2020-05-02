""" """
from imapclient import IMAPClient, SEEN
import os
import pytest

from email_listener import EmailListener


@pytest.fixture
def email_listener():
    """
    Returns an EmailListener instance with email and password taken from env
    """

    # Email and password are read from environment variables
    email = os.environ['EL_EMAIL']
    app_password = os.environ['EL_APW']
    # Read from the folder 'email_listener'
    folder = "email_listener"
    # Save attachments to a dir saved in env
    attachment_dir = os.environ['EL_FOLDER']

    return EmailListener(email, app_password, folder, attachment_dir)


def test_init():
    """ """
    # Create an example email listener object
    el = EmailListener("example@email.com", "badpassword", "Inbox", "/fake/path")
    # Check that all the values are initialized correctly
    check1 = (el.email == "example@email.com")
    check2 = (el.app_password == "badpassword")
    check3 = (el.folder == "Inbox")
    check4 = (el.attachment_dir == "/fake/path")
    check5 = (el.server is None)

    assert check1 and check2 and check3 and check4 and check5


def test_login(email_listener):
    """ """
    # Get an imap connection
    email_listener.login()

    assert type(email_listener.server) is IMAPClient


def test_logout(email_listener):
    """ """
    # Get an imap connection
    email_listener.login()

    # Logout of the connection
    email_listener.logout()

    assert email_listener.server is None


def test_scrape_no_move(email_listener):
    """
    Currently has an attachment email, an html email, and a non-multipart email.
    """

    # Login
    email_listener.login()

    # Scrape the emails, but don't move them
    msg_list = email_listener.scrape(None) 

    # Open each file and ensure it has the correct content (same for each email)
    check2 = []
    for i in range(len(msg_list)):
        # Open the file for reading
        fp = open(msg_list[i], 'r')
        # Read it
        msg = fp.readlines()
        # Check that each line contains what it should (minus extra whitespace)
        line1 = (msg[0].strip() == "This is a test message.")
        line2 = (msg[1].strip() == "This is another line.")
        check2.append(line1 and line2)
        # Close the file
        fp.close()
        # Delete the file
        os.remove(msg_list[i])
        # If the file wasn't removed for some reason, fail
        if os.path.exists(msg_list[i]):
            print("ERROR: FILE EXISTS")
            check2[i] = False

    # Scrape again, and ensure the same files are returned, indicating they
    # weren't moved
    check3 = []
    msg_list2 = email_listener.scrape(None)
    # If the same filenames are in the list, it is the same emails, since
    # the filename is built from the sender and the email id
    for i in range(len(msg_list2)):
        if msg_list2[i] in msg_list:
            check3.append(True)
        else:
            check3.append(False)
        # Delete the file
        os.remove(msg_list2[i])

    # Logout
    email_listener.logout()

    # Check that the correct number of emails is found, that each file contains
    # what it is supposed to, and that the files aren't moved and can be scraped
    # by making sure every item in the second list is in the first, and that the
    # second list is not empty
    assert (len(msg_list) == 3) and all(check2) and all(check3) and bool(msg_list2)


def test_scrape_move(email_listener):
    # Login
    email_listener.login()

    # Scrape the emails, but don't move them
    msg_list = email_listener.scrape("email_listener2")

    # Open each file and ensure it has the correct content (same for each email)
    check2 = []
    for i in range(len(msg_list)):
        # Open the file for reading
        fp = open(msg_list[i], 'r')
        # Read it
        msg = fp.readlines()
        # Check that each line contains what it should (minus extra whitespace)
        line1 = (msg[0].strip() == "This is a test message.")
        line2 = (msg[1].strip() == "This is another line.")
        check2.append(line1 and line2)
        # Close the file
        fp.close()
        # Delete the file
        os.remove(msg_list[i])
        # If the file wasn't removed for some reason, fail
        if os.path.exists(msg_list[i]):
            print("ERROR: FILE EXISTS")
            check2[i] = False

    # Scrape again, and ensure the same files are returned, indicating they
    # weren't moved
    check3 = []
    msg_list2 = email_listener.scrape(None)
    # Delete any files that may have been created
    for i in range(len(msg_list2)):
        os.remove(msg_list2[i])

    # Switch folders
    email_listener.server.select_folder("email_listener2", readonly=False)
    # Search the new folder for seen messages (should be the previous messages)
    messages = email_listener.server.search("SEEN")
    
    # Move emails back to original folder
    for uid, message_data in email_listener.server.fetch(messages, 'RFC822').items():
        email_listener.server.remove_flags(uid, [SEEN])
        email_listener.server.move(uid, "email_listener")

    # Logout
    email_listener.logout()

    # Check that the correct number of emails is found, that each file contains
    # what it is supposed to, and that the files are moved to 'email_listener2',
    # and that the files are marked
    assert (len(msg_list) == 3) and all(check2) and not bool(msg_list2) and (len(messages) == 3)


#def test_listen_no_process(email_listener):
    # Login


#def test_listen_process(email_listener):
#    pass


#@pytest.mark.slow
#def test_listen_new_email():
#    pass


#@pytest.mark.slow
#def test_listen_timeout():
#    pass


