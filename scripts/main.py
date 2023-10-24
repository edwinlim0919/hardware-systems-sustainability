# Main script for running gRPC HotelReservation in tandem with the Intel IPU emulator

import sys
import os
import argparse
import logging
import subprocess

import utils
import metadata


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('grpc-hotel-ipu')

def setup_application(application_name, replace_zip, node_ssh_list):
    application_name_upper = application_name.upper()
    if application_name_upper not in metadata.application_info:
        ValueError('specified application does not exist in metadata.appication_info')
    application_info = metadata.application_info[application_name_upper]

    curr_dir = os.getcwd()
    node_ssh_list_path = curr_dir + '/../node-ssh-lists/' + node_ssh_list
    if not os.path.isfile(node_ssh_list_path):
        ValueError('specified ssh command file does not exist grpc-hotel-ipu/ssh-node-lists')
    node_ssh_lines_unfiltered = [line.strip() for line in open(node_ssh_list_path).readlines()]
    node_ssh_lines = []
    for word_list in [line.split()[:-1] for line in node_ssh_lines_unfiltered]:
        full_line = ''
        for word in word_list:
            full_line += (word + ' ')
        node_ssh_lines.append(full_line.strip())

    # Zip grpc-hotel-ipu/datacenter-soc into grpc-hotel-ipu/zipped-applications
    application_dir_path = application_info['manager_dir_path']
    application_zip_path = '../zipped-applications/' + application_name + '.zip'
    application_folder_paths = application_info['zip_paths']
    zip_cmd_arg1 = ''
    for zip_path in application_folder_paths.values():
        zip_cmd_arg1 += (' ' + zip_path)
    zip_str = 'zip -r {0} {1}'
    zip_cmd = zip_str.format(application_zip_path,
                             zip_cmd_arg1)
    logger.info('----------------')
    logger.info('Setting up ' + application_name_upper + '...')
    if os.path.isfile(application_zip_path) and not replace_zip:
        logger.info(application_zip_path + ' already exists and replace-zip not specified, skipping zip step')
    else:
        logger.info('zipping ' + application_zip_path)
        subprocess.Popen(zip_cmd.split()).wait()

    # For each node in node_ssh_list, copy application zip and unzip
    scp_str = 'scp {0} {1}@{2}:{3}'
    scp_r_str = 'scp -r {0} {1}@{2}:{3}'
    ssh_str = 'ssh {0}@{1}'
    unzip_str = 'yes | unzip {0}'
    cp_str = 'cp -R {0} {1}'
    cd_str = 'cd {0}'
    uid = os.getlogin()
    zip_file_name = utils.extract_path_end(application_zip_path)

    procs_list = []
    logger.info('copying, unzipping, and organizing ' + zip_file_name + ' for specified nodes')
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        scp_cmd = scp_str.format(application_zip_path,
                                 uid,
                                 addr_only,
                                 '~/' + zip_file_name)
        procs_list.append(subprocess.Popen(scp_cmd.split()))
    for proc in procs_list:
        proc.wait()

    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = ssh_str.format(uid, addr_only)
        unzip_cmd = unzip_str.format('~/' + zip_file_name)
        procs_list.append(subprocess.Popen(ssh_cmd.split() + [unzip_cmd]))
    for proc in procs_list:
        proc.wait()

    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = ssh_str.format(uid, addr_only)
        cp_cmds = []
        for zip_path in application_folder_paths.values():
            zip_path_end = utils.extract_path_end(zip_path)
            zip_path_dest = '~/' + zip_path_end
            zip_path_src = '~/datacenter-soc/' + zip_path
            cp_cmd = cp_str.format(zip_path_src, zip_path_dest)
            cp_cmds.append(cp_cmd)
        for cp_cmd in cp_cmds:
            procs_list.append(subprocess.Popen(ssh_cmd.split() + [cp_cmd]))
    for proc in procs_list:
        proc.wait()

    # Copy scripts and install dependencies on all nodes
    logger.info('copying setup scripts for specified nodes')
    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        scp_setup_cmd = scp_str.format('../setup.sh',
                                       uid,
                                       addr_only,
                                       '~/setup.sh')
        procs_list.append(subprocess.Popen(scp_setup_cmd.split()))
    for proc in procs_list:
        proc.wait()

    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        scp_scripts_cmd = scp_r_str.format('../scripts',
                                           uid,
                                           addr_only,
                                           '~/scripts')
        procs_list.append(subprocess.Popen(scp_scripts_cmd.split()))
    for proc in procs_list:
        proc.wait()

    # Since ./setup.sh takes a while, run in parallel and wait
    logger.info('running setup scripts in parallel for specified nodes')
    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = ssh_str.format(uid, addr_only)
        setup_cmd = 'cd ~/ ; yes | ./setup.sh'
        procs_list.append(subprocess.Popen(ssh_cmd.split() + [setup_cmd]))
    for proc in procs_list:
        proc.wait()

    # Build docker images for all of the microservices
    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = ssh_str.format(uid, addr_only)
        cd_cmd = cd_str.format(application_info['node_dir_path'])
        docker_build_cmd = cd_cmd + ' ; sudo docker compose build'
        #print(ssh_cmd + ' ' + docker_build_cmd)
        procs_list.append(subprocess.Popen(ssh_cmd.split() +
                          [docker_build_cmd]))
    for proc in procs_list:
        proc.wait()

    logger.info('Set up ' + application_name + ' application successfully.')
    logger.info('----------------')


def setup_docker_swarm(published, target, registry):
    advertise_addr = utils.parse_ifconfig()
    docker_swarm_init_str = 'sudo docker swarm init ' + \
                            '--advertise-addr {0}'
    docker_swarm_init_cmd = docker_swarm_init_str.format(advertise_addr)
    docker_service_create_str = 'sudo docker service create ' + \
                                '--name registry ' + \
                                '--publish published={0},target={1} registry:{2}'
    docker_service_create_cmd = docker_service_create_str.format(published,
                                                                 target,
                                                                 registry)
    logger.info('----------------')
    logger.info('Setting up docker swarm...')
    logger.info('advertise-addr: ' + advertise_addr)
    logger.info('Initializing docker swarm...')
    subprocess.Popen(docker_swarm_init_cmd.split()).wait()
    logger.info('Starting local registry on this node...')
    logger.info('published: ' + str(published))
    logger.info('target: ' + str(target))
    logger.info('registry: ' + str(registry))
    subprocess.Popen(docker_service_create_cmd.split()).wait()
    logger.info('Set up docker swarm successfully.')
    logger.info('----------------')


def join_docker_swarm(node_ssh_list, manager_addr):
    logger.info('----------------')
    logger.info('Joining docker swarm from other nodes...')
    swarm_join_cmd = utils.parse_swarm_join_token_worker()
    logger.info('Swarm join command: ' + swarm_join_cmd)

    curr_dir = os.getcwd()
    node_ssh_list_path = curr_dir + '/../node-ssh-lists/' + node_ssh_list
    if not os.path.isfile(node_ssh_list_path):
        ValueError('specified ssh command file does not exist grpc-hotel-ipu/ssh-node-lists')
    node_ssh_lines_unfiltered = []
    for ssh_line in [line.strip() for line in open(node_ssh_list_path).readlines()]:
        if manager_addr not in ssh_line:
            node_ssh_lines_unfiltered.append(ssh_line)
    node_ssh_lines = []
    for word_list in [line.split()[:-1] for line in node_ssh_lines_unfiltered]:
        full_line = ''
        for word in word_list:
            full_line += (word + ' ')
        node_ssh_lines.append(full_line.strip())
    node_labels = [line.split()[-1] for line in node_ssh_lines_unfiltered]

    ssh_str = 'ssh {0}@{1}'
    uid = os.getlogin()

    procs_list = []
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = ssh_str.format(uid, addr_only)
        procs_list.append(subprocess.Popen(ssh_cmd.split() + [swarm_join_cmd]))
    for proc in procs_list:
        proc.wait()

    #for line in node_ssh_lines_unfiltered:
    #    print(line)
    #for line in node_ssh_lines:
    #    print(line)
    #for label in node_labels:
    #    print(label)

    logger.info('----------------')


def leave_docker_swarm(is_manager):
    docker_swarm_leave_cmd = 'sudo docker swarm leave --force'
    logger.info('----------------')
    logger.info('Leaving docker swarm...')
    if is_manager:
        logger.info('I am a manager! Waiting for all non-manager nodes to leave...')
        # TODO: Make sure all non-manager nodes have left swarm first
    subprocess.Popen(docker_swarm_leave_cmd.split()).wait()
    logger.info('Left swarm successfully.')
    logger.info('----------------')


#def setup_application(application_name, replace_zip, node_ssh_list):


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)

    # Setting up docker swarm
    parser.add_argument('--setup-docker-swarm',
                        dest='setup_docker_swarm',
                        action='store_true',
                        help='specify arg to set up docker swarm')
    parser.add_argument('--published',
                        dest='published',
                        type=int,
                        help='specify the published value for creating docker registry service')
    parser.add_argument('--target',
                        dest='target',
                        type=int,
                        help='specify the target value for creating docker registry service')
    parser.add_argument('--registry',
                        dest='registry',
                        type=int,
                        help='specify the registry value for creating docker registry service')
    # Leaving docker swarm
    parser.add_argument('--leave-docker-swarm',
                        dest='leave_docker_swarm',
                        action='store_true',
                        help='specify arg to leave docker swarm')
    parser.add_argument('--is-manager',
                        dest='is_manager',
                        action='store_true',
                        help='specify arg if current docker node is a manager')
    # Setting up DeathStarBench applications on CloudLab nodes
    parser.add_argument('--setup-application',
                        dest='setup_application',
                        action='store_true',
                        help='specify arg to setup specified application')
    parser.add_argument('--application-name',
                        dest='application_name',
                        type=str,
                        help='provide the name of the application')
    parser.add_argument('--replace-zip',
                        dest='replace_zip',
                        action='store_true',
                        help='replace if .zip already exists in grpc-hotel-ipu/zipped-applications')
    parser.add_argument('--node-ssh-list',
                        dest='node_ssh_list',
                        type=str,
                        help='provide name of file within grpc-hotel-ipu/node-ssh-lists/ containing CloudLab ssh commands')
    # Joining docker swarm from other nodes
    parser.add_argument('--join-docker-swarm',
                        dest='join_docker_swarm',
                        action='store_true',
                        help='specify arg to join docker swarm from other nodes')
    parser.add_argument('--manager-addr',
                        dest='manager_addr',
                        type=str,
                        help='provide name of the node that will manage node and run the workload generator')
    # Starting DeathStarBench applications on CloudLab nodes after setup and swarm initialization
    parser.add_argument('--start-application',
                        dest='start_application',
                        action='store_true',
                        help='specify arg to start specified application')

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    if args.setup_application:
        if args.application_name is None:
            raise ValueError('application name must be provided for application setup')
        if args.node_ssh_list is None:
            raise ValueError('must provide file containing CloudLab ssh node info for application setup')
        setup_application(args.application_name, args.replace_zip, args.node_ssh_list)
    if args.setup_docker_swarm:
        if args.published is None:
            raise ValueError('published value should be specified for creating docker registry service')
        if args.target is None:
            raise ValueError('target value should be specified for creating docker registry service')
        if args.registry is None:
            raise ValueError('registry value should be specified for creating docker registry service')
        setup_docker_swarm(args.published, args.target, args.registry)
    if args.join_docker_swarm:
        if args.node_ssh_list is None:
            raise ValueError('must provide file containing CloudLab ssh node info for application setup')
        if args.manager_addr is None:
            raise ValueError('must provide ssh address of the swarm manager node')
        join_docker_swarm(args.node_ssh_list, args.manager_addr)
    if args.leave_docker_swarm:
        leave_docker_swarm(args.is_manager)
