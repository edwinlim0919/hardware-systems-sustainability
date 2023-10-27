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
First, you will need to make an .txt file in grpc-hotel-ipu/node-ssh-lists such as c6320_24.txt, which contains the ssh command for each node in your CloudLab experiment, as well as node label such as node<x>. You should just order these in increasing number for simplicity, and they correspond to placement constraints in the docker-compose-swarm.yml files within grpc-hotel-ipu/configs. Here is an example for a 24 node cluster (you will need to use your own cloudlab uid instead of edwinlim):
```
ssh edwinlim@clnode146.clemson.cloudlab.us node0
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

Then, you can run scripts to zip the application, copy it to all the nodes, and run some setup scripts on the nodes to install dependencies. You can use a command like this, providing both the name of the application and the node ssh info from above (currently only the modified gRPC HotelReservation application is supported by the scripts). Run all these commands from grpc-hotel-ipu/scripts.
```bash
python3 main.py --setup-application --application-name hotelreservation_grpc --node-ssh-list c6320_24.txt
```

## Setting up a Docker Swarm
Use this command to set up a docker swarm on the node that will be your manager node. You should do this on node0.
```bash
python3 main.py --setup-docker-swarm --published 7696 --target 5000 --registry 2
```

## Joining the other nodes to the Docker Swarm
Then, join the other nodes to the Docker Swarm as worker nodes by running the following command from the manager node. You will need to provide the node ssh info file, as well as the address of the manager node (without the "<uid>@" portion of the ssh command).
```bash
python3 main.py --join-docker-swarm --node-ssh-list c6320_24.txt --manager-addr clnode146.clemson.cloudlab.us
```

## Labeling the nodes in the Docker Swarm
Once the other nodes are joined to the swarm, assign them the node<x> labels from the ssh node info with the following command. You will need to provide the ssh info file to the script.
```bash
python3 main.py --label-docker-swarm --node-ssh-list c6320_24.txt
```

## Starting the application
Once all nodes have joined the swarm and have been labeled, you can now start the application. You will need a docker-compose-swarm.yml file in grpc-hotel-ipu/configs that contains information about each microservice and their node mappings. The example hotelreservation_grpc_c6320_24_docker-compose-swarm.yml maps each microservice onto its own node. In this example, node2-node23 host microservices. Node0 only runs the swarm manager, and node1 runs the workload generator. You can start the application with the following command, providing all the information. The --application-name argument is different from the --docker-application-name argument, but that's because the --aplication-name only holds random metadata needed for the Python scripting. The --docker-application-name argument is the name of the actual application within Docker.
```bash
python3 main.py --start-application --manager-addr clnode146.clemson.cloudlab.us --application-name hotelreservation_grpc --docker-application-name hotelReservation --swarm-yml-name hotelreservation_grpc_c6320_24_docker-compose-swarm.yml
```
Give the application a few minutes to start up, and you can periodically check the status with the following command. When the application is up and running, you should see a '1/1' for all the microservices under the 'Replicated' section.
```bash
sudo docker service ls
```
Once the application has fully started up, check if is function by issuing a request with the following command.
```bash
curl -X GET "http://10.10.1.1:5000/hotels?inDate=2015-04-13&outDate=2015-04-15&lat=64.83538&lon=-147.8233"
```

## Taking down the Docker Swarm
Once you are done with using the application, you can take down the Docker Swarm with the following command.
```bash
python3 main.py --leave-docker-swarm --node-ssh-list c6320_24.txt --manager-addr clnode146.clemson.cloudlab.us
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
