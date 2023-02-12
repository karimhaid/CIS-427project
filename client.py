import socket

def start_client():
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 5753))

    # Communicate with the server
    try:
        while True:
            # Send data to the server
            data = raw_input("Enter data to send (quit to exit): ")
            if data == "quit":
                break
            client_socket.send(data)

            # Receive data from the server
            data = client_socket.recv(1024)
            if not data:
                break
            print("Received data: {}".format(data))
    finally:
        # Clean up
        client_socket.close()
        print("Connection closed")

if __name__ == '__main__':
    start_client()
