"""
Name:          Sean Hassett
"""

from select import select
import socket
import packet_utils

IP = "127.0.0.1"
GATEWAY_IP = "127.0.0.1"
SERVER_IP = "127.0.0.1"
GATEWAY_PORT = 40000
SERVER_PORT_1 = 50000
SERVER_PORT_2 = 50001
SERVER_PORT_3 = 50002
BUFFER_SIZE = 1024
STARTING_SEQUENCE_NUMBER = 0
MAX_SEQUENCE_NUMBER = 2
RETRY_TIMEOUT = 5


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_dict = {}
        try:
            self.sock.connect((self.host, self.port))
            self.connected = True
        except ConnectionRefusedError:
            print('ERROR: The connection was refused, is the gateway running?')
            input("Press enter to quit")

    def communicate(self):
        while self.connected:
            try:
                message = bytes(input("Enter your message:\n"), "utf-8")

                have_server = False
                server_port = 0
                while not have_server:
                    server_number = input("Select a Server [1] [2] [3]: ")
                    if server_number == "1":
                        server_port = SERVER_PORT_1
                        have_server = True
                    elif server_number == "2":
                        server_port = SERVER_PORT_2
                        have_server = True
                    elif server_number == "3":
                        server_port = SERVER_PORT_3
                        have_server = True

                if server_port not in self.server_dict:
                    self.server_dict[server_port] = 0
                else:
                    self.server_dict[server_port] += 1
                    if self.server_dict[server_port] > MAX_SEQUENCE_NUMBER:
                        self.server_dict[server_port] = 0

                sequence_number = self.server_dict[server_port]

                server_packet = packet_utils.create_packet(sequence_number, IP, 0, SERVER_IP, server_port, message)
                gateway_packet = packet_utils.create_packet(sequence_number, IP, 0, GATEWAY_IP, GATEWAY_PORT,
                                                            server_packet)
                acknowledged = False

                while not acknowledged:
                    self.sock.sendall(gateway_packet)
                    try:
                        ready = select([self.sock], [], [], RETRY_TIMEOUT)
                        if ready[0]:
                            response_packet = self.sock.recv(BUFFER_SIZE)
                            unpacked = packet_utils.unpack(bytes(response_packet))
                            expected_next_sequence_number = unpacked.data
                            if int(expected_next_sequence_number) == int(sequence_number):
                                acknowledged = False
                                print("resending...")
                            else:
                                acknowledged = True
                    except ConnectionAbortedError:
                        print("Your connection has timed out, please restart the program.")
                        input("Press enter to quit")
                        break

            except ConnectionResetError:
                print("Your connection to the gateway has been lost, please restart the program.")
                input("Press enter to quit")
                break

if __name__ == "__main__":
    Client(IP, GATEWAY_PORT).communicate()
