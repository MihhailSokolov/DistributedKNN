# DistributedKNN
Master-Slave distributed system that works together to speed up the kNN classification. 

## Description
k-Nearest-Neighbors classification is very powerful yet very simple machine learning algorithm used for classification. One of the biggest downsides of this algorithm is that it can very slow on big dataset.
This application solves that problem by distributing dataset and workload between multiple machines.

## Algorithm
- Dataset is uploaded on the Master node
- All Slaves connect to Master
- Master distributes the dataset to each Slave node evenly
- Master send a new data point for classification to all Slaves
- Each Slave returns `k/n` _(rounded up)_ nearest points to the new data point and their classes where `k` is the number of nearest neighbors required for classification and `n` is the number of Slaves
- Master now has at least `k` nearest points and can do majority voting to choose a class for the new data point. If Master receives more than `k` points, it must iterate through these points leaving only `k` nearest of them to the new data point.
- Classification is done. Slaves can disconnect.

# Running
## Master
Master node can be run by executing class `src/master_node.py`.
It supports the following CLI arguments:
- `--host` - set Master node host name
- `--port` - set Master node port number
- `-k` - set number for `k` in _kNN_
- `-n`, `--num-slaves` - set number of expected Slave nodes

## Slave
Slave node can be run by executing class `src/slave_node.py`.
It supports the following CLI arguments:
- `--master-host`, `-mh` - set Master node host name
- `--master-port`, `-mp` - set Master node port number