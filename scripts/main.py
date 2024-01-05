# Main script for running gRPC HotelReservation in tandem with the Intel IPU emulator

import sys
import os
import argparse
import logging
import subprocess

import utils
import metadata


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('hardware-systems-sustainability')


def setup_application(application_name, replace_zip, node_ssh_list):
    logger.info('----------------')
    application_name_upper = application_name.upper()
    logger.info('Setting up ' + application_name_upper + ' on all Docker Swarm nodes...')

    if application_name_upper not in metadata.application_info:
        ValueError(application_name_upper + ' does not exist in metadata.appication_info')
    application_info = metadata.application_info[application_name_upper]

    node_ssh_lines_unfiltered = [line.strip() for line in utils.get_file_relative_path(node_ssh_list, '../node-ssh-lists').readlines()]
    node_ssh_lines = []
    for word_list in [line.split()[:-1] for line in node_ssh_lines_unfiltered]:
        full_line = ''
        for word in word_list:
            full_line += (word + ' ')
        node_ssh_lines.append(full_line.strip())

    # Zip hardware-systems-sustainability/DeathStarBench into hardware-systems-sustainability/zipped-applications
    dsb_dir_path = '../DeathStarBench'
    dsb_zip_path = '../zipped-applications/DeathStarBench.zip'
    zip_cmd = utils.zip_str.format(dsb_zip_path,
                                   dsb_dir_path)
    if os.path.isfile(dsb_zip_path) and not replace_zip:
        logger.info(dsb_zip_path + ' already exists and replace-zip is not specified, skipping zip step')
    else:
        logger.info('zipping ' + dsb_zip_path)
        subprocess.Popen(zip_cmd.split()).wait()

    # For each node in node_ssh_list, copy application zip and unzip
    uid = os.getlogin()
    zip_file_name = utils.extract_path_end(dsb_zip_path)
    procs_list = []

    # Clearing every node to avoid StrictHostKeyChecking
    home_dir_all = '/users/' + os.getlogin() + '/*'
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = utils.ssh_str.format(uid, addr_only)
        rm_cmd = utils.rm_rf_str.format(home_dir_all)
        procs_list.append(subprocess.Popen(ssh_cmd.split() + [rm_cmd]))
    for proc in procs_list:
        proc.wait()

    logger.info('copying, unzipping, and organizing ' + zip_file_name + ' for specified nodes')
    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        scp_cmd = utils.scp_str.format(dsb_zip_path,
                                       uid,
                                       addr_only,
                                       '~/' + zip_file_name)
        procs_list.append(subprocess.Popen(scp_cmd.split()))
    for proc in procs_list:
        proc.wait()

    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = utils.ssh_str.format(uid, addr_only)
        unzip_cmd = utils.unzip_str.format('~/' + zip_file_name)
        procs_list.append(subprocess.Popen(ssh_cmd.split() + [unzip_cmd]))
    for proc in procs_list:
        proc.wait()

    # Copy scripts and install dependencies on all nodes
    logger.info('copying setup scripts for specified nodes')
    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        scp_cmd = utils.scp_str.format('../setup.sh',
                                       uid,
                                       addr_only,
                                       '~/setup.sh')
        procs_list.append(subprocess.Popen(scp_cmd.split()))
    for proc in procs_list:
        proc.wait()

    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        scp_cmd = utils.scp_r_str.format('../scripts',
                                         uid,
                                         addr_only,
                                         '~/scripts')
        procs_list.append(subprocess.Popen(scp_cmd.split()))
    for proc in procs_list:
        proc.wait()

    # Since ./setup.sh takes a while, run in parallel and wait
    logger.info('running setup scripts in parallel for specified nodes')
    procs_list.clear()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = utils.ssh_str.format(uid, addr_only)
        setup_cmd = 'cd ~/ ; yes | ./setup.sh'
        procs_list.append(subprocess.Popen(ssh_cmd.split() + [setup_cmd]))
    for proc in procs_list:
        proc.wait()

    logger.info('Set up ' + application_name_upper + ' on all Docker Swarm nodes successfully')
    logger.info('----------------')


def setup_docker_swarm():
    logger.info('----------------')
    logger.info('Setting up Docker Swarm with current node as manager...')

    advertise_addr = utils.parse_ifconfig()
    docker_swarm_init_str = 'sudo docker swarm init ' + \
                            '--advertise-addr {0}'
    docker_swarm_init_cmd = docker_swarm_init_str.format(advertise_addr)
    logger.info('advertise-addr: ' + advertise_addr)
    logger.info('Initializing docker swarm...')
    subprocess.Popen(docker_swarm_init_cmd.split()).wait()

    logger.info('Set up Docker Swarm successfully.')
    logger.info('----------------')


def setup_docker_registry(published, target, registry):
    logger.info('----------------')
    logger.info('Setting up Docker registry...')

    docker_service_create_str = 'sudo docker service create ' + \
                                '--name registry ' + \
                                '--publish published={0},target={1} registry:{2}'
    docker_service_create_cmd = docker_service_create_str.format(published,
                                                                 target,
                                                                 registry)
    logger.info('Starting local registry on this node...')
    subprocess.Popen(docker_service_create_cmd.split()).wait()

    logger.info('Set up Docker registry successfully.')
    logger.info('----------------')


def join_docker_swarm(node_ssh_list, manager_addr):
    logger.info('----------------')
    logger.info('Joining Docker Swarm from other nodes...')
    swarm_join_cmd = utils.parse_swarm_join_token_worker()
    logger.info('Swarm join command: ' + swarm_join_cmd)

    node_ssh_lines_unfiltered = []
    for ssh_line in [line.strip() for line in utils.get_file_relative_path(node_ssh_list, '../node-ssh-lists').readlines()]:
        if manager_addr not in ssh_line:
            node_ssh_lines_unfiltered.append(ssh_line)
    node_ssh_lines = []
    for word_list in [line.split()[:-1] for line in node_ssh_lines_unfiltered]:
        full_line = ''
        for word in word_list:
            full_line += (word + ' ')
        node_ssh_lines.append(full_line.strip())
    node_labels = [line.split()[-1] for line in node_ssh_lines_unfiltered]

    uid = os.getlogin()
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = utils.ssh_str.format(uid, addr_only)
        subprocess.Popen(ssh_cmd.split() + [swarm_join_cmd]).wait()

    logger.info('All nodes have joined Docker Swarm successfully')
    logger.info('----------------')


def leave_docker_swarm(node_ssh_list, manager_addr):
    logger.info('----------------')
    logger.info('Leaving Docker Swarm from all nodes...')
    swarm_leave_cmd = 'sudo docker swarm leave --force'
    logger.info('Swarm leave command: ' + swarm_leave_cmd)

    node_ssh_lines_unfiltered = []
    node_ssh_lines_manager = ''
    for ssh_line in [line.strip() for line in utils.get_file_relative_path(node_ssh_list, '../node-ssh-lists').readlines()]:
        if manager_addr not in ssh_line:
            node_ssh_lines_unfiltered.append(ssh_line)
        else:
            node_ssh_lines_manager = ssh_line
    node_ssh_lines = []
    for word_list in [line.split()[:-1] for line in node_ssh_lines_unfiltered]:
        full_line = ''
        for word in word_list:
            full_line += (word + ' ')
        node_ssh_lines.append(full_line.strip())
    full_line = ''
    for word in node_ssh_lines_manager.split()[:-1]:
        full_line += (word + ' ')
    node_ssh_lines_manager = full_line.strip()

    uid = os.getlogin()
    procs_list = []
    for ssh_line in node_ssh_lines:
        addr_only = utils.extract_ssh_addr(ssh_line)
        ssh_cmd = utils.ssh_str.format(uid, addr_only)
        procs_list.append(subprocess.Popen(ssh_cmd.split() + [swarm_leave_cmd]))
    for proc in procs_list:
        proc.wait()
    logger.info('All worker nodes left!')

    subprocess.Popen(node_ssh_lines_manager.split() + [swarm_leave_cmd]).wait()
    logger.info('Manager has left swarm!')
    logger.info('All nodes have left Docker Swarm successfully')
    logger.info('----------------')


# TODO: After running this terminal seems to get funky, don't know why
def label_docker_swarm(node_ssh_list):
    logger.info('----------------')
    logger.info('Labeling all docker swarm nodes...')

    node_ids = utils.parse_node_ls()
    node_ssh_lines_unfiltered = [line.strip() for line in utils.get_file_relative_path(node_ssh_list, '../node-ssh-lists').readlines()]
    node_label_lines = [line.split()[-1] for line in node_ssh_lines_unfiltered]
    if len(node_ids) != len(node_label_lines):
        raise ValueError("node_ids has a length mismatch with node_label_lines")

    for i in range(len(node_label_lines)):
        label_add_cmd = utils.label_add_str.format(node_label_lines[i] + '=true', node_ids[i])
        subprocess.Popen(label_add_cmd.split()).wait()

    logger.info('All Docker Swarm nodes have been labeled successfully')
    logger.info('----------------')


def start_application(manager_addr, application_name, docker_application_name, swarm_yml_name, nodes_pinned):
    uid = os.getlogin()
    ssh_cmd = utils.ssh_str.format(uid, manager_addr)
    application_name_upper = application_name.upper()
    logger.info('----------------')
    logger.info('Starting ' + application_name_upper + ' across Docker Swarm nodes')
    if application_name_upper not in metadata.application_info:
        ValueError('specified application does not exist in metadata.appication_info')
    application_info = metadata.application_info[application_name_upper]

    #cd_cmd = utils.cd_str.format(application_info['node_dir_path'].format(uid))

    #logger.info('Building all the Docker images')
    #build_images_cmd = 'sudo docker compose build'
    #subprocess.Popen(ssh_cmd.split() + [cd_cmd] + ['&&'] + [build_images_cmd]).wait()

    #logger.info('Pushing Docker images to local registry')
    #rebuilt_push_images_cmd = 'bash ~/scripts/rebuilt-push-images.sh'
    #subprocess.Popen(ssh_cmd.split() + [rebuilt_push_images_cmd]).wait()

    #logger.info('Copying Docker Swarm yml to application directory in manager node')
    #cp_dest = application_info['node_dir_path'].format(uid) + '/' + swarm_yml_name
    #cp_src = os.getcwd() + '/../configs/' + swarm_yml_name
    #cp_cmd = utils.cp_str.format(cp_src, cp_dest)
    #subprocess.Popen(cp_cmd.split()).wait()

    logger.info('Deploying Docker Swarm to start application')
    if nodes_pinned:
        # X amount of nodes, swarm master node can be isolated from other services if needed (manual placement)
        # TODO: Will not currently work becaus cd_cmd is undefined
        application_deploy_cmd = utils.application_deploy_str.format(swarm_yml_name, docker_application_name)
        subprocess.Popen(ssh_cmd.split() + [cd_cmd] + ['&&'] + [application_deploy_cmd]).wait()
    else:
        # X amount of nodes, swarm master node can be colocated with other services (automatic placement)
        dsb_path = application_info['dsb_path'].format(uid)
        cd_cmd = utils.cd_str.format(dsb_path)
        application_deploy_cmd = utils.application_deploy_str.format(swarm_yml_name, docker_application_name)

        print('cd_cmd: ' + cd_cmd)
        print('application_deploy_cmd: ' + application_deploy_cmd)

    logger.info(application_name_upper + ' successfully deployed')
    logger.info('----------------')


def run_workload_generator(wrkgen_addr, application_name, numthreads, numconnections, duration, rps, compile_wrk):
    logger.info('----------------')
    logger.info('Running workload generator on designated workload generator node')
    uid = os.getlogin()
    ssh_cmd = utils.ssh_str.format(uid, wrkgen_addr)
    application_name_upper = application_name.upper()
    cd_cmd = utils.cd_str.format('~/wrk2')

    if compile_wrk:
        logger.info('Copying wrk2_points.txt to home directory')
        if application_name_upper not in metadata.application_info:
            ValueError('specified application does not exist in metadata.appication_info')
        application_info = metadata.application_info[application_name_upper]
        cp_cmd = utils.cp_str.format(application_info['wrk2_points_path'], '~/wrk2_points.txt')
        subprocess.Popen(ssh_cmd.split() + [cp_cmd]).wait()

        logger.info('Modifying path to wrk2_points.txt in wrk.c')
        sed_cmd = utils.sed_str.format('REPLACE_ME', uid, application_info['wrk_csrc_path'])
        subprocess.Popen(ssh_cmd.split() + [sed_cmd]).wait()

        logger.info('Building the workload generator')
        subprocess.Popen(ssh_cmd.split() + [cd_cmd] + ['&&'] + ['sudo make']).wait()

        logger.info('Copying workload lua to home directory')
        scp_cmd = utils.scp_str.format(application_info['workload_lua_path'], uid, wrkgen_addr, '~/modified-mixed-workload.lua')
        subprocess.Popen(scp_cmd.split()).wait()

    logger.info('Starting the workload generator')
    wrkgen_res_file = '/users/' + uid + \
                      '/wrkgen_' + application_name_upper + \
                      '_' + numthreads + \
                      '_' + numconnections + \
                      '_' + duration + \
                      '_' + rps
    wrk_cmd = utils.wrk_str.format(numthreads, numconnections, duration, rps, wrkgen_res_file)
    subprocess.Popen(ssh_cmd.split() + [cd_cmd] + ['&&'] + [wrk_cmd]).wait()

    logger.info('Copying results from workload generator node')
    # deleting previous results file w/ same name if it exists
    rm_cmd = utils.rm_f_str.format(wrkgen_res_file)
    if os.path.isfile(wrkgen_res_file):
        subprocess.Popen(rm_cmd.split()).wait()
    scp_cmd = utils.scp_reverse_str.format(uid, wrkgen_addr, wrkgen_res_file, wrkgen_res_file)
    subprocess.Popen(scp_cmd.split()).wait()

    logger.info('wrkgen_res_file: ' + wrkgen_res_file)
    res_file = open(wrkgen_res_file, 'r')
    res_file_lines = res_file.readlines()
    avg_latencies = []
    for i in range(len(res_file_lines)):
        line = res_file_lines[i]
        if 'Test Results' in line:
            latency_results = res_file_lines[i+2]
            avg_latency = latency_results.split()[1]
            avg_latencies.append(avg_latency)
            logger.info('avg_latency: ' + avg_latency)
    res_file.close()

    logger.info('Deleting results files to save space')
    subprocess.Popen(ssh_cmd.split() + [rm_cmd]).wait()
    subprocess.Popen(rm_cmd.split()).wait()

    logger.info('ALL AVG LATENCIES: ' + str(avg_latencies))
    logger.info('Working generator results collected and parsed')
    logger.info('----------------')
    return avg_latencies


def run_latency_sweep(wrkgen_addr, application_name, numthreads, numconnections, duration, start_rps, max_rps, rps_scaling):
    logger.info('----------------')
    logger.info('Performing latency sweep in 1 minute intervals')

    compile_wrk = True
    rps_to_avg_latency = {}
    curr_rps = start_rps
    while curr_rps < max_rps:
        avg_latencies = run_workload_generator(wrkgen_addr, application_name, numthreads, numconnections, duration, str(int(curr_rps)), compile_wrk)
        avg_latencies_sum = 0
        for lat_str in avg_latencies:
            if lat_str[-2:] == 'ms':
                avg_latencies_sum += float(lat_str[:-2])
            elif lat_str[-1:] == 's':
                avg_latencies_sum += float(lat_str[:-1] * 1000)
            elif lat_str[-1:] == 'm':
                avg_latencies_sum += float(lat_str[:-1] * 1000 * 60)
        avg_latency = avg_latencies_sum / len(avg_latencies)
        rps_to_avg_latency[int(curr_rps)] = avg_latency

        curr_rps = curr_rps * rps_scaling
        compile_wrk = False

    logger.info('Listing latency sweep results')
    lines = []
    for key, val in rps_to_avg_latency.items():
        lines.append(str(key) + ' ' + str(val) + '\n')
        logger.info('RPS: ' + str(key) + ', LAT: ' + str(val))

    res_file = application_name + '-' + \
               numthreads + '-' + \
               numconnections + '-' + \
               duration + '-' + \
               str(start_rps) + '-' + \
               str(max_rps) + '-' + \
               str(rps_scaling)
    logger.info('Writing latency sweep results to: hardware-systems-sustainability/results/')
    f = open("../results/" + res_file, "w")
    f.writelines(lines)
    f.close()

    logger.info('Latency sweep complete')
    logger.info('----------------')


def run_workload_generator_profiling(pid):
    logger.info('----------------')
    logger.info('Profiling and get perf results')

    subprocess.Popen(['sudo', 'perf', 'record', '-F', '250', '-e', 'cpu-cycles:ppp,instructions,branches,branch-misses', '--call-graph', 'lbr', '-p', str(pid), 'sleep', '60']).wait()
    subprocess.Popen(['bash', '~/scripts/perf.sh']).wait()
    subprocess.Popen(['sudo', '/dev/shm/perf', 'report', '--call-graph=folded,0.00000001', '--no-children', '-i', 'perf.data']).wait()

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)

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
                        help='replace if .zip already exists in hardware-systems-sustainability/zipped-applications')
    parser.add_argument('--node-ssh-list',
                        dest='node_ssh_list',
                        type=str,
                        help='provide name of file within hardware-systems-sustainability/node-ssh-lists/ containing CloudLab ssh commands')
    # Setting up Docker Swarm
    parser.add_argument('--setup-docker-swarm',
                        dest='setup_docker_swarm',
                        action='store_true',
                        help='specify arg to set up Docker Swarm')
    # Setting up Docker registry
    parser.add_argument('--setup-docker-register',
                        dest='setup_docker_registry',
                        action='store_true',
                        help='specify arg to set up Docker registry')
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
    # Joining docker swarm from other nodes
    parser.add_argument('--join-docker-swarm',
                        dest='join_docker_swarm',
                        action='store_true',
                        help='specify arg to join docker swarm from other nodes')
    parser.add_argument('--manager-addr',
                        dest='manager_addr',
                        type=str,
                        help='provide address of the node that will manage the Docker Swarm')
    # Leaving docker swarm
    parser.add_argument('--leave-docker-swarm',
                        dest='leave_docker_swarm',
                        action='store_true',
                        help='specify arg to leave docker swarm')
    # Applying labels to docker swarm nodes
    parser.add_argument('--label-docker-swarm',
                        dest='label_docker_swarm',
                        action='store_true',
                        help='specify arg to label docker swarm')
    # Starting DeathStarBench applications on CloudLab nodes after setup and swarm initialization
    parser.add_argument('--start-application',
                        dest='start_application',
                        action='store_true',
                        help='specify arg to start specified application')
    parser.add_argument('--nodes-pinned',
                        dest='nodes_pinned',
                        action='store_true',
                        help='specify whether a specific node placement has been made for each microservice')
    parser.add_argument('--docker-application-name',
                        dest='docker_application_name',
                        type=str,
                        help='specify the name of the docker application (may be different than --application-name)')
    parser.add_argument('--swarm-yml-name',
                        dest='swarm_yml_name',
                        type=str,
                        help='provide name of docker-compose-swarm yml file within hardware-systems-sustainability/configs containing swarm node mappings')
    # Running workload generator
    parser.add_argument('--run-workload-generator',
                        dest='run_workload_generator',
                        action='store_true',
                        help='specify arg to run the workload generator on a specified node')
    parser.add_argument('--wrkgen-addr',
                        dest='wrkgen_addr',
                        type=str,
                        help='provide address of the node that will run the workload generator')
    parser.add_argument('--numthreads',
                        dest='numthreads',
                        type=str,
                        help='the total number of threads per URL for the workload generator')
    parser.add_argument('--numconnections',
                        dest='numconnections',
                        type=str,
                        help='the total number of http connections to keep open for the workload generator')
    parser.add_argument('--duration',
                        dest='duration',
                        type=str,
                        help='the duration to run the workload generator')
    parser.add_argument('--rps',
                        dest='rps',
                        type=str,
                        help='requests per second for the workload generator')
    parser.add_argument('--compile-wrk',
                        dest='compile_wrk',
                        action='store_true',
                        help='specify arg to compile wrk2 if it has not already been compiled')
    # Running latency sweep (runs workload generator)
    parser.add_argument('--run-latency-sweep',
                        dest='run_latency_sweep',
                        action='store_true',
                        help='specify arg to run a latency sweep with given parameters')
    parser.add_argument('--start-rps',
                        dest='start_rps',
                        type=int,
                        help='rps at which to start latency sweep')
    parser.add_argument('--max-rps',
                        dest='max_rps',
                        type=int,
                        help='rps at which to end latency sweep')
    parser.add_argument('--rps-scaling',
                        dest='rps_scaling',
                        type=float,
                        help='scale current rps by this factor for each sweep iteration')
    # Profiling workload generator on manager node
    parser.add_argument('--profiling',
                        dest='profiling',
                        action='store_true',
                        help='specify arg to run the workload generator with profiling')
    parser.add_argument('--pid',
                        dest='pid',
                        type=int,
                        help='specify the pid of the workload generator process')

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
        setup_docker_swarm()

    if args.setup_docker_registry:
        if args.published is None:
            raise ValueError('published value should be specified for creating docker registry service')
        if args.target is None:
            raise ValueError('target value should be specified for creating docker registry service')
        if args.registry is None:
            raise ValueError('registry value should be specified for creating docker registry service')
        setup_docker_swarm(args.published, args.target, args.registry)

    if args.join_docker_swarm:
        if args.node_ssh_list is None:
            raise ValueError('must provide file containing CloudLab ssh node info for joining nodes')
        if args.manager_addr is None:
            raise ValueError('must provide ssh address of the swarm manager node')
        join_docker_swarm(args.node_ssh_list, args.manager_addr)

    if args.leave_docker_swarm:
        if args.node_ssh_list is None:
            raise ValueError('must provide file containing CloudLab ssh node info for leaving nodes')
        if args.manager_addr is None:
            raise ValueError('must provide ssh address of the swarm manager node')
        leave_docker_swarm(args.node_ssh_list, args.manager_addr)

    if args.label_docker_swarm:
        if args.node_ssh_list is None:
            raise ValueError('must provide file containing CloudLab ssh node info for labeling nodes')
        label_docker_swarm(args.node_ssh_list)

    if args.start_application:
        if args.manager_addr is None:
            raise ValueError('must provide ssh address of the swarm manager node')
        if args.application_name is None:
            raise ValueError('application name must be provided for starting the application')
        if args.docker_application_name is None:
            raise ValueError('docker application name must be provided for starting the application')
        if args.swarm_yml_name is None:
            raise ValueError('must provide name of Docker Swarm yml within hardware-systems-sustainability/configs')
        start_application(args.manager_addr,
                          args.application_name,
                          args.docker_application_name,
                          args.swarm_yml_name,
                          args.nodes_pinned)

    if args.run_workload_generator:
        if args.wrkgen_addr is None:
            raise ValueError('must provide ssh address of the workload generator node')
        if args.application_name is None:
            raise ValueError('application name must be provided to run the workload generator')
        if args.numthreads is None:
            raise ValueError('numthreads parameter must be provided for the workload generator')
        if args.numconnections is None:
            raise ValueError('numconnections parameter must be provided for the workload generator')
        if args.duration is None:
            raise ValueError('duration parameter must be provided for the workload generator')
        if args.rps is None:
            raise ValueError('rps parameter must be provided for the workload generator')
        if args.compile_wrk is None:
            raise ValueError('must specify whether to compile wrk2 or not')
        run_workload_generator(args.wrkgen_addr,
                               args.application_name,
                               args.numthreads,
                               args.numconnections,
                               args.duration,
                               args.rps,
                               args.compile_wrk)

    if args.run_latency_sweep:
        if args.wrkgen_addr is None:
            raise ValueError('must provide ssh address of the workload generator node')
        if args.application_name is None:
            raise ValueError('application name must be provided to run the workload generator')
        if args.numthreads is None:
            raise ValueError('numthreads parameter must be provided for the workload generator')
        if args.numconnections is None:
            raise ValueError('numconnections parameter must be provided for the workload generator')
        if args.duration is None:
            raise ValueError('duration parameter must be provided for the workload generator')
        run_latency_sweep(args.wrkgen_addr,
                          args.application_name,
                          args.numthreads,
                          args.numconnections,
                          args.duration,
                          args.start_rps,
                          args.max_rps,
                          args.rps_scaling)
    #if args.profiling:
    #    if args.pid is None:
    #        raise ValueError('must provide pid of workload generator process for profiling')
    #    utils.profile_workload_generator(args.manager_addr, args.pid)
