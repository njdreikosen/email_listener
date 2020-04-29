"""email_listener: Listen in an email folder and process incoming emails."""
import email
import html2text
from imapclient import IMAPClient
import os

from .helpers import (
    calc_timeout,
    get_time,
)

class email_listener:
    def __init__(self, email, app_password, folder):
        self.email = email
        self.app_password = app_password
        self.folder = folder
        self.server = None


    def login(self):
        self.server = IMAPClient('imap.gmail.com')
        self.server.login(self.email, self.app_password)
        self.server.select_folder(self.folder, readonly=False)


    def logout(self):
        self.server.logout()


    def scrape(self, move):
        # List containing the file paths of each file created for an email message
        msg_list = []

        # Search for unseen messages
        messages = self.server.search("UNSEEN")
        # For each unseen message
        for uid, message_data in self.server.fetch(messages, 'RFC822').items():
            # Get the message
            email_message = email.message_from_bytes(message_data[b'RFC822'])
            # Get who the message is from
            user = email_message.get('From')

            # Display notice
            print("PROCESSING: Email UID = {} from {}".format(uid, user))

            # Base file name
            file_base = "{}_{}_".format(user, uid)
            # Count for number of files created, used to help name files
            file_count = 0
            # File extension
            file_ext = "txt"

            # If the email has multiple parts
            if email_message.is_multipart():
                # For each part
                for part in email_message.walk():
                    # If the part is multipart, pass
                    if part.get_content_maintype() == 'multipart':
                        continue
                    # If the header says the part type is None, pass
                    if part.get('Content-Disposition') is None:
                        continue

                    # If the part is html text
                    if part.get_content_type() == 'text/html':
                        # Convert the body from html to plain text
                        body = html2text.html2text(part.get_payload())
                        # Set the access mode as write to text file
                        access_mode = 'w'
                    # If the part is plain text
                    elif part.get_content_type() == 'text/plain':
                        # Get the body
                        body = part.get_payload()
                        # Set the access mode as write to text file
                        access_mode = 'w'
                    # If the part is an attachment
                    elif bool(part.get_filename()):
                        # Get the body
                        body = part.get_payload(decode=True)
                        # Get the file extension
                        file_ext = part.get_filename().split('.')[-1]
                        # Set the access mode as write to binary file
                        access_mode = 'wb'
                    else:
                        continue

                    # File path name, to be filled below
                    file_path = ""

                    # Create the file path and check that it doesn't exist
                    # If it does, increment file_count and try again
                    while (file_path == "" or os.path.isfile(file_path)):
                        file_name = "{}{}.{}".format(file_base, file_count, file_ext)
                        file_path = os.path.join(file_dir, file_name)
                        file_count += 1

                    # Open the file, write to it, then close it
                    fp = open(file_path, access_mode)
                    fp.write(body)
                    fp.close()
                    msg_list.append(file_path)

            # If the message isn't multipart
            else:
                # Get the body
                body = email_message.as_bytes().decode(encoding='UTF-8')
                # Create the file path
                file_name = "{}.{}".format(file_base, file_ext)
                file_path = os.path.join(file_dir, file_name)
                # Open the file and write to it
                fp = open(file_path, 'w')
                fp.write(body)
                fp.close()
                msg_list.append(file_path)

            # If a move folder is specified
            if move is not None:
                self.server.add_flags(uid, 'SEEN')
                try:
                    # Move the message to another folder
                    self.server.move(uid, move)
                except:
                    # Create the folder and move the message to the folder
                    self.server.create_folder(move)
                    server.move(uid, move)
        return msg_list


    def listen(self, timeout, move=None, process_func=None) -> None:
        # Ensure server is connected
        if type(self.server) is not IMAPClient:
            raise ValueError("server attribute must be type IMAPClient")

        # Get the timeout value
        outer_timeout = calc_timeout(timeout)        

        # Run until the timeout is reached
        while (get_time() < outer_timeout):
            # Start idling
            self.server.idle()
            print("Connection is now in IDLE mode.")
            # Set idle timeout to 5 minutes
            inner_timeout = time.time() + 60*5
            # Until idle times out
            while (datetime.datetime.now() < inner_timeout):
                # Check for a new response every 30 seconds
                responses = self.server.idle_check(timeout=30)
                print("Server sent:", responses if responses else "nothing")
                # If there is a response
                if (responses):
                    # Suspend the idling
                    self.server.idle_done()
                    # Process the new emails
                    msg_files = self.scrape(move)
                    # If a process function is passed in
                    if type(process_func) is 'function':
                        process_func(msg_files)
                    # Restart idling
                    self.server.idle()
            # Stop idling
            self.server.idle_done()
        return



