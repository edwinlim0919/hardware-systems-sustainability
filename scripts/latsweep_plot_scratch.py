import sys
import os
import argparse
import logging
import subprocess

import utils
import metadata

import matplotlib.pyplot as plt
import numpy as np


filename = sys.argv[1]

#filename_path = '../results/hotelreservation_grpc-50-50-2m-100-3000-1.1'
filename_path = '../results/' + filename
file = open(filename_path, 'r')
lines = file.readlines()

rps_list = []
lat_list = []
for line in lines:
    newline_removed = line[:-1]
    line_split = newline_removed.split()
    rps_list.append(int(line_split[0]))
    lat_list.append(float(line_split[1]))

plt.plot(rps_list, lat_list)
plt.xlabel("Requests Per Second")
plt.ylabel("Mean Latency (ms)")
plt.savefig(filename_path + '.png', dpi='figure', format=None)
