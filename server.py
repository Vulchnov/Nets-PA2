import struct
import sys
import socket
import select
import hashlib

def create_struct(short_int1, long_int1, long_int2, str_32_byte):
    # This function will be used to create a universal struct object
    message = struct.pack('!HLL32s', short_int1, long_int1, long_int2, str_32_byte)
    return message
    

def open_struct(struct_obj):
    # This function will be used to open a universal struct object
    message = struct.unpack('!HLL32s', struct_obj)
    return message  # Returns array [short, long, long, 32-byte string]


def create_acknowledgement(input_n):
    # This function retrieves the S value from the initialization message
    # Then, return acknowledgement message
    
    # Write your logic
    type = 0x2
    length = input_n #This is where you would normally do the 40 * S that the pdf asks for, however that is to large for the struct.pack() method
    empty_payload = bytes(32)
    message = create_struct(type, 0, length, empty_payload)
    return message


def check_initialization(encoded_data):
    try:
        initial_message = open_struct(encoded_data)
        num_hash_requests = initial_message[1]  # Block sizes this client will send
        type_val = initial_message[0]
        if type_val != 0x1:
            print("SERVER: Invalid Type Value")
            return False
        return num_hash_requests
    except:
        print("SERVER: Invalid Data Format")
        return False
    
def check_hash_request(encoded_data):
    try:
        initial_message = open_struct(encoded_data)
        type_val = initial_message[0]
        if type_val != 0x3:
            print("SERVER: Invalid Type Value")
            return False 
        return initial_message # Struct Object
    except:
        print("SERVER: Invalid Data Format")
        return False


def get_hashed_data(hash_request):
    # This function will receive an unpacked struct representing our hash request
    # Then, return hashed data and hash response

    # Extract variables
    request_type = 0x4
    request_i = hash_request[1]  # HashRequest i
    request_len = 32  # HashRequest Length
    request_payload = hash_salt.encode('utf-8') + hash_request[3]  # HashRequest Data + UTF-8 Encoded Salt
    hash_and_salt = hashlib.sha256(request_payload).digest() #Hash the message and use digest() to convert it to bytes
    request_i += 1
    return create_struct(request_type, request_i, request_len, hash_and_salt)


def start_server(port):
    # This function will create our TCP Server Socket, start listening, then return the Socket Object

    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.setblocking(False)  # Allow multiple connections
    tcp_server_socket.bind(('', port))  # Start listening!
    tcp_server_socket.listen(10)  # 10 is the max number of queued connections allowed
    return tcp_server_socket


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Variables we need
    for i in range(len(sys.argv)-1):
        if sys.argv[i] == "-p":
            server_port = int(sys.argv[i+1])  # Extract server port from command line arguments
        elif sys.argv[i] == "-s":
            hash_salt = sys.argv[i+1]  # Extract salt value from command line arguments

    server_socket = start_server(server_port)
    clients = [server_socket]
    n_sizes = {}
    print("Server listening...")

    ## WRITE YOUR CODE TO IMPLEMENT SERVER SIDE PROTOCOL LOGIC
    ## USE select() to handle multiple clients

    while True:
        readable, writable, errored = select.select(clients, [], [], 0.1)

        for s in readable:
            if s is server_socket: #If its a new connection accept and add them back to the list
                client_socket, address = server_socket.accept()
                print(f"connection made with {address}")
                clients.append(client_socket)
            else: #Else they are already accepted and waiting to be worked with
                try:
                    data = s.recv(1024)

                    if not data: #If nothing is recieved the client has disconnected early
                        print(f"Client disconnected")
                        clients.remove(s)
                        s.close()
                        continue

                    initial_message = open_struct(data) #Open the message
                    message_type = initial_message[0]

                    if message_type == 0x1: #If its an initialization message send an ack
                        n_size = check_initialization(data)
                        ack_message = create_acknowledgement(n_size)
                        s.sendall(ack_message)
                    elif message_type == 0x3: #Else hash the info and send it to the client
                        hash_request_info = check_hash_request(data)
                        if hash_request_info:
                            hashed_data_response = get_hashed_data(hash_request_info)
                            s.sendall(hashed_data_response)
                    else:
                        print(f"Unknown message type")

                except ConnectionResetError:
                    print(f"Client unexpectedly disconnected")
                    clients.remove(s)
                    s.close()





    
