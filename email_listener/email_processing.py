"""email_processing: Optional processing methods to be used with EmailListener.listen().

Example:

    # Create the EmailListener
    email = "example@gmail.com"
    password = "badpassword"
    folder = "Inbox"
    attachment_dir = "/path/to/attachments"
    el = EmailListener(email, password, folder, attachment_dir)

    # Pass to the listen() function
    timeout = 5
    el.listen(timeout, process_func=write_txt_file)

"""

# Imports from other packages
import json
import os
# Imports from this package
from email_listener.email_responder import EmailResponder


def write_txt_file(email_listener, msg_dict):
    """Write the email message data returned from scrape to text files.

    Args:
        email_listener (EmailListener): The EmailListener object this function
            is used with.
        msg_dict (dict): The dictionary of email message data returned by the
            scraping function.

    Returns:
        A list of file paths of files that were created and written to.

    """

    # List of files to be returned
    file_list = []
    # For each key, create a file and ensure it doesn't exist
    for key in msg_dict.keys():
        file_path = os.path.join(email_listener.attachment_dir, "{}.txt".format(key))
        if os.path.exists(file_path):
            print("File has already been created.")
            continue

        # Open the file
        with open(file_path, "w+") as file:
            # Write the subject to the file
            file.write("Subject\n\n{}\n\n\n".format(msg_dict[key].get("Subject")))
            # Write each section to the file
            for key2 in msg_dict[key].keys():
                val = msg_dict[key][key2]
                # The subject is already writte, skip it
                if (key2 == "Subject"):
                    continue
                # The attachment list will look weird if written as a python list
                if (key2 == "attachments"):
                    files = ""
                    for attachment in val:
                        files = "{}{}\n".format(files, attachment)
                    val = files

                file.write("{}\n\n{}\n\n\n".format(key2, val.strip()))
        # Add the file name to the return list
        file_list.append(file_path)

    return file_list


def send_basic_reply(email_listener, msg_dict):
    """Write the messages to files, and then send a simple automated reply.

    Args:
        email_listener (EmailListener): The EmailListener object this function
            is used with.
        msg_dict (dict): The dictionary of email message data returned by the
            scraping function.

    Returns:
        A list of file paths of files that were created and written to.

    """

    # Write the email messages to files for use later
    file_list = write_txt_file(email_listener, msg_dict)

    er = EmailResponder(email_listener.email, email_listener.app_password)
    er.login()

    # Create the automated response
    subject = "Thank you!"
    message = "Thank you for your email, your request is being processed."

    # For each email
    for key in msg_dict.keys():
        # Split the key up to remove the email uid
        sender_email_parts = key.split('_')
        sender_email = "_".join(sender_email_parts[1:])
        # Send the email
        er.send_singlepart_msg(sender_email, subject, message)

    er.logout()

    return file_list


def write_json_file(email_listener, msg_dict):
    """Write the email message data returned from scrape to json files.

    Args:
        email_listener (EmailListener): The EmailListener object this function
            is used with.
        msg_dict (dict): The dictionary of email message data returned by the
            scraping function.

    Returns:
        A list of file paths of files that were created and written to.

    """

    # List of files to be returned
    file_list = []
    # For each key, create a file and ensure it doesn't exist
    for key in msg_dict.keys():
        file_path = os.path.join(email_listener.attachment_dir, "{}.json".format(key))
        if os.path.exists(file_path):
            print("File has already been created.")
            continue

        # Convert the returned dict to json
        json_obj = json.dumps(msg_dict[key], indent = 4)

        # Open the file
        with open(file_path, "w+") as file:
            # Write the json object to the file
            file.write(json_obj)
        # Add the file name to the return list
        file_list.append(file_path)

    return file_list

