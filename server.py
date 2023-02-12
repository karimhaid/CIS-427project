import socket

def start_server():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 5753))
    server_socket.listen(1)

    # Accept incoming connections
    print("Waiting for incoming connections...")
    client_socket, client_address = server_socket.accept()
    print("Accepted connection from {}".format(client_address))

    # Communicate with the client
    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024)
            if not data:
                break
            print("Received data from client: {}".format(data))

            # Send data back to the client
            server_message = raw_input("Enter message to send back to the client (quit to exit): ")
            if server_message == "quit":
                break
            client_socket.send("ACK: {}".format(server_message))
    finally:
        # Clean up
        client_socket.close()
        server_socket.close()
        print("Connection closed")

if __name__ == '__main__':
    while True:
        start_server()
