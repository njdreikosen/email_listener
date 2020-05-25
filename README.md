# email_listener

[![Build Status](https://travis-ci.com/njdreikosen/email_listener.svg?branch=master)](https://travis-ci.com/njdreikosen/email_listener)
[![codecov](https://codecov.io/gh/njdreikosen/email_listener/branch/master/graph/badge.svg)](https://codecov.io/gh/njdreikosen/email_listener)
[![Maintainability](https://api.codeclimate.com/v1/badges/bc3e61eb9d5870824e69/maintainability)](https://codeclimate.com/github/njdreikosen/email_listener/maintainability)
[![PyPI version](https://badge.fury.io/py/email-listener.svg)](https://badge.fury.io/py/email-listener)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/email-listener)
[![Wheel Status](https://pypip.in/wheel/email-listener/badge.svg)](https://pypi.python.org/pypi/email-listener/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

email_listener is a Python package for listening in an email folder and processing incoming emails by scraping them, and optionally processing them with a custom processing script. Additionally, the EmailResponder class is included as an easy way to send reply emails.

email_listener currently supports only Gmail, but other email services may work with minor tweaks.


## Basic usage:

```
import email_listener

# Set your email, password, what folder you want to listen to, and where to save attachments
email = "example@gmail.com"
app_password = "password"
folder = "Inbox"
attachment_dir = "/path/to/attachments"
el = email_listener.EmailListener(email, app_password, folder, attachment_dir)

# Log into the IMAP server
el.login()

# Get the emails currently unread in the inbox
messages = el.scrape()
print(messages)

# Start listening to the inbox and timeout after an hour
timeout = 60
el.listen(timeout)
```

The output:
```
{'227_somebody@gmail.com': {'Subject': 'EmailListener Test', 'Plain_Text': 'This is the plain text message.\r\nThis is another line.\r\n', 'Plain_HTML': 'This is the HTML message.  \nThis is another line.  \n\n', 'HTML': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n<html xmlns="http://www.w3.org/1999/xhtml">\r\n  <head>\r\n    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\r\n    <title>EmailListener Test</title>\r\n    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>\r\n  </head>\r\n  <body>\r\n    <p>This is the HTML message.<br/>This is another line.<br/></p>\r\n  </body>\r\n</html>', 'attachments': ['/home/pi/email_listener/tests/attachments/EmailListener_test.txt']}}
```

The output, but prettier:
```
{'227_somebody@gmail.com':
    {'Subject': 'EmailListener Test',
     'Plain_Text': 'This is the plain text message.\r\nThis is another line.\r\n',
     'Plain_HTML': 'This is the HTML message.  \nThis is another line.  \n\n',
     'HTML': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n
              <html xmlns="http://www.w3.org/1999/xhtml">\r\n
                <head>\r\n
                  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\r\n
                  <title>EmailListener Test</title>\r\n
                  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>\r\n
                </head>\r\n
                <body>\r\n
                  <p>This is the HTML message.<br/>This is another line.<br/></p>\r\n
                </body>\r\n
              </html>',
     'attachments': ['/home/pi/email_listener/tests/attachments/EmailListener_test.txt']
    }
}
```

More detailed examples can be found in each module.


## How to Install

`email_listener` is available on pypi
https://pypi.org/project/email-listener/

```
$ pip install email_listener
```


## Package Requirements
- IMAP must be enabled in the 'Forwarding and POP/IMAP' section of the Gmail settings.
- A Google Account app password must be created, which can be done in the 'Security' section of your Google Account page.


## Running Unit Tests

Once the unit test requirements are met, run the unit tests with the following command:
`python3 -m pytest`

#### Unit Test Requirements
Unit tests require a valid gmail account, which requires a few additions:
- A label (or folder) named 'email_listener' must be created
- A filter must be created, which moves any emails sent to '<Your email>+email_listener@gmail.com' to the email_listener label/folder

Along with these changes, the following environmental variables must be created:
`EL_EMAIL` and `EL_APW`

For example, on the Raspian OS, this can be done by adding the following to `/home/pi/.profile`:
```
export EL_EMAIL="[Your Gmail email]"
export EL_APW="[Your Google Account app password]"
```

