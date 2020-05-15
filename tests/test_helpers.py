"""Test suit for helper functions."""

# Imports from other packages
import datetime
import pytest
import time
# Import from this package
from email_listener.helpers import (
    calc_timeout,
    get_time
)


def test_calc_timeout_int():
    """Test a timeout given in minutes."""

    # Timeout, in minutes, to test
    t_out = 10

    # Get the current time
    t = time.localtime()

    # Calculate the timeout time
    future = calc_timeout(t_out)

    # Convert current time to seconds
    test = time.mktime(t)

    # Check that the times are within a second of each other, as it
    # doesn't need to be more precise, and ignores command runtime
    # and rounding errors
    assert abs((test + t_out*60) - future) <= 1


def test_calc_timeout_list():
    """Test a timeout given as a time formatted as [hour, minute]."""

    # Set the timeout to midnight
    t_out = [0, 0]
    
    # Get the current time
    t = time.localtime()

    # Calculate the timeout time
    future = calc_timeout(t_out)

    # Convert current time to seconds
    test = time.mktime(t)

    # Get a datetime object at the timeout time
    dt = datetime.datetime.fromtimestamp(future)

    # Check that the timeout is in the future
    check1 = (test < future)
    # Check that the datetime corresponding to the timeout has
    # hours and minutes equal to the input hours and minutes
    check2 = (dt.hour == t_out[0])
    check3 = (dt.minute == t_out[1])

    # Check that all the checks are true
    assert check1 and check2 and check3
    

def test_calc_timeout_invalid_type():
    """Test that a ValueError is raised if the input isn't an int or list."""

    # Check that the error is raised
    with pytest.raises(ValueError) as err:
        calc_timeout("This should fail")

def test_get_time():
    """Check that get_time returns the same time as the time module."""

    # Get the time
    now = get_time()

    # Get the current time and convert it to seconds
    t = time.localtime()
    test = time.mktime(t)

    # Check that the times are within a second of each other, as it
    # doesn't need to be more precise, and ignores command runtime
    # and rounding errors
    assert abs(now - test) <= 1

