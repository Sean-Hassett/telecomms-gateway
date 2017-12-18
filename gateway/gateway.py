"""
Name:          Sean Hassett
"""

import socket
import threading
import packet_utils

TIMEOUT = 600
IP = '127.0.0.1'
PORT = 40000
BUFFER_SIZE = 1024


class Gateway(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen_for_clients(self):
        print("Gateway\nListening for clients...")
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(TIMEOUT)
            threading.Thread(target=self.listen, args=(client, address)).start()
            print("connected to client @{}:{}\n".format(address[0], address[1]))

    def listen(self, client, address):
        size = BUFFER_SIZE
        while True:
            try:
                packet = client.recv(size)
                if packet:
                    print("RECEIVED PACKET FROM {}:{}".format(address[0], address[1]))
                    unpacked = packet_utils.unpack(packet)
                    client_packet = packet_utils.unpack(bytes(unpacked.data, "utf-8"))

                    sequence_number = client_packet.sequence_number
                    source_ip = address[0]
                    source_port = address[1]
                    destination_ip = client_packet.destination_ip
                    destination_port = client_packet.destination_port
                    data = bytes(client_packet.data, "utf-8")

                    print("DESTINATION: {}:{}".format(destination_ip, destination_port))
                    print("SEQUENCE NO.: {}".format(sequence_number))

                    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    try:
                        server_sock.connect((destination_ip, destination_port))
                    except ConnectionRefusedError:
                        print('ERROR: The connection was refused, is the server running?')
                        input("Press enter to quit")

                    server_packet = packet_utils.create_packet(sequence_number, source_ip, source_port, destination_ip,
                                                               destination_port, data)
                    packet_utils.to_string(server_packet)
                    print("forwarding to server...\n")
                    server_sock.sendall(server_packet)

                    server_response = server_sock.recv(BUFFER_SIZE)
                    unpacked = packet_utils.unpack(server_response)
                    data = unpacked.data
                    print("SERVER RESPONSE: {}\n".format(data))
                    client.sendall(server_response)
                else:
                    client.close()
            except:
                client.close()
                return

if __name__ == "__main__":
    Gateway(IP, PORT).listen_for_clients()
