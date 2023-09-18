#!/usr/bin/env bash

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-Linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

wget https://bootstrap.pypa.io/get-pip.py
python3 ./get-pip.py
setenv PATH "{$PATH}:/users/`whoami`/.local/bin"
pip3 install asyncio aiohttp

sudo apt-get install libssl-dev -y
sudo apt-get install libz-dev -y
sudo apt-get install luarocks -y
sudo luarocks install luasocket
sudo apt install linux-tools-`uname -r` linux-tools-generic htop -y
sudo apt install libelf-dev libdw-dev systemtap-sdt-dev libunwind-dev libslang2-dev libnuma-dev libiberty-dev -y

wget https://gist.githubusercontent.com/sriramdvt/6c5a4e10489d2c7cade906b9de25bcf9/raw/688a69681053ff193a2fe9379d51d64b85eb834c/run-perf.sh -P /dev/shm
wget https://gist.githubusercontent.com/sriramdvt/27b046b512f72ea22f339e717948a86f/raw/c88678bc15c6b36d1d424fe668d26c4a9353c1da/rebuild_perf.sh -P ~
wget https://gist.githubusercontent.com/sriramdvt/d591e81bffbfd983ff01a49fe0c55c73/raw/a121b7d6bb1f6011e2d5a7be5ec4c639b911dfb2/docker_setup_labels.sh -P ~
wget https://gist.githubusercontent.com/sriramdvt/e269792e5ee437c368dbad7d194c69cd/raw/b0caa21022c8320135dd70c66650ce223b0a8042/docker-compose-swarm.yml -P ~
wget https://gist.githubusercontent.com/sriramdvt/0d81a43bc4da351615e0ea7a4fef95fc/raw/279b8593f6cd558ba4d54187970319fbf22c3de7/taskset.sh -P ~
wget https://gist.githubusercontent.com/sriramdvt/a4665af6a019f97e88e67a7eb71866a9/raw/b573b329a78d561feb16901fd343187fe1495c11/services.sh -P ~
wget https://gist.githubusercontent.com/sriramdvt/5500d3efcbc77c79247071f65c271198/raw/bb986e0f95b31162651a2e2abf6f571e75939656/rebuilt_push_images.sh -P ~

git clone https://github.com/delimitrou/DeathStarBench.git
