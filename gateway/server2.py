"""
Name:          Sean Hassett

Based on code provided by https://stackoverflow.com/users/2814626/nettux443
"""

import socket
import threading
import packet_utils

TIMEOUT = 120
IP = '127.0.0.1'
PORT = 50001
BUFFER_SIZE = 1024
STARTING_SEQUENCE_NUMBER = 0
MAX_SEQUENCE_NUMBER = 2


class Server(object):
    def __init__(self, host, port):
        self.sequence_number = STARTING_SEQUENCE_NUMBER
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.client_dict = {}

    def listen_for_gateway(self):
        print("Server2\nListening for gateway...\n")
        self.sock.listen(5)
        while True:
            gateway, address = self.sock.accept()
            gateway.settimeout(TIMEOUT)
            threading.Thread(target=self.listen, args=(gateway, address)).start()

    def listen(self, gateway, address):
        size = BUFFER_SIZE
        while True:
            try:
                packet = gateway.recv(size)
                if packet:
                    unpacked = packet_utils.unpack(packet)
                    client_sequence_num = unpacked.sequence_number
                    source_ip = unpacked.source_ip
                    source_port = unpacked.source_port
                    data = unpacked.data

                    client_id = source_port
                    destination_ip = source_ip
                    destination_port = source_port

                    if client_id not in self.client_dict:
                        self.client_dict[client_id] = 0

                    expected_sequence_number = self.client_dict[client_id]

                    sequence_number = self.sequence_number
                    if client_sequence_num == expected_sequence_number:
                        print(data)
                        self.client_dict[client_id] += 1
                        if self.client_dict[client_id] > MAX_SEQUENCE_NUMBER:
                            self.client_dict[client_id] = 0
                        next_sequence_number = self.client_dict[client_id]
                        response_packet = packet_utils.create_packet(sequence_number, IP, PORT, destination_ip,
                                                                     destination_port,
                                                                     bytes(str(next_sequence_number), "utf-8"))
                    else:
                        response_packet = packet_utils.create_packet(sequence_number, IP, PORT, destination_ip,
                                                                     destination_port,
                                                                     bytes(str(expected_sequence_number), "utf-8"))
                    gateway.sendall(response_packet)
                    gateway.close()
                    self.sequence_number += 1
                    if self.sequence_number > MAX_SEQUENCE_NUMBER:
                        self.sequence_number = 0
                else:
                    gateway.close()
            except:
                gateway.close()
                return

if __name__ == "__main__":
    Server(IP, PORT).listen_for_gateway()
