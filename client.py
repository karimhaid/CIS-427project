import socket
import sys


# List of valid arguments
VALID_IPS = ["localhost", "127.0.0.1"]


def start_client(ip):
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, 5753))

    # Communicate with the server
    while True:
        # Send data to the server
        send_data = raw_input("COMMAND: ")
        client_socket.send(send_data)

        # Receive data from the server
        get_data = client_socket.recv(1024)
        if not get_data:
            break
        #print("Received data: {}".format(get_data))
        print("{}".format(get_data))

        # Clean up for SHUTDOWN and QUIT commands
        if send_data == "SHUTDOWN" or send_data == "QUIT":
            client_socket.close()
            print("Connection closed")
            exit()


if __name__ == '__main__':
    # Get IP argument for client connection
    try:
        ip_address = sys.argv[1]
    except IndexError:
        print("Usage: client <Server IP Address> INVALID IP")
        exit()

    # Error for invalid arguments or missing argument
    if len(sys.argv) < 2 or ip_address not in VALID_IPS:
        print("Usage: client <Server IP Address> INVALID IP")
        exit()
    # Otherwise start the client with the given argument
    else:
        start_client(ip_address)
