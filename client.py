import socket

def start_client():
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 5753))

    # Communicate with the server
    try:
        while True:
            # Send data to the server
            send_data = raw_input("COMMAND: ")
            if send_data == "QUIT":
                print("200 OK")
                break
            client_socket.send(send_data)

            # Receive data from the server
            get_data = client_socket.recv(1024)
            if not get_data:
                break
            print("Received data: {}".format(get_data))
            if send_data == "SHUTDOWN":
                break
    finally:
        # Clean up
        client_socket.close()
        print("Connection closed")

if __name__ == '__main__':
    start_client()
