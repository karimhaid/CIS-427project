import socket
import sqlite3

# List of commands for client to use
COMMANDS = ["BUY", "SELL", "BALANCE", "LIST", "SHUTDOWN", "QUIT"]

def valid_command(command):
    if command[0] not in COMMANDS or len(command) > 6:
        return False
    else:
        return True

def start_server():
    # Create database connection and tables
    conn = sqlite3.connect("trading.db")
    print("CONNECTED TO DATABASE")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS USERS
        (
            ID INTEGER AUTO_INCREMENT NOT NULL,
            FIRST_NAME VARCHAR(255),
            LAST_NAME VARCHAR(255),
            USER_NAME VARCHAR(255) NOT NULL,
            PASSWORD VARCHAR(255),
            USD_BALANCE DOUBLE NOT NULL,
            PRIMARY KEY (ID)
        );"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS STOCKS
        (
            ID INTEGER AUTO_INCREMENT NOT NULL,
            STOCK_SYMBOL VARCHAR(4) NOT NULL,
            STOCK_NAME VARCHAR(20) NOT NULL,
            STOCK_BALANCE DOUBLE,
            USER_ID INTEGER,
            PRIMARY KEY (ID),
            FOREIGN KEY (USER_ID) REFERENCES USERS (ID)
        );"""
    )

    # Check if database is empty and add user if so
    cursor = conn.cursor()
    cursor = conn.execute("SELECT * FROM USERS LIMIT 1")
    if cursor.fetchone() is None:
        conn.execute("""INSERT INTO USERS (ID, FIRST_NAME,
        LAST_NAME, USER_NAME, PASSWORD, USD_BALANCE)
        VALUES (1, 'Jonathan', 'McMillan', 'jrmcmill',
        '1234', 100.00)""")
        conn.commit()
        print("ADDED DEFAULT USER TO EMPTY DATABASE")

    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 5753))
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
            words = data.split()

            # Check if user sent a valid command
            if valid_command == True:
                client_socket.send("{}".format(
                    "VALID COMMAND"
                ))
            else:
                client_socket.send("{}".format(
                    "INVALID COMMAND"
                ))

            # Send data back to the client
            # server_message = raw_input("Enter message to send back to the client (quit to exit): ")
            # if server_message == "quit":
            #     break
            # client_socket.send("{}".format(server_message))
    finally:
        # Clean up
        client_socket.close()
        server_socket.close()
        print("Connection closed")

if __name__ == "__main__":
    while True:
        start_server()
