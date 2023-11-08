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
uid = os.getlogin()
ssh_cmd = utils.ssh_str.format(uid, node_addr)

# Rebuild perf

ps_grep_cmd = utils.ps_grep_str.format(microservice_name)
out = subprocess.check_output(ssh_cmd.split() + [ps_grep_cmd])
docker_id = str(out.split()[0])[2:-1]


