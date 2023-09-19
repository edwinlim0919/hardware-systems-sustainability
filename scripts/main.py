# Main script for running gRPC HotelReservation in tandem with the Intel IPU emulator

import sys
import os
import argparse
import logging
import ipaddress

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('grpc-hotel-ipu')

def setup_docker_swarm(advertise_addr):
    logger.info('----------------')
    logger.info('Setting up docker swarm...')
    logger.info('----------------')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    #parser.add_argument('-u', '--user', dest='email', type=str, help='Username/Email used for login')
    #parser.add_argument('-p', '--production', dest='production', action='store_true', help='Example of boolean arg')
    #parser.add_argument('-o', '--option', dest='option', type=str, help='Example of str arg')
    #parser.add_argument('file', metavar='file', type=str, help='Example of a positional argument')
    parser.add_argument('--setup-docker-swarm',
                        action='store_true',
                        help='specify arg to set up docker swarm')
    parser.add_argument('--advertise-addr',
                        type=str,
                        help='')
    args = parser.parse_args()

    if args.setup_docker_swarm:

    #logger.info('--------------')
    #logger.info('Hello World!')
