# P2P-Network

## Objective:
The objective of this project is to implement a Gossip protocol over a peer-to-peer network to broadcast messages and ensure the liveness of connected peers. This README provides an overview of the network setup, protocol specifications, program output, and additional considerations regarding security.

# Network Setup:
The network consists of two types of nodes:

Seed Nodes: Seed nodes act as entry points to the peer-to-peer network. They maintain a list of connected peers and facilitate the bootstrapping process for new nodes.
Peer Nodes: Peer nodes connect to seed nodes, receive information about other peers, and establish connections with a subset of them. Peer nodes broadcast messages and check the liveness of connected peers.

# Input Format:
The Host and Port of all the seed nodes will be hard coded in the config file. Also once you run the peer.py you will be asked to provide the host and port of the peer in the 
