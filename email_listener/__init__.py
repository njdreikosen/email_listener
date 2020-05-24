"""email_listener: Listen in an email folder and process incoming emails.

Example:

    # Create the listener
    listener = EmailListener("example@email.com", "badpassword", "Inbox", "./files/")
    # Log the listener into the IMAP server
    listener.login()
    # Scrape emails from the folder without moving them
    listener.scrape()
    # Scrape emails from the folder, and move them to the "email_listener" folder
    listener.scrape("email_listener")
    # Listen in the folder for 5 minutes, without moving the emails, and not
    # calling any process function on the emails.
    listener.listen(5)
    # Listen in the folder until 1:30pm, moving each new email to the "email_listener"
    # folder, and calling the processing function 'send_reply()'
    listener.listen([13, 30], "email_listener", send_reply)
    # Log the listener out of the IMAP server
    listener.logout()

"""

# Imports from other packages
import email
import html2text
from imapclient import IMAPClient, SEEN
import os
# Imports from this package
from .helpers import (
    calc_timeout,
    get_time,
)
from .email_processing import write_txt_file


class EmailListener:
    """EmailListener object for listening to an email folder and processing emails.

    Attributes:
        email (str): The email to listen to.
        app_password (str): The password for the email.
        folder (str): The email folder to listen in.
        attachment_dir (str): The file path to the folder to save scraped
            emails and attachments to.
        server (IMAPClient): The IMAP server to log into. Defaults to None.

    """

    def __init__(self, email, app_password, folder, attachment_dir):
        """Initialize an EmailListener instance.

        Args:
            email (str): The email to listen to.
            app_password (str): The password for the email.
            folder (str): The email folder to listen in.
            attachment_dir (str): The file path to folder to save scraped
                emails and attachments to.

        Returns:
            None

        """

        self.email = email
        self.app_password = app_password
        self.folder = folder
        self.attachment_dir = attachment_dir
        self.server = None


    def login(self):
        """Logs in the EmailListener to the IMAP server.

        Args:
            None

        Returns:
            None

        """

        self.server = IMAPClient('imap.gmail.com')
        self.server.login(self.email, self.app_password)
        self.server.select_folder(self.folder, readonly=False)


    def logout(self):
        """Logs out the EmailListener from the IMAP server.

        Args:
            None

        Returns:
            None

        """

        self.server.logout()
        self.server = None


    def scrape(self, move=None, unread=False, delete=False):
        """Scrape unread emails from the current folder.

        Args:
            move (str): The folder to move scraped emails to. Defaults to None.

        Returns:
            A list of the file paths to each scraped email.

        """

        # Ensure server is connected
        if type(self.server) is not IMAPClient:
            raise ValueError("server attribute must be type IMAPClient")

        # List containing the file paths of each file created for an email message
        msg_dict = {}

        # Search for unseen messages
        messages = self.server.search("UNSEEN")
        # For each unseen message
        for uid, message_data in self.server.fetch(messages, 'RFC822').items():
            # Get the message
            email_message = email.message_from_bytes(message_data[b'RFC822'])
            # Get who the message is from
            user_raw = email_message.get_all('From', [])
            user_list = email.utils.getaddresses(user_raw)
            if len(user_list[0]) == 1:
                user = user_list[0][0]
            elif len(user_list[0]) == 2:
                user = user_list[0][1]
            else:
                user = "UnknownEmail"

            # Generate the dict key for this email
            key = "{}_{}".format(uid, user)
            # Generate the value dictionary to be filled later
            val_dict = {}

            # Display notice
            print("PROCESSING: Email UID = {} from {}".format(uid, user))

            # Add the subject
            val_dict["Subject"] = email_message.get('Subject').strip()

            # If the email has multiple parts
            if email_message.is_multipart():
                # For each part
                for part in email_message.walk():
                    # If the part is multipart, pass
                    if part.get_content_maintype() == 'multipart':
                        continue

                    # If the part is an attachment
                    file_name = part.get_filename()
                    if bool(file_name):
                        # Generate file path
                        file_path = os.path.join(self.attachment_dir, file_name)
                        with open(file_path, 'wb') as file:
                            file.write(part.get_payload(decode=True))
                        attachment_list = val_dict.get("attachments")
                        if attachment_list is None:
                            val_dict["attachments"] = ["{}".format(file_path)]
                        else:
                            attachment_list.append("{}".format(file_path))
                            val_dict["attachments"] = attachment_list

                    # If the part is html text
                    elif part.get_content_type() == 'text/html':
                        # Convert the body from html to plain text
                        val_dict["Plain_HTML"] = html2text.html2text(
                                part.get_payload())
                        val_dict["HTML"] = part.get_payload()

                    # If the part is plain text
                    elif part.get_content_type() == 'text/plain':
                        # Get the body
                        val_dict["Plain_Text"] = part.get_payload()

            # If the message isn't multipart
            else:
                val_dict["Plain_Text"] = email_message.get_payload()

            msg_dict[key] = val_dict

            # If the message should be marked as unread
            if bool(unread):
                self.server.remove_flags(uid, [SEEN])

            # If a move folder is specified
            if move is not None:
                try:
                    # Move the message to another folder
                    self.server.move(uid, move)
                except:
                    # Create the folder and move the message to the folder
                    self.server.create_folder(move)
                    self.server.move(uid, move)
            elif bool(delete):
                # Add delete statement
                self.server.set_gmail_labels(uid, "\\Trash")

        return msg_dict


    def listen(self, timeout, process_func=write_txt_file, move=None,
               unread=False, delete=False):
        """Listen in an email folder for incoming emails, and process them.

        Args:
            timeout (int or list): Either an integer representing the number
                of minutes to timeout in, or a list, formatted as [hour, minute]
                of the local time to timeout at.
            move (str): The name of the folder to move processed emails to. If
                None, the emails are not moved or marked as read. Defaults to
                None.
            process_func (function): A function called to further process the
                emails. The function must take only the list of file paths
                returned by the scrape function as an argument. Defaults to the
                example function write_txt_file in the email_processing module.

        Returns:
            None

        """

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
            inner_timeout = get_time() + 60*5
            # Until idle times out
            while (get_time() < inner_timeout):
                # Check for a new response every 30 seconds
                responses = self.server.idle_check(timeout=30)
                print("Server sent:", responses if responses else "nothing")
                # If there is a response
                if (responses):
                    # Suspend the idling
                    self.server.idle_done()
                    # Process the new emails
                    msgs = self.scrape(move=move, unread=unread, delete=delete)
                    # Run the process function
                    process_func(self, msgs)
                    # Restart idling
                    self.server.idle()
            # Stop idling
            self.server.idle_done()
        return

