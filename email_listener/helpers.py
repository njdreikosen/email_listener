""" Helper functions for email_listener. """
import datetime


def calc_timeout(timeout) -> float:
    """
    Calculate the time when a timeout should occur in seconds since epoch
    """

    # Get datetime object for the current time
    t = datetime.datetime.now()

    # Calculate time offset based on whether timeout is a
    # list or an int of minutes
    if type(timeout) is list:
        hr = (timeout[0] - t.hour) % 24
        mi = (timeout[1] - t.minute) % 60
        sec = 0 - t.second

        if (timeout[1] - t.minute) < 0:
            hr -= 1
            hr = hr % 24
    elif type(timeout) is int:
        # Convert input minutes to hours and minutes
        hr = timeout // 60
        mi = timeout % 60
        sec = 0
    else:
        # Input isn't an int or list, so it is invalid
        err = ( "timeout must be either a list in the format [hours, minutes] "
                "or an integer representing minutes"
        )
        raise ValueError(err)

    # Calculate the change in time between now and the timeout
    t_delta = datetime.timedelta(seconds=sec, minutes=mi, hours=hr)
    # Calculate the timeout in seconds since epoch
    t_out = (t + t_delta).timestamp()

    # Return the timeout
    return t_out


def get_time() -> float:
    """
    Get the current time in seconds since epoch
    """

    return datetime.datetime.now().timestamp()

