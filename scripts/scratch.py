import sys
import os
import argparse
import logging
import subprocess

import utils
import metadata

import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd

#plotting = False
plotting = True
#profiling = True

if plotting:
    #filename = '../results/hotelreservation_grpc-50-50-20s-100-200-1.2'
    filename = '../results/hotelreservation_grpc-50-50-2m-100-3000-1.1'
    file = open(filename, 'r')
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
    plt.savefig(filename + '.png', dpi='figure', format=None)

#if profiling:
