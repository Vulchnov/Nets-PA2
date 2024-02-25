import struct
import sys
import socket


def create_struct(short_int1, long_int1, long_int2, str_32_byte):
    # This function will be used to create a universal struct object
    message = struct.pack('!HLL32s', short_int1, long_int1, long_int2, str_32_byte)
    return message
    

def open_struct(struct_obj):
    # This function will be used to open a universal struct object
    message = struct.unpack('!HLL32s', struct_obj)
    return message  # Returns array [short, long, long, 32-byte string]

def create_initialization(hash_requests):
    # This function will be used to create the initialization message to send to the server using struct
    # Then, return the message
    empty_binary = bytes(32)
    message = create_struct(0x1, socket.htonl(hash_requests), 0, empty_binary)
    return message


def create_hash_request(hash_count, block_size, current_block):
    # This function will create a Hash Request
    # Then, return the message as a struct obj

    hash_count += 1;
    block_len = block_size
    struct_hash_message = create_struct(0x3, hash_count, block_len, current_block)

    return struct_hash_message


def check_acknowledgement(encoded_data):
    try:
        initial_message = open_struct(encoded_data)
        type_val = initial_message[0]
        if type_val != 0x2:
            print("CLIENT: Invalid Type Value")
            return False
        return initial_message[2] # Returns the Length from Ack Message
    except:
        print("CLIENT: Invalid Data Format")
        return False


def check_hash_response(encoded_data):
    try:
        initial_message = open_struct(encoded_data)
        type_val = initial_message[0]
        print(type_val)
        if type_val != 0x4:
            print("CLIENT: Invalid Type Value")
            return False
        return initial_message # Returns Struct Object
    except:
        print("CLIENT: Invalid Data Format")
        return False


def connect_server(ip, port):
    # This function will be used to create a socket and connect to server
    # Then, return the socket object
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((ip, port))

    print("Connected to server!")
    return tcp_socket


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Variables we need from the command line
    server_ip = sys.argv[2]  # Extract server IP
    server_port = int(sys.argv[4])  # Extract server port
    hash_block_size = int(sys.argv[6])  # Extract S
    file_path = sys.argv[8]  # Extract file path

    # Open our file from command line
    chosen_file = open(file_path, 'rb')

    # Connect to the server!
    server_socket = connect_server(server_ip, server_port)

    # Initialization Message Portion
    # Write your logic for initilization message
    init_message = create_initialization(hash_block_size)
    server_socket.sendall(init_message)
    print("Initialization sent.")

    # Acknowledgement Message Verification (write your code below)
    ack_message = server_socket.recv(1024)
    ack_length = check_acknowledgement(ack_message)

    if ack_length is False:
        print("Ack failed.")
    else:
        print("ACK received from server.")
    

    # Let's keep track of hash count, and our new hashed data file
    # you can write the hash values received from the server in this file
    count = 0
    hashed_data = open("hashed_data.txt", 'w')
    print("New Hashed File Created.")
    # Use a loop to send each block
    
    # Write your code to implement client's side protocol logic.
    while True:
        current_block = chosen_file.read(hash_block_size)
        if not current_block:
            break
        hash_request_message = create_hash_request(count, hash_block_size, current_block)
        server_socket.sendall(hash_request_message)

        hash_response = server_socket.recv(1024)
        response = check_hash_response(hash_response)

        if response is False:
            print("Error receive hash response.")
            continue
            
        hash_value = response[3]
        hashed_data.write(hash_value.hex())
        hashed_data.write('\n')
        count += 1

    # We're done - Let's close our open files and sockets
    print("Done! Closing files and sockets.")
    hashed_data.close()  # New Hash Data File
    chosen_file.close()  # Command Line File
    server_socket.close()  # Server Socket



