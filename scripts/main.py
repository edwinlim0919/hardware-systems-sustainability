# Main script for running gRPC HotelReservation in tandem with the Intel IPU emulator

import sys
import os
import argparse
import logging
import subprocess

import utils

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('grpc-hotel-ipu')

def setup_docker_swarm():
    advertise_addr = utils.parse_ifconfig(logger)
    docker_swarm_init_cmd = "sudo docker swarm init " + \
                            "--advertise-addr " + advertise_addr

    logger.info('----------------')
    logger.info('Setting up docker swarm...')
    logger.info('advertise-addr: ' + advertise_addr)
    logger.info('init-cmd: ' + docker_swarm_init_cmd)
    logger.info('Initializing docker swarm...')
    subprocess.Popen(docker_swarm_init_cmd.split()).wait()
    logger.info('Starting local registry on this node...')

    logger.info('Set up docker swarm successfully.')
    logger.info('----------------')

def leave_docker_swarm(is_manager):
    docker_swarm_leave_cmd = "sudo docker swarm leave --force"

    logger.info('----------------')
    logger.info('Leaving docker swarm...')
    if is_manager:
        logger.info('I am a manager! Waiting for all non-manager nodes to leave...')
        # TODO: Make sure all non-manager nodes have left swarm first
    subprocess.Popen(docker_swarm_leave_cmd.split()).wait()
    logger.info('Left swarm successfully.')
    logger.info('----------------')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup-docker-swarm',
                        dest='setup_docker_swarm',
                        action='store_true',
                        help='specify arg to set up docker swarm')
    parser.add_argument('--leave-docker-swarm',
                        dest='leave_docker_swarm',
                        action='store_true',
                        help='specify arg to leave docker swarm')
    parser.add_argument('--is-manager',
                        dest='is_manager',
                        action='store_true',
                        help='specify arg if current docker node is a manager')
    args = parser.parse_args()

    if args.setup_docker_swarm:
        setup_docker_swarm()
    if args.leave_docker_swarm:
        leave_docker_swarm(args.is_manager)
