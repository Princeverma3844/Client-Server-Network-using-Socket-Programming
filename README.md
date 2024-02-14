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
- You need to close any peer to check for the dead message send by the other peers to the seed node

## Proof of correctness
- **gossips:** All the nodes starts to communicate gossips the with their peers as soon as they get connected which can be seen from the output file.
- **broadcast:** This can be verified from some of the outputs that the sender peer id is different from the id of the peer from which the message is initiated.
- **dead:** This can be verified once you close any peer after some time in the output file of the seed output.
- **liveliness:** The receival of dead message from the peer to the seed itself proves the liveliness messages of the peers. 

### Key Concepts
- **Threading:** Used to enable peers to act as both servers and clients simultaneously.
- **Locks:** Employed to ensure thread-safe access to shared resources.

## Probable attacks
- **Sybil Attack:** In a Sybil attack, a malicious peer creates multiple fake identities (Sybil nodes) to gain a disproportionately large influence within the network. These fake identities could be used to disrupt the network's operation, manipulate messages, or control the flow of information.
- **Eclipse Attack:** In an eclipse attack, an attacker isolates a target node by surrounding it with malicious peers controlled by the attacker. This isolation prevents the target node from receiving accurate information, leading to potential disruptions or malicious actions.
- **Denial of Service (DoS) Attack:** Malicious peers could launch DoS attacks by overwhelming targeted nodes with a high volume of requests or messages, thereby disrupting their normal operations and potentially causing them to appear as if they are unresponsive.

## Solution to these attacks
- **Peer Reputation Systems:** Implementing reputation systems where peers assess each other's behavior and assign reputations could help identify and isolate malicious peers.
- **Sybil Resistance:** Introduce mechanisms to limit the influence of Sybil nodes, such as requiring proof of computational work or social network verification.
- **Firewall and Filtering:** Deploy firewalls and message filtering mechanisms to detect and block malicious traffic, thereby mitigating DoS attacks and preventing the spread of malicious messages.

## Outputs
Each node generates a separate output file in the same directory as the peer and seed nodes.
