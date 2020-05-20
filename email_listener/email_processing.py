"""email_processing: Optional processing methods to be used with EmailListener.scrape.

Example:

    # Pass to the scrape function

"""

# Imports from other packages
import os
#from . import EmailListener


def write_to_file(email_listener, msg_dict):
    """Write the email message data returned from scrape.

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
            # Write each section to the file
            for key2 in msg_dict[key].keys():
                val = msg_dict[key][key2]
                if (key2 == "attachments"):
                    files = ""
                    for attachment in val:
                        files = "{}{}\n".format(files, attachment)
                    val = files

                file.write("{}\n\n{}\n\n\n".format(key2, val.strip()))
        # Add the file name to the return list
        file_list.append(file_path)

    return file_list

