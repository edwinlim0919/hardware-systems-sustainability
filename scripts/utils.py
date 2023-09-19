# Utility functions for running gRPC HotelReservation in tandem with the Intel IPU emulator

import re
import subprocess

# Validates that ip_address string is in a valid format
def validate_ip(ip_address):
    return re.match(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', ip_address)

def parse_ifconfig(logger):
    ifconfig_proc = subprocess.Popen(['ifconfig', '-a'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
    ifconfig_text = ifconfig_proc.communicate()[0].decode('utf-8')

    # TODO: Not sure if every docker manager ip will follow 10.10.1.X format, hardcoded for now
    manager_ip_regex = r'10\.10\.1\.[0-9]{1,3}'
    valid_ips = []
    for line in ifconfig_text.splitlines():
        words = line.split()
        prev_word = ''
        for word in words:
            if (prev_word == 'inet' and
                re.match(manager_ip_regex, word)):
                valid_ips.append(word)
            prev_word = word

    if len(valid_ips) != 1:
        raise ValueError('ifconfig parsing error: more than 1 valid docker manager address found')
    return valid_ips[0]
