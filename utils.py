from pathlib import Path

def convert_date(date: int) -> int:
    """ Convert an epoch timestamp from iPhone to a standard UNIX timestamp. """
    # Apple starts epoch at 2001-01-01
    epoch = 978307200

    if date > epoch * 1000**2:
        # After iOS11, epoch needs to be converted from nanoseconds to seconds and adjusted 31 years
        return date // 1000**3 + epoch
    else:
        # Before iOS11, epoch is already in seconds
        return date + epoch

def read_file(file) -> str:
        with open(file, 'r') as f:
            output = f.read()
        return output