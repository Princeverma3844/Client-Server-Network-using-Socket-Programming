# P2P-Network

## Objective
The objective of this project is to implement a Gossip protocol over a peer-to-peer network to broadcast messages and ensure the liveness of connected peers. This README provides an overview of the network setup, protocol specifications, program output, and additional considerations regarding security.

## Network Setup
The network consists of two types of nodes:

- **Seed Nodes:** Seed nodes act as entry points to the peer-to-peer network. They maintain a list of connected peers and facilitate the bootstrapping process for new nodes.
- **Peer Nodes:** Peer nodes connect to seed nodes, receive information about other peers, and establish connections with a subset of them. Peer nodes broadcast messages and check the liveness of connected peers.

## Input Format
The Host and Port of all the seed nodes will be hardcoded in the config file. When running the `peer.py` script, you will be prompted to provide the host and port of the peer in the corresponding terminal. The host must be localhost (127.0.0.1), and the port must be unique for each peer instance.

## How To Run
1. Start by running the `seed.py` file to activate all seed nodes.
2. Create multiple instances of the peer node using the command prompt. Provide a unique host and port for each peer instance.

## Functionality
- Seed nodes listen for incoming connections from peers.
- Peers, once connected to a seed, retrieve the list of other peers and establish connections with them.
- Peers exchange two types of messages: Gossip messages and liveness messages. Each peer sends 10 gossip messages to its neighbors, forwarding new messages only. Liveness messages are sent periodically to check peer status.
- If a peer fails to receive a response to three consecutive liveness messages from a neighbor, it reports the unresponsive peer to connected seed nodes for removal from the peer list.

### Key Concepts
- **Threading:** Used to enable peers to act as both servers and clients simultaneously.
- **Locks:** Employed to ensure thread-safe access to shared resources.

## Outputs
Each node generates a separate output file in the same directory as the peer and seed nodes.

This README provides clear instructions and explanations of the project's components and functionalities, enhancing readability and professionalism.
