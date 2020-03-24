import socket, time, random, struct, hashlib, binascii


# Binary encoding of sub version
def create_sub_version():
    sub_version = "/Satoshi:0.7.2/"
    return b"\x0F" + sub_version.encode();


# Binary encoding of network address
# \x01 - Identifies services field in network address structure \x01 refers to NODE_NETWORK
# The bytearray part is just representing an IPV4 address as an IPV6 address
# port is again converted to some byte form
def create_network_address(ip_addr, port):
    net_addr = struct.pack(">8s16sH", b'\x01',
                           bytearray.fromhex("00000000000000000000ffff") + socket.inet_aton(ip_addr), port)
    return net_addr


# Creating TCP request object
def create_message(magic, command, payload):
    # First 4 bytes of SHA256(SHA256(payload))
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[0:4]
    return struct.pack("L12sL4s", magic, command.encode(), len(payload), checksum) + payload


# Creating "version" request payload
def create_payload_ver(peer_ip_addr):
    version = 60002
    services = 1
    timestamp = int(time.time())
    addr_local = create_network_address("127.0.0.1", 8333)
    addr_peer = create_network_address(peer_ip_addr, 8333)
    nonce = random.getrandbits(64)
    start_height = 0
    payload = struct.pack('<LQQ26s26sQ16sL', version, services, timestamp, addr_peer,
                          addr_local, nonce, create_sub_version(), start_height)
    return payload


# Creating verack request message
def create_message_verack():
    return bytearray.fromhex("f9beb4d976657261636b000000000000000000005df6e0e2")


# Creating "getdata" request payload
def create_payload_getdata(tx_id):
    count = 1
    type = 1
    hash = bytearray.fromhex(tx_id)
    payload = struct.pack("<bb32s", count, type, hash)
    return payload


# Print req/res data
def print_response(command, req_data, res_data):
    print("")
    print("Command: " + command)
    print("Request:")
    print(binascii.hexlify(req_data))
    print("Response")
    print(binascii.hexlify(res_data))


if __name__ == '__main__':
    # magic value for the main network
    magic_value = 0xd9b4bef9
    tx_id = "fc57704eff327aecfadb2cf3774edc919ba69aba624b836461ce2be9c00a0c20"
    peer_ip_address = '104.199.184.15'
    peer_tcp_port = 8333
    buffer_size = 1024

    # Create Request Objects
    ver_payload = create_payload_ver(peer_ip_address)
    ver_msg = create_message(magic_value, 'version', ver_payload)
    ver_ack_msg = create_message_verack()
    get_data_payload = create_payload_getdata(tx_id)
    get_data_msg = create_message(magic_value, "getdata", get_data_payload)

    # Establish TCP connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((peer_ip_address, peer_tcp_port))

    # Send message "version"
    s.send(ver_msg)
    res_data = s.recv(buffer_size)
    print_response("version", ver_msg, res_data);

    # Send msg "verack"
    s.send(ver_ack_msg)
    res_data = s.recv(buffer_size)
    print_response("verack", ver_ack_msg, res_data)

    # Send msg "getdata"
    s.send(get_data_msg)
    res_data = s.recv(buffer_size)
    print_response("getdata", get_data_msg, res_data)

    s.close()
