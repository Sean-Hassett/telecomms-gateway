"""
Name:          Sean Hassett

Methods for conveniently packeting data to be sent between the client, gateway and server with the required
header information and unpacking packets on the other side
"""

from collections import namedtuple


def create_packet(sequence_number, source_ip, source_port, destination_ip, destination_port, data):
    """
    Takes the parameters passed in and converts them to a hex string representation
    Encodes the string and returns a bytes object
    """
    packet = ""
    packet += "{0:#0{1}x}".format(sequence_number, 6)[2:]    # bytes 0-1 - sequence_number

    ip_holder = source_ip.split(".")
    for element in ip_holder:
        packet += ("{0:#0{1}x}".format(int(element), 4)[2:])  # bytes 2-5 - source_ip

    packet += ("{0:#0{1}x}".format(source_port, 6)[2:])       # bytes 6-7 - source_port

    ip_holder = destination_ip.split(".")
    for element in ip_holder:
        packet += ("{0:#0{1}x}".format(int(element), 4)[2:])  # bytes 8-11 - destination_ip

    packet += ("{0:#0{1}x}".format(destination_port, 6)[2:])  # bytes 12-13 - destination_port

    for byte in data:
        packet += ("{0:#0{1}x}".format(byte, 4)[2:])          # bytes 14-   - data

    return bytes(packet, "utf-8")


def unpack(input_data):
    """
    Takes a Packet object and unpacks it into the original components
    Returns a namedtuple which contains the original components
    """
    output_data = namedtuple('output_data', ['sequence_number', 'source_ip', 'source_port', 'destination_ip',
                                             'destination_port', 'data'])

    data = input_data.decode("utf-8")

    output_data.sequence_number = int(data[0:4], 16)               # bytes 0-1 - sequence_number

    output_data.source_ip = ""
    output_data.source_ip += str(int(data[4:6], 16)) + "."
    output_data.source_ip += str(int(data[6:8], 16)) + "."
    output_data.source_ip += str(int(data[8:10], 16)) + "."
    output_data.source_ip += str(int(data[10:12], 16))             # bytes 2-5 - source_ip

    output_data.source_port = int(data[12:16], 16)                 # bytes 6-7 - source_port

    output_data.destination_ip = ""
    output_data.destination_ip += str(int(data[16:18], 16)) + "."
    output_data.destination_ip += str(int(data[18:20], 16)) + "."
    output_data.destination_ip += str(int(data[20:22], 16)) + "."
    output_data.destination_ip += str(int(data[22:24], 16))        # bytes 8-11 - destination_ip

    output_data.destination_port = int(data[24:28], 16)            # bytes 12-13 - destination_port

    output_data.data = ""                                          # bytes 14-   - data
    output_data.data += ''.join(chr(int(data[i:i+2], 16)) for i in range(28, len(data), 2))

    return output_data


def print_packet(packet):
    """
    Prints a hex string represenation of the packet passed in as well as a plaintext
    representation of the individual packet components
    """
    decoded = packet.decode("utf-8")
    print("")
    print(' '.join([decoded[i:i + 2] for i in range(0, len(decoded), 2)]))

    unpacked = unpack(packet)
    print("Sequence No.: {}".format(unpacked.sequence_number))
    print("Source IP: {}".format(unpacked.source_ip))
    print("Source Port: {}".format(unpacked.source_port))
    print("Dest. IP: {}".format(unpacked.destination_ip))
    print("Dest. Port: {}".format(unpacked.destination_port))
    print("Data: {}\n".format(unpacked.data))
