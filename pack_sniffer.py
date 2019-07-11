import socket
import struct
import textwrap
"""
Python network packet sniffer tutorial -> youtube
"""
HOST = socket.gethostbyname(socket.gethostname())

def main():
    conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)    # AF_INET\AF_PACKET IPPROTO_IP\ntohs(3)
    conn.bind((HOST, 0))
    conn.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
#    conn.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    while True:
        raw_data = conn.recvfrom(65536)
        dest_mac, src_mac, eth_proto, data = ethernet_frame(raw_data)
        print('\nEthernet Frame:')
        print('Destination: {}, Source: {}, Protocol: {}'.format(dest_mac, src_mac, eth_proto))

# Unpack ethernet frame
def ethernet_frame(data):
    dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[14:])
    return get_mac_addr(dest_mac), get_mac_addr(src_mac), socket.htons(proto), data[14:]

# return properly formatted MAC address (AA:BB:CC:DD:EE:FF)
def get_mac_addr(bytes_addr):
    bytes_str = map('{:02x}'.format, bytes_addr)
    return ':'.join(bytes_str).upper()



main()