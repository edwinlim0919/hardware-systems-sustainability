import sys
import os
import argparse
import logging
import subprocess

import utils
import metadata

import matplotlib.pyplot as plt
import numpy as np


microservice_name = sys.argv[1]
node_addr = sys.argv[2]
rebuild_perf = sys.argv[3]
uid = os.getlogin()
ssh_cmd = utils.ssh_str.format(uid, node_addr)

if rebuild_perf == 'true':
    # Installing various perf dependencies
    install_flex_cmd = 'sudo apt-get update && sudo apt-get install flex'
    #subprocess.Popen(ssh_cmd.split() + [install_flex_cmd]).wait()
    subprocess.Popen(install_flex_cmd.split()).wait()
    install_bison_cmd = 'sudo apt-get update && sudo apt-get install bison'
    #subprocess.Popen(ssh_cmd.split() + [install_bison_cmd]).wait()
    subprocess.Popen(install_bison_cmd.split()).wait()
 
    # Rebuild perf
    rebuild_perf_cmd = 'bash ~/scripts/rebuild-perf.sh'
    #subprocess.Popen(ssh_cmd.split() + [rebuild_perf_cmd]).wait()
    subprocess.Popen(rebuild_perf_cmd.split()).wait()

# Get process ID running inside Docker container
ps_grep_cmd = utils.ps_grep_str.format(microservice_name)
#out = subprocess.check_output(ssh_cmd.split() + [ps_grep_cmd])
out = subprocess.check_output(ps_grep_cmd.split())
docker_id = str(out.split()[0])[2:-1]
top_cmd = utils.top_str.format(docker_id)
#out = subprocess.check_output(ssh_cmd.split() + [top_cmd])
out = subprocess.check_output(top_cmd.split())
pid = str(out).split()[8]

perf_items = ['cpu-cycles:ppp,instructions,branches,branch-misses']

# Run perf
for perf_item in perf_items:
    perf_cmd = utils.perf_str.format(perf_item, pid)
    print(perf_cmd)
#    subprocess.Popen(ssh_cmd.split() + [perf_cmd]).wait()
