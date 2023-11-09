import sys
import os
import argparse
import logging
import subprocess

import utils
import metadata

import matplotlib.pyplot as plt
import numpy as np


filename1 = sys.argv[1]
filename2 = sys.argv[2]

filename1_path = '../results/' + filename1
filename2_path = '../results/' + filename2
file1 = open(filename1_path, 'r')
lines1 = file1.readlines()
file2 = open(filename2_path, 'r')
lines2 = file2.readlines()

rps_list1 = []
lat_list1 = []
rps_list2 = []
lat_list2 = []

for line in lines1:
    newline_removed = line[:-1]
    line_split = newline_removed.split()
    rps_list1.append(int(line_split[0]))
    lat_list1.append(float(line_split[1]))
for line in lines2:
    newline_removed = line[:-1]
    line_split = newline_removed.split()
    rps_list2.append(int(line_split[0]))
    lat_list2.append(float(line_split[1]))

plt.plot(rps_list1, lat_list1, color='red', label='c6320')
plt.plot(rps_list2, lat_list2, color='blue', label='c6420')
plt.legend()
plt.xlabel("Requests Per Second")
plt.ylabel("Mean Latency (ms)")
plt.savefig('../results/bothsweeps' + '.png', dpi='figure', format=None)
