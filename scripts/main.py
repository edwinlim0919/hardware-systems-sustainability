# Main script for running gRPC HotelReservation in tandem with the Intel IPU emulator

import sys
import os
import argparse
import logging
import subprocess

import utils

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('grpc-hotel-ipu')

def setup_docker_swarm(advertise_addr):
    docker_swarm_init_cmd = "sudo docker swarm init " + \
                            "--advertise-addr " + advertise_addr
    utils.parse_ifconfig(logger)

    logger.info('----------------')
    logger.info('Setting up docker swarm...')
    logger.info('advertise-addr: ' + advertise_addr)
    #logger.info(docker_swarm_init_cmd)
    #os.system(docker_swarm_init_cmd)
    #subprocess.Popen(docker_swarm_init_cmd, shell=True).wait()
    logger.info('----------------')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    #parser.add_argument('-u', '--user', dest='email', type=str, help='Username/Email used for login')
    #parser.add_argument('-p', '--production', dest='production', action='store_true', help='Example of boolean arg')
    #parser.add_argument('-o', '--option', dest='option', type=str, help='Example of str arg')
    #parser.add_argument('file', metavar='file', type=str, help='Example of a positional argument')
    parser.add_argument('--setup-docker-swarm',
                        dest='setup_docker_swarm',
                        action='store_true',
                        help='specify arg to set up docker swarm')
    parser.add_argument('--advertise-addr',
                        dest='advertise_addr',
                        type=str,
                        help='advertised address for the docker swarm')
    args = parser.parse_args()

    if args.setup_docker_swarm:
        if (args.advertise_addr is None or
            not isinstance(args.advertise_addr, str) or
            not utils.validate_ip(args.advertise_addr)):
            raise ValueError('advertise-addr IP address in string format is required for setting up a docker swarm')
        setup_docker_swarm(args.advertise_addr)
    #logger.info('--------------')
    #logger.info('Hello World!')
