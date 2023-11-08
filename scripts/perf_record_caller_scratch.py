import sys
import os
import argparse
import logging
import subprocess

import utils
import metadata


microservice_name = sys.argv[1]
rebuild_perf = sys.argv[2]
node_addr = sys.argv[3]
uid = os.getlogin()
ssh_cmd = utils.ssh_str.format(uid, node_addr)

subprocess.Popen(ssh_cmd.split() + ['cd ~/scripts && python3 perf_record_scratch.py frontend false']).wait()
