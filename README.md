# gRPC HotelReservation + Intel IPU Scripting

Usable scripting for running DeathStarBench's HotelReservation application in tandem with Intel's IPU emulator on CloudLab.

## CloudLab Setup

First, ssh into your CloudLab master node with the -A option to cache public keys in your ssh-agent. An example is shown below, but you will need your own CloudLab account and experiment cluster.
```bash
ssh -A edwinlim@ms0415.utah.cloudlab.us
```

Then, go to the /dev/shm directory and clone the repository.
```bash
cd /dev/shm
git clone git@github.com:edwinlim0919/grpc-hotel-ipu.git 
```

After cloning, head into the /grpc-hotel-ipu directory and initialize the datacenter-soc submodule.
```bash
cd grpc-hotel-ipu/
git submodule init datacenter-soc/
git submodule update --init

```

Next, still within the /grpc-hotel-ipu directory, set up some bash environment stuff.
Press "y" and enter whenever prompted.
You may need to log out of the node and log back in to see env changes take affect.
```bash
source ./env.sh
```

Next, install the dependencies needed to run DeathStarBench.
Press "y" and enter whenever prompted.
You may need to log out of the node and log back in to see env changes take effect.
```bash
source ./setup.sh
```

## Setting up an application across CloudLab nodes
First, you will need to make an .txt file in grpc-hotel-ipu/node-ssh-lists such as c6420_24.txt, which contains the ssh command for each node in your CloudLab experiment, as well as node label such as node<x>. You should just order these in increasing number for simplicity, and they will correspond to placement constraints in the docker-compose-swarm.yml file. Here is an example for a 24 node cluster:
```
ssh edwinlim@clnode109.clemson.cloudlab.us node0
ssh edwinlim@clnode123.clemson.cloudlab.us node1
ssh edwinlim@clnode100.clemson.cloudlab.us node2
ssh edwinlim@clnode098.clemson.cloudlab.us node3
ssh edwinlim@clnode165.clemson.cloudlab.us node4
ssh edwinlim@clnode105.clemson.cloudlab.us node5
ssh edwinlim@clnode128.clemson.cloudlab.us node6
ssh edwinlim@clnode114.clemson.cloudlab.us node7
ssh edwinlim@clnode107.clemson.cloudlab.us node8
ssh edwinlim@clnode131.clemson.cloudlab.us node9
ssh edwinlim@clnode152.clemson.cloudlab.us node10
ssh edwinlim@clnode166.clemson.cloudlab.us node11
ssh edwinlim@clnode119.clemson.cloudlab.us node12
ssh edwinlim@clnode132.clemson.cloudlab.us node13
ssh edwinlim@clnode112.clemson.cloudlab.us node14
ssh edwinlim@clnode146.clemson.cloudlab.us node15
ssh edwinlim@clnode115.clemson.cloudlab.us node16
ssh edwinlim@clnode129.clemson.cloudlab.us node17
ssh edwinlim@clnode104.clemson.cloudlab.us node18
ssh edwinlim@clnode124.clemson.cloudlab.us node19
ssh edwinlim@clnode108.clemson.cloudlab.us node20
ssh edwinlim@clnode140.clemson.cloudlab.us node21
ssh edwinlim@clnode168.clemson.cloudlab.us node22
ssh edwinlim@clnode110.clemson.cloudlab.us node23
```
```bash
python3 main.py --setup-application --application-name hotelreservation_grpc --node-ssh-list <provide .txt file from node-ssh-lists>
```

## Setting up a Docker Swarm
```bash
cd scripts/
python3 main.py --setup-docker-swarm --published 7696 --target 5000 --registry 2
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
