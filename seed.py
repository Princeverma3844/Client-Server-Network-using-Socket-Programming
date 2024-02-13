import json
import socket
import threading
import pickle
import os
# Read data from the JSON config file

def main():

    # Read data from the JSON config file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = "config.json"
    file_path = os.path.join(current_dir, filename)
    with open(file_path) as f:
        config_data = json.load(f)

    N = config_data["N"]
    seed_list = config_data["Seed_info"]
    print("The number of seed nodes = ", N)

    # Making the seed node
    class seed:
        # Parameter initialised
        def __init__(self, Host, Port):
            self.Host = Host
            self.Port = Port
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.Host, self.Port))
            self.server_socket.listen()
            self.Peer_list = []
            self.lock_output = threading.Lock()
            self.lock = threading.Lock()

        # Writing the output to the console as well as to the output file
        def outout_write(self, msg):
            self.lock_output.acquire()                  # Lock ensures that the common resource is not corrupted
            print(msg)
            out_filename = f"seed_output{self.Port}.txt"
            out_path = os.path.join(current_dir, out_filename)
            with open(out_path, "a") as file:
                file.write(msg + "\n")
            self.lock_output.release()

        # Function Communicates with the Peer nodes
        def handle_node(self, seed_socket, peer_address):
            msg = f"{self.Port} seed node accepted connection from {peer_address}"
            self.outout_write(msg)
            peer_id = seed_socket.recv(1024)
            peer_id = pickle.loads(peer_id)
            neigh_list = pickle.dumps(self.Peer_list)
            seed_socket.sendall(neigh_list)
            self.Peer_list.append(peer_id)
            while True:
                try:
                    msg = seed_socket.recv(1024)
                    dead_id = json.loads(msg.decode())
                    msg_out = f"I am seed with ip = [{self.Host},{self.Port}] and this is the dead node id = {dead_id}"
                    self.outout_write(msg_out)
                    if (dead_id[0], dead_id[1]) in self.Peer_list:
                        self.Peer_list.remove(dead_id)
                except:
                    pass
        
        # Ready to listen to the Peers
        def connect(self):
            while True:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(target=self.handle_node, args=(client_socket, client_address)).start()

    for i in range(N):
        host = seed_list[i]["Host"]
        port = seed_list[i]["Port"]
        seed_Node = seed(host, port)
        threading.Thread(target=seed_Node.connect).start()

if __name__ == "__main__":
    main()