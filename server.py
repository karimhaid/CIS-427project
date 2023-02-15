import socket
import sqlite3


# List of commands for client to use
COMMANDS = ["BUY", "SELL", "BALANCE", "LIST", "SHUTDOWN", "QUIT"]


def valid_command(command):
    # Check if first word is valid and if word count is valid
    if command[0] not in COMMANDS or len(command) > 5:
        return False
    # Check if BUY command has valid stock ticker
    if command[0] == "BUY" and (len(command) != 5 or \
        len(command[1]) > 5):
        return False
    # Check if BUY command has valid numeric values
    elif command[0] == "BUY":
        try:
            float(command[2])  # stock quantity
            float(command[3])  # price
            int(command[4])  # user ID
        except ValueError:
            return False
    # Check the same as above in BUY but for SELL command
    if command[0] == "SELL" and (len(command) != 5 or \
        len(command[1]) > 5):
        return False
    elif command[0] == "SELL":
        try:
            float(command[2])
            float(command[3])
            int(command[4])
        except ValueError:
            return False
    # Check if remaining commands are only one word
    if command[0] == "LIST" and len(command) != 1:
        return False
    if command[0] == "BALANCE" and len(command) != 1:
        return False
    if command[0] == "SHUTDOWN" and len(command) != 1:
        return False
    if command[0] == "QUIT" and len(command) != 1:
        return False
    # Otherwise return True indicating valid command
    return True


def buy_command(sock, db, command):
    # Initialize DB cursor for SQL
    cursor = db.cursor()
    # Determine cost and get user balance
    cost = float(command[2]) * float(command[3])  # quantity * price
    cursor.execute("SELECT USD_BALANCE FROM USERS WHERE ID = " +
    command[4] + ";")
    result = cursor.fetchone()
    if result is None:
        sock.send("{}".format(
            "400 invalid command: user " + command[4] +
            " doesn't exist\n"  
        ))
        return
    initial_bal = result[0]

    # Error if user has insufficient balance
    if cost > initial_bal:
        sock.send("{}".format(
            "400 invalid command: Insufficient funds\n"  
        ))
        return

    # Determine new balance and get user's current stock
    new_bal = initial_bal - cost
    ticker = command[1]
    cursor.execute("SELECT * FROM STOCKS WHERE USER_ID = " +
    command[4] + " AND STOCK_SYMBOL = '" + ticker + "';")
    result = cursor.fetchone()

    # Add stock if user doesn't yet have
    if result is None:
        db.execute("INSERT INTO STOCKS (STOCK_SYMBOL," +
        "STOCK_NAME, STOCK_BALANCE, USER_ID) VALUES ('" +
        ticker + "', '" + ticker + "', " + command[2] + ", " + 
        command[4] + ");")
    # Otherwise increment the user's stock
    else:
        db.execute("UPDATE STOCKS SET STOCK_BALANCE = STOCK_BALANCE + " +
        command[2] + " WHERE USER_ID = " +
        command[4] + " AND STOCK_SYMBOL = '" +
        ticker + "';")
    # Update user's balance
    db.execute("UPDATE USERS SET USD_BALANCE = " + str(new_bal) +
    " WHERE ID = " + command[4] + ";")
    db.commit()

    # Get STOCK_BALANCE for outgoing message to client
    cursor.execute("SELECT STOCK_BALANCE FROM STOCKS WHERE " +
    "USER_ID = " + command[4] + " AND STOCK_SYMBOL = '" + ticker + "';")
    result = cursor.fetchone()

    # Indicate success to client with info
    sock.send("{}".format(
        "200 OK\nBOUGHT: New balance: " + str(result[0]) + " " +
        ticker + ". USD balance " + str(new_bal) + "\n"
    ))


def sell_command(sock, db, command):
    # Initialize DB cursor for SQL
    cursor = db.cursor()
    # Determine gain and get user balance
    gain = float(command[2]) * float(command[3])  # quantity * price
    cursor.execute("SELECT USD_BALANCE FROM USERS " +
    "WHERE ID = " + command[4] + ";")
    result = cursor.fetchone()
    if result is None:
        sock.send("{}".format(
            "400 invalid command: user " + command[4] +
            " doesn't exist\n"  
        ))
        return
    initial_bal = result[0]
    ticker = command[1]

    # Get user's stock balance
    cursor.execute("SELECT STOCK_BALANCE FROM STOCKS WHERE "+
    "USER_ID = " + command[4] + " AND STOCK_SYMBOL = '" + ticker + "';")
    result = cursor.fetchone()

    # Error if user doesn't have the stock
    if result is None:
        sock.send("{}".format(
            "400 invalid command: Stock not found in bought list\n" 
        ))
        return
    initial_stock_bal = result[0]

    # Error if user has insufficient stock
    if float(command[2]) > initial_stock_bal:
        sock.send("{}".format(
            "400 invalid command: Insufficient stock\n" 
        ))
        return

    # Determine new balance and update that and stock amount
    new_bal = initial_bal + gain
    db.execute("UPDATE STOCKS SET STOCK_BALANCE = STOCK_BALANCE - " +
    command[2] + " WHERE USER_ID = " + command[4] + " AND STOCK_SYMBOL = '" +
    ticker + "';")
    db.execute("UPDATE USERS SET USD_BALANCE = " + str(new_bal) +
    " WHERE ID = " + command[4] + ";")
    db.commit()

    # Get updated balances for outgoing message to client
    cursor.execute("SELECT STOCK_BALANCE FROM STOCKS WHERE " +
    "USER_ID = " + command[4] + " AND STOCK_SYMBOL = '" + ticker + "';")
    result = cursor.fetchone()

    # Indicate success to client with info
    sock.send("{}".format(
        "200 OK\nSOLD: New balance: " + str(result[0]) + " " + ticker +
        ". USD balance " + str(new_bal) + "\n"
    ))


def bal_command(sock, db, command):
    # Initialize DB cursor for SQL
    cursor = db.cursor()
    # Get user's name and balance
    # (default to USER_ID = 1 for this program)
    cursor.execute("""SELECT FIRST_NAME, LAST_NAME,
    USD_BALANCE FROM USERS WHERE ID = 1;""")
    result = cursor.fetchone()
    name = result[0] + " " + result[1]
    bal = format(result[2], ".2f")

    # Outgoing client message with info
    sock.send("{}".format(
        "200 OK\nBalance for user " + name + ": " + bal + "\n"
    ))


def list_command(sock, db, command):
    # Initialize DB cursor for SQL
    cursor = db.cursor()
    # Get listing info from user for each stock and output
    # (default to USER_ID = 1 for this program)
    cursor.execute("SELECT ID FROM STOCKS WHERE USER_ID=1;")
    result = cursor.fetchone()
    # Send client a message if no stocks yet traded
    if result is None:
        output="EMPTY: no stocks have been traded yet"
    else:
        output="The list of records in the Stocks database for user 1: \n"
        for row in cursor.execute("""SELECT ID,STOCK_SYMBOL,STOCK_BALANCE,USER_ID FROM STOCKS
        WHERE USER_ID = 1;"""):
            Stock=str(row[0])+" "+str(row[1])+" "+str(row[2])
            User=str(row[3])
            output+=Stock+" "+ User+"\n"

    # Outgoing client message with info
    sock.send("{}".format(
        "200 OK\n" + output
        ))


def start_server():
    # Create database connection and tables
    conn = sqlite3.connect("trading.db")
    print("CONNECTED TO DATABASE")

    # USE THIS BLOCK FOR RESETTING THE TABLES!!!
    # conn.execute("DROP TABLE IF EXISTS USERS;")
    # conn.execute("DROP TABLE IF EXISTS STOCKS;")
    # conn.commit()
    # USE ABOVE BLOCK FOR RESETTING THE TABLES!!!

    # Create the USERS and STOCKS tables if missing
    conn.execute(
        """CREATE TABLE IF NOT EXISTS USERS
        (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FIRST_NAME VARCHAR(255),
            LAST_NAME VARCHAR(255),
            USER_NAME VARCHAR(255) NOT NULL,
            PASSWORD VARCHAR(255),
            USD_BALANCE DOUBLE NOT NULL
        );"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS STOCKS
        (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            STOCK_SYMBOL VARCHAR(4) NOT NULL,
            STOCK_NAME VARCHAR(20) NOT NULL,
            STOCK_BALANCE DOUBLE,
            USER_ID INTEGER,
            FOREIGN KEY (USER_ID) REFERENCES USERS (ID)
        );"""
    )

    # Check if USERS is empty and add default user if so
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS LIMIT 1")
    if cursor.fetchone() is None:
        conn.execute("""INSERT INTO USERS (FIRST_NAME,
        LAST_NAME, USER_NAME, PASSWORD, USD_BALANCE)
        VALUES ('Jonathan', 'McMillan', 'jrmcmill',
        '1234', 100.00);""")
        conn.commit()
        print("ADDED DEFAULT USER TO EMPTY TABLE")

    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Ensure quick server restart
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", 5753))
    server_socket.listen(1)

    # Accept incoming connections
    print("Waiting for incoming connections...")
    client_socket, client_address = server_socket.accept()
    print("Accepted connection from {}".format(client_address))

    # Communicate with the client
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if not data:
            break
        print("Received: {}".format(data))
        words = data.split()

        # Check if user sent a valid command
        if valid_command(words):
            if words[0] == "BUY":
                buy_command(client_socket, conn, words)
            elif words[0] == "SELL":
                sell_command(client_socket, conn, words)
            elif words[0] == "BALANCE":
                bal_command(client_socket, conn, words)
            elif words[0] == "LIST":
                list_command(client_socket, conn, words)
            elif words[0] == "QUIT":
                client_socket.send("{}".format(
                    "200 OK\n"
                ))
                server_socket.close()
                print("Connection closed")
            elif words[0] == "SHUTDOWN":
                client_socket.send("{}".format(
                    "200 OK\n"
                ))
                client_socket.close()
                server_socket.close()
                conn.close()
                print("Connection closed")
                exit()
        # Otherwise indicate invalid command received
        else:
            client_socket.send("{}".format(
                # Invalid command error
                "403 message format error: check input and try again\n"
            ))


if __name__ == "__main__":
    # Start the server and wait for client connection
    while True:
        start_server()
