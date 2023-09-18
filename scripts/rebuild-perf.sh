kname=$(uname -r | cut -d'-' -f 1)
echo "${kname}"
wget https://mirrors.edge.kernel.org/pub/linux/kernel/tools/perf/v${kname}/perf-${kname}.tar.gz
gunzip perf-${kname}.tar.gz
tar xf perf-${kname}.tar

cd perf-${kname}

echo "Replacing %2f with %8f"...
# important thing is to change in perf/util/callchain.c in callchain_counts_value
find . -type f -exec sed -i 's/.2f%/.8f%/g' {} \;

make -C tools/perf install

cp tools/perf/perf /dev/shm
