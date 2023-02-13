import socket
import sys


VALID_IPS = ["localhost", "127.0.0.1"]


def start_client(ip):
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, 5753))

    # Communicate with the server
    #try:
    while True:
        # Send data to the server
        send_data = raw_input("COMMAND: ")
        # if send_data == "QUIT":
        #     print("200 OK")
        #     break
        client_socket.send(send_data)

        # Receive data from the server
        get_data = client_socket.recv(1024)
        if not get_data:
            break
        print("Received data: {}".format(get_data))
        if send_data == "SHUTDOWN" or send_data == "QUIT":
            client_socket.close()
            print("Connection closed")
            exit()
    # finally:
    #     # Clean up
    #     client_socket.close()
    #     print("Connection closed")
    #     exit()


if __name__ == '__main__':
    ip_address = sys.argv[1]

    if len(sys.argv) < 2 or ip_address not in VALID_IPS:
        print("Usage: client <Server IP Address>")
        exit()
    else:
        start_client(ip_address)
