import os
import csv
import pandas as pd
import matplotlib.pyplot as plt

result_dir = "../results"
plots_dir = "../plots"

categories = ["Architecture Event", "Memory", "Kernal", "Hashing", "Synchronization", "Compression", "C Libraries", 
              "Golang Kernel/Synchronization", "Golang Memory Management", "GoLang Garbage Collection", 
              "Application Logic", "Miscellaneous", "Total Unallocated Overhead"]

# Extracts the contents of a performance raw txt file
# based on the categories listed
def extract_file_contents(file, df):
    memory = 0
    kernal = 0
    hashing = 0
    synchronization = 0
    compression = 0
    c_libraries = 0
    golang_kernel = 0
    golang_memory = 0
    golang_garbage = 0
    application_logic = 0
    miscellaneous = 0
    total_unallocated = 0

    architecturalEvent = file.split("_")[0]
    result_filename = os.path.join(result_dir, file)
    with open(result_filename, 'r+') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("Memory"):
                memory = float(line.split(" ")[1].strip('%\n'))
            if line.startswith("Kernel"):
                kernal = float(line.split(" ")[1].strip('%\n'))
            if line.startswith("Hashing"):
                hashing = float(line.split(" ")[1].strip('%\n'))
            if line.startswith("Synchronization"):
                synchronization = float(line.split(" ")[1].strip('%\n'))
            if line.startswith("Compression"):
                compression = float(line.split(" ")[1].strip('%\n'))
            if line.startswith("C Libraries"):
                c_libraries = float(line.split(" ")[2].strip('%\n'))
            if line.startswith("Golang Kernel/Synchronization"):
                golang_kernel = float(line.split(" ")[2].strip('%\n'))
            if line.startswith("Golang Memory Management"):
                golang_memory = float(line.split(" ")[3].strip('%\n'))
            if line.startswith("Golang Garbage Collection"):
                golang_garbage = float(line.split(" ")[3].strip('%\n'))
            if line.startswith("Application Logic"):
                application_logic = float(line.split(" ")[2].strip('%\n'))
            if line.startswith("Miscellaneous"):
                miscellaneous = float(line.split(" ")[1].strip('%\n'))
            if line.startswith("Total Unallocated Overhead"):
                total_unallocated = float(line.split(" ")[3].strip('%\n'))
    # add the row to the dataframe
    df = pd.concat([df, pd.DataFrame([[architecturalEvent, memory, kernal, hashing, synchronization, compression, c_libraries, 
                     golang_kernel, golang_memory, golang_garbage, application_logic, miscellaneous, total_unallocated]], columns=categories)])
    return df
            
df = pd.DataFrame(columns=categories)
for file in os.listdir(result_dir):
    if file.endswith(".txt"):
        df = extract_file_contents(file, df)
df.sort_values(by=['Architecture Event'], inplace=True)

# Plot all stats
ax = df.plot.barh(x="Architecture Event", y=["Memory", "Kernal", "Hashing", "Synchronization", "Compression", "C Libraries", "Golang Kernel/Synchronization", "Golang Memory Management", "GoLang Garbage Collection", "Application Logic", "Miscellaneous", "Total Unallocated Overhead"], stacked=True, figsize=(16, 7))
for c in ax.containers:
    labels = [round(v.get_width() ,1) if v.get_width() > 0 else '' for v in c]
    ax.bar_label(c, labels=labels, fmt='%d', label_type='center')
plt.title("Hotel Reservation events bucketed by category")
plt.ylabel("Architectural Event")
plt.xlabel("Percentage of the event samples (%)")
plt.legend(loc="upper center", bbox_to_anchor=(0.5, +1.15), ncol=6)
figname = plots_dir + "/all_stats.png"
plt.savefig(figname, bbox_inches='tight')

plt.clf()

# Plot L1 stats
L1_df = df[df["Architecture Event"].str.contains("L1")]
ax = L1_df.plot.barh(x="Architecture Event", y=["Memory", "Kernal", "Hashing", "Synchronization", "Compression", "C Libraries", "Golang Kernel/Synchronization", "Golang Memory Management", "GoLang Garbage Collection", "Application Logic", "Miscellaneous", "Total Unallocated Overhead"], stacked=True, figsize=(16, 7))
for c in ax.containers:
    labels = [round(v.get_width() ,1) if v.get_width() > 0 else '' for v in c]
    ax.bar_label(c, labels=labels, fmt='%d', label_type='center')
plt.title("Hotel Reservation events bucketed by category (L1)")
plt.ylabel("Architectural Event")
plt.xlabel("Percentage of the event samples (%)")
plt.legend(loc="upper center", bbox_to_anchor=(0.5, +1.15), ncol=6)
figname = plots_dir + "/L1_stats.png"
plt.savefig(figname, bbox_inches='tight')
plt.clf()

# Plot L2 stats
L2_df = df[df["Architecture Event"].str.contains("L2")]
ax = L2_df.plot.barh(x="Architecture Event", y=["Memory", "Kernal", "Hashing", "Synchronization", "Compression", "C Libraries", "Golang Kernel/Synchronization", "Golang Memory Management", "GoLang Garbage Collection", "Application Logic", "Miscellaneous", "Total Unallocated Overhead"], stacked=True, figsize=(16, 7))
for c in ax.containers:
    labels = [round(v.get_width() ,1) if v.get_width() > 0 else '' for v in c]
    ax.bar_label(c, labels=labels, fmt='%d', label_type='center')
plt.title("Hotel Reservation events bucketed by category (L2)")
plt.ylabel("Architectural Event")
plt.xlabel("Percentage of the event samples (%)")
plt.legend(loc="upper center", bbox_to_anchor=(0.5, +1.15), ncol=6)
figname = plots_dir + "/L2_stats.png"
plt.savefig(figname, bbox_inches='tight')
plt.clf()

# Plot LLC stats
LLC_df = df[df["Architecture Event"].str.contains("LLC")]
ax = LLC_df.plot.barh(x="Architecture Event", y=["Memory", "Kernal", "Hashing", "Synchronization", "Compression", "C Libraries", "Golang Kernel/Synchronization", "Golang Memory Management", "GoLang Garbage Collection", "Application Logic", "Miscellaneous", "Total Unallocated Overhead"], stacked=True, figsize=(16, 7))
for c in ax.containers:
    labels = [round(v.get_width() ,1) if v.get_width() > 0 else '' for v in c]
    ax.bar_label(c, labels=labels, fmt='%d', label_type='center')
plt.title("Hotel Reservation events bucketed by category (LLC)")
plt.ylabel("Architectural Event")
plt.xlabel("Percentage of the event samples (%)")
plt.legend(loc="upper center", bbox_to_anchor=(0.5, +1.15), ncol=6)
figname = plots_dir + "/LLC_stats.png"
plt.savefig(figname, bbox_inches='tight')
plt.clf()

# Plot TLB stats
TLB_df = df[df["Architecture Event"].str.contains("TLB")]
ax = TLB_df.plot.barh(x="Architecture Event", y=["Memory", "Kernal", "Hashing", "Synchronization", "Compression", "C Libraries", "Golang Kernel/Synchronization", "Golang Memory Management", "GoLang Garbage Collection", "Application Logic", "Miscellaneous", "Total Unallocated Overhead"], stacked=True, figsize=(16, 7))
for c in ax.containers:
    labels = [round(v.get_width() ,1) if v.get_width() > 0 else '' for v in c]
    ax.bar_label(c, labels=labels, fmt='%d', label_type='center')
plt.title("Hotel Reservation events bucketed by category (TLB)")
plt.ylabel("Architectural Event")
plt.xlabel("Percentage of the event samples (%)")
plt.legend(loc="upper center", bbox_to_anchor=(0.5, +1.15), ncol=6)
figname = plots_dir + "/TLB_stats.png"
plt.savefig(figname, bbox_inches='tight')
plt.clf()

# Plot cycle, instruction, branch stats
CIB_df = df[df["Architecture Event"].str.contains("cycle|instruction|branch")]
ax = CIB_df.plot.barh(x="Architecture Event", y=["Memory", "Kernal", "Hashing", "Synchronization", "Compression", "C Libraries", "Golang Kernel/Synchronization", "Golang Memory Management", "GoLang Garbage Collection", "Application Logic", "Miscellaneous", "Total Unallocated Overhead"], stacked=True, figsize=(16, 7))
for c in ax.containers:
    labels = [round(v.get_width() ,1) if v.get_width() > 0 else '' for v in c]
    ax.bar_label(c, labels=labels, fmt='%d', label_type='center')
plt.title("Hotel Reservation events bucketed by category (CIB)")
plt.ylabel("Architectural Event")
plt.xlabel("Percentage of the event samples (%)")
plt.legend(loc="upper center", bbox_to_anchor=(0.5, +1.15), ncol=6)
figname = plots_dir + "/CIB_stats.png"
plt.savefig(figname, bbox_inches='tight')
plt.clf()
