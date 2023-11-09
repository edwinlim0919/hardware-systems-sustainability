import sys
import os
import re
import argparse
import logging
import subprocess

import utils
import metadata
import time

microservice_name = sys.argv[1]
rebuild_perf = sys.argv[2]
uid = os.getlogin()

if rebuild_perf == 'true':
    # Installing various perf dependencies
    update_flex_cmd = 'sudo apt-get update'
    subprocess.Popen(update_flex_cmd.split()).wait()
    install_flex_cmd = 'sudo apt-get install flex'
    subprocess.Popen(install_flex_cmd.split()).wait()
    update_bison_cmd = 'sudo apt-get update'
    subprocess.Popen(update_bison_cmd.split()).wait()
    install_bison_cmd = 'sudo apt-get install bison'
    subprocess.Popen(install_bison_cmd.split()).wait()

    # Rebuild perf
    rebuild_perf_cmd = 'bash /users/' + uid + '/scripts/rebuild-perf.sh'
    subprocess.Popen(rebuild_perf_cmd.split()).wait()

perfdata_path = '/users/' + uid + '/perfdata'
if not os.path.exists(perfdata_path):
    mkdir_cmd = 'mkdir ' + perfdata_path
    subprocess.Popen(mkdir_cmd.split()).wait()

# Get process ID running inside Docker container
ps_grep_cmd = utils.ps_grep_str.format(microservice_name)
out = subprocess.check_output(ps_grep_cmd, shell=True)
docker_id = str(out.split()[0])[2:-1]
top_cmd = utils.top_str.format(docker_id)
out = subprocess.check_output(top_cmd.split())
pid = str(out).split()[8]

perf_items = ['cpu-cycles:ppp,instructions,branches,branch-misses',
              'cpu-cycles:ppp,instructions,L1-dcache-loads,L1-dcache-load-misses',
              'cpu-cycles:ppp,instructions,L2-stores,L2-store-misses',
              'cpu-cycles:ppp,instructions,LLC-loads,LLC-load-misses',
              'cpu-cycles:ppp,instructions,LLC-stores,LLC-store-misses',
              'cpu-cycles:ppp,instructions,dTLB-loads,dTLB-load-misses',
              'cpu-cycles:ppp,instructions,dTLB-stores,dTLB-store-misses',
              'cpu-cycles:ppp,instructions,iTLB-loads,iTLB-load-misses',
              'cpu-cycles:ppp,instructions,L1-icache-load-misses,L1-dcache-stores',
              'cpu-cycles:ppp,instructions,L2-loads,L2-load-misses']

# Run perf
for perf_item in perf_items:
    perf_cmd = utils.perf_str.format(perf_item, pid)
    subprocess.Popen(perf_cmd.split()).wait()

    # Only last two perf records are unique across perf runs
    # cycles and instructions are profiled for every run
    perf_item_split = perf_item.split(',')
    perfdata_file = perf_item_split[2] + '_' + perf_item_split[3] + '_perf.data'
    cp_cmd = utils.cp_str.format('/users/' + uid + '/scripts/perf.data', '/users/' + uid + '/perfdata/' + perfdata_file)
    subprocess.Popen(cp_cmd.split()).wait()

home_path = '/users/' + uid + '/'
scripts_path = '/users/' + uid + '/scripts/'
perfdata_path = '/users/' +  uid + '/perfdata/'

# Get individual event records, save in home directory
for perf_item in perf_items:
    for filename in os.listdir(scripts_path):
        if 'perf.hist.' in filename:
            print('deleting ' + scripts_path + filename)
            os.remove(os.path.join(scripts_path, filename))

    perf_item_split = perf_item.split(',')
    perfdata_file = perf_item_split[2] + '_' + perf_item_split[3] + '_perf.data'
    perfdata_filepath = '/users/' + uid + '/perfdata/' + perfdata_file
    autoperf_cmd = 'bash /users/' + uid + '/scripts/autoperf.sh ' + perfdata_filepath
    subprocess.Popen(autoperf_cmd.split()).wait()

    cp_cmd = utils.cp_str.format(scripts_path + 'perf.hist.0', perfdata_path + perf_item_split[2] + '_' + perf_item_split[3] + '_perf.hist.0')
    subprocess.Popen(cp_cmd.split()).wait()
    cp_cmd = utils.cp_str.format(scripts_path + 'perf.hist.1', perfdata_path + perf_item_split[2] + '_' + perf_item_split[3] + '_perf.hist.1')
    subprocess.Popen(cp_cmd.split()).wait()
    cp_cmd = utils.cp_str.format(scripts_path + 'perf.hist.2', perfdata_path + perf_item_split[2] + '_' + perf_item_split[3] + '_perf.hist.2')
    subprocess.Popen(cp_cmd.split()).wait()
    cp_cmd = utils.cp_str.format(scripts_path + 'perf.hist.3', perfdata_path + perf_item_split[2] + '_' + perf_item_split[3] + '_perf.hist.3')
    subprocess.Popen(cp_cmd.split()).wait()
