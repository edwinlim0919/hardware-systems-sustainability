# Utility functions for running gRPC HotelReservation in tandem with the Intel IPU emulator

import re

# Validates that ip_address string is in a valid format
def validate_ip(ip_address):
    return re.match(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', ip_address)
