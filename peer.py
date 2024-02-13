import socket
import json 
import threading
import random
import pickle
import time 
from datetime import datetime
import threading
import os

def main():
    
    # Read data from the JSON config file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = "config.json"
    file_path = os.path.join(current_dir, filename)
    with open(file_path) as f:
        config_data = json.load(f)

    # randomly choose the n//2+1 seed nodes from the config file
    N = config_data["N"]
    seed_list = config_data["Seed_info"]
    num_seed_conn = N//2 + 1
    random_indices = random.sample(range(len(seed_list)), num_seed_conn) # select random seed nodes

    # class for the Peer node
    class Peer():
        # initialisation of the Peer node paramaters
        def __init__(self, Peer_host, Peer_port):
            self.Peer_host = Peer_host
            self.Peer_port = Peer_port
            self.id = (Peer_host, Peer_port)
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peer_socket.bind(self.id)
            self.peer_socket.listen()
            self.peer_neighbour = set()
            self.peer_seed = []
            self.ML = {}
            self.neigh_socket_lst = []
            self.msg = 1
            self.no_response_ct = {}
            self.socket_to_id = {}
            self.lock = threading.Lock()
            self.lock_output = threading.Lock()   

        # For printing the output to the console as well as to the output file
        def outout_write(self, msg):
            # lock aquired so that same resource could not be used by multiple users
            self.lock_output.acquire()
            print(msg)
            out_filename = f"output{self.id}.txt"
            out_path = os.path.join(current_dir, out_filename)
            with open(out_path, "a") as file:
                # Write content to the file
                file.write(msg + "\n")
            self.lock_output.release()

        # Mainting the output format
        def out_handle(self, timestamp, id, msg):
            out = f"< {timestamp} > < {id} > < {msg} >"
            self.outout_write(out)

        # Making our connection with the choosen seed nodes
        def connect_to_seed(self, Host, Port):
            try:
                # Making the socket to connect with the seed
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect((Host,Port))
                self.peer_seed.append(peer_socket)
                id = pickle.dumps(self.id)          # sending our ID to the host for registration
                peer_socket.sendall(id)
                list = peer_socket.recv(1024)       # The list that seed sends about their connected peer nodes
                neigh_list = pickle.loads(list)
                for neigh in neigh_list:
                    self.peer_neighbour.add(neigh)  # Appending all the peer nodes to our neighbour list
            except Exception as e:
                pass
        
        # Making connection with choosen seed nodes and making threads for independent execution
        def connect_seed(self):
            threads = []
            for i in random_indices:
                Host = seed_list[i]["Host"]
                Port = seed_list[i]["Port"]
                thread = threading.Thread(target=self.connect_to_seed, args=(Host, Port))
                threads.append(thread)
                thread.start()
            for thread in threads:                    # Waiting for all the connection to complete with the seed node
                thread.join()

            num = random.randint(1,4)
            num = min(len(self.peer_neighbour),num)   # number of peer neighbour < 4 given
            self.peer_neighbour = random.sample(list(self.peer_neighbour), num)
            out_msg = ""
            if(len(self.peer_neighbour) == 0):
                out_msg = "First node have no neighbour"
            else:
                out_msg = f"This is the final neighbour peers {self.peer_neighbour}"
            self.outout_write(out_msg)                 # Output the final neighbour peer list 
        
        # Making the connection to the Neighbour Peers selected
        def connect_neighbour(self, host, port):
            try:
                neighbour_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                neighbour_socket.connect((host,port))
                self.neigh_socket_lst.append(neighbour_socket)
                self.no_response_ct[neighbour_socket] = 0
                threading.Thread(target= self.handle_gossip_msg, args= (neighbour_socket, )).start()   
                threading.Thread(target= self.handle_neighbour, args= (neighbour_socket ,self.id)).start()
            except:
                pass
        
        def conn_to_neigh(self):
            for neighbours in self.peer_neighbour:
                neigh_host, neigh_port = neighbours 
                threading.Thread(target= self.connect_neighbour, args= (neigh_host, neigh_port)).start()

        # Function for the propagation of the gossip message
        def handle_propagation(self, prop_socket, msg):
            try:
                msg = json.dumps(["propagated", self.id, msg, datetime.now().time().strftime("%Y-%m-%d %H:%M:%S")])
                prop_socket.sendall(msg.encode())
            except:
                pass
            
        def propagate(self, msg):
            self.lock.acquire()                         # This lock ensures that the neigh_socket_lst do not get changed while running in the for loop as it could make errors
            for socket in self.neigh_socket_lst:
                thread = threading.Thread(target= self.handle_propagation, args= (socket, msg))
                thread.start()
            self.lock.release()

        # Listen to the Peer that is sending the message that can be gossip or propagated or Liveliness
        def handle_neighbour(self, neigh_socket, id):
            try:
                while True:
                    peer_msg = neigh_socket.recv(1024)
                    if not peer_msg:
                        continue
                    peer_msg = json.loads(peer_msg.decode())
                    self.socket_to_id[neigh_socket] = peer_msg[1]
                    key_pair = (peer_msg[2], peer_msg[3])
                    if(peer_msg[0] == "gossip" or peer_msg[0] == "propagated"):  # If the message is gossip or propagated than we need to check whether the
                        if key_pair not in self.ML:                              # message is in the ML dictionary, if not so then we need to propagate that message to
                            self.ML[key_pair] = 1                                # the neighbouring peers
                            self.out_handle(peer_msg[3], peer_msg[1], peer_msg[2])
                            threading.Thread(target= self.propagate, args=(peer_msg[2],)).start()
            except Exception as e:
                pass

        # Want to listen all the Peers in the separate thread
        def listen_neighbour(self):
            try:
                while True:
                    neigh_socket, id = self.peer_socket.accept()
                    threading.Thread(target=self.handle_neighbour, args=(neigh_socket,id)).start()  # Receiving the message from other Peers
                    threading.Thread(target=self.handle_gossip_msg, args=(neigh_socket,)).start()   # Sending the messages to the connected Peers
                    self.lock.acquire()                                           # Lock necessary to prevent the resource corruption as it is a shared resource
                    self.neigh_socket_lst.append(neigh_socket)
                    self.no_response_ct[neigh_socket] = 0
                    self.lock.release()
            except Exception as e:
                pass

        # Function for sending the gossip message to all the peer nodes
        def handle_gossip_msg(self, gossip_socket):
            try:
                count = 10
                while(count > 0):
                    msg = ["gossip", self.id, f"This is a gossip message initiated from {self.id}", datetime.now().time().strftime("%Y-%m-%d %H:%M:%S")]
                    message = json.dumps(msg)
                    self.ML[(msg[2],msg[3])] = 1
                    gossip_socket.sendall(message.encode())
                    count -= 1
                    time.sleep(5)
            except:
                pass

        # Function for sending the liveliness message, If the Peer is not responding to the liveliness, means it is dead and need to be removed
        def handle_liv_msg(self, liv_socket, msg):
            message = json.dumps(["live", self.id, "This is a liveliness message", datetime.now().time().strftime("%Y-%m-%d %H:%M:%S")])
            try:
                liv_socket.sendall(message.encode())
            except:
                self.no_response_ct[liv_socket] += 1
                if(self.no_response_ct[liv_socket] == 3):               # maximum 3 times Peer did not responded
                    threading.Thread(target= self.handle_dead, args= (liv_socket,)).start()
                    self.lock.acquire()
                    liv_socket.close()
                    self.neigh_socket_lst.remove(liv_socket)
                    self.lock.release()

        def liveliness_msg(self):
            try:
                while True:
                    self.lock.acquire()
                    for socket in self.neigh_socket_lst:
                        threading.Thread(target= self.handle_liv_msg, args= (socket, self.msg)).start()
                    self.lock.release()
                    time.sleep(13)
            except:
                pass

        # Handle all the dead_peers
        def send_dead_peer(self, seed, dead_socket):
            try:
                id = self.socket_to_id[dead_socket]                     # Id of the dead peer
                out_msg = f"{id} is the dead node and need to report to the seed"
                self.outout_write(out_msg)
                message = json.dumps(id)                                # send the dead message to the seed node
                seed.sendall(message.encode())
            except:
                pass

        def handle_dead(self, dead_socket):
            for seeds in self.peer_seed:
                threading.Thread(target= self.send_dead_peer, args= (seeds, dead_socket)).start() 

        # Function to start the Peer Node
        def start(self):
            self.connect_seed()
            threading.Thread(target= self.conn_to_neigh).start()
            threading.Thread(target= self.listen_neighbour).start()
            threading.Thread(target= self.liveliness_msg).start()

    Host =  input("Please type the Host id of the peer = ")      # 127.0.1.1
    Port = int(input("Please type the Port id of the peer = "))  # 1
    Peer_node = Peer(Host,Port)
    Peer_node.start()                                            # start the Peer node

if __name__ == "__main__":
    main()
