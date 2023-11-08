import sys
import os
import argparse
import logging
import subprocess

import utils
import metadata


microservice_name = sys.argv[1]
rebuild_perf = sys.argv[2]

if rebuild_perf == 'true':
    # Installing various perf dependencies
    install_flex_cmd = 'sudo apt-get update && sudo apt-get install flex'
    subprocess.Popen(install_flex_cmd.split()).wait()
    install_bison_cmd = 'sudo apt-get update && sudo apt-get install bison'
    subprocess.Popen(install_bison_cmd.split()).wait()

    # Rebuild perf
    rebuild_perf_cmd = 'bash ~/scripts/rebuild-perf.sh'
    subprocess.Popen(rebuild_perf_cmd.split()).wait()

# Get process ID running inside Docker container
ps_grep_cmd = utils.ps_grep_str.format(microservice_name)
out = subprocess.check_output(ps_grep_cmd, shell=True)
docker_id = str(out.split()[0])[2:-1]
top_cmd = utils.top_str.format(docker_id)
out = subprocess.check_output(top_cmd.split())
pid = str(out).split()[8]

perf_items = ['cpu-cycles:ppp,instructions,branches,branch-misses']

# Run perf
for perf_item in perf_items:
    perf_cmd = utils.perf_str.format(perf_item, pid)
    subprocess.Popen(perf_cmd.split()).wait()
