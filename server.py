import socket
import sqlite3

# List of commands for client to use
COMMANDS = ["BUY", "SELL", "BALANCE", "LIST", "SHUTDOWN", "QUIT"]

def valid_command(command):
    if command[0] not in COMMANDS or len(command) > 5:
        return False
    if command[0] == "BUY" and (len(command) != 5 or \
        3 > len(command[1]) > 4):
        return False
    elif command[0] == "BUY":
        try:
            float(command[2])
            float(command[3])
        except ValueError:
            return False
    if command[0] == "SELL" and (len(command) != 5 or \
        3 > len(command[1]) > 4):
        return False
    elif command[0] == "SELL":
        try:
            float(command[2])
            float(command[3])
        except ValueError:
            return False
    if command[0] == "LIST" and len(command) != 1:
        return False
    if command[0] == "BALANCE" and len(command) != 1:
        return False
    if command[0] == "SHUTDOWN" and len(command) != 1:
        return False
    if command[0] == "QUIT" and len(command) != 1:
        return False
    return True

def buy_command(sock, db, command):
    cursor = db.cursor()
    cost = float(command[2]) * float(command[3])  # quantity * price
    cursor.execute("""SELECT USD_BALANCE FROM USERS
    WHERE ID = 1;""")
    result = cursor.fetchone()
    initial_bal = result[0]

    if cost > initial_bal:
        sock.send("{}".format(
            "ERROR NOT ENOUGH MONEY TO BUY"  # FIX THIS!!!
        ))
        return

    new_bal = initial_bal - cost
    ticker = command[1]
    cursor.execute("SELECT * FROM STOCKS WHERE USER_ID = 1 AND " +
    "STOCK_SYMBOL = '" + ticker + "';")
    result = cursor.fetchone()

    if result is None:
        db.execute("INSERT INTO STOCKS (STOCK_SYMBOL," +
        "STOCK_NAME, STOCK_BALANCE, USER_ID) VALUES ('" +
        ticker + "', '" + ticker + "', " + command[2] + ", 1);")
    else:
        db.execute("UPDATE STOCKS SET STOCK_BALANCE = STOCK_BALANCE + " +
        command[2] + " WHERE USER_ID = 1 AND STOCK_SYMBOL = '" +
        ticker + "';")
    db.execute("UPDATE USERS SET USD_BALANCE = " + str(new_bal) +
    " WHERE ID = 1;")
    db.commit()

    cursor.execute("SELECT STOCK_BALANCE FROM STOCKS WHERE " +
    "USER_ID = 1 AND STOCK_SYMBOL = '" + ticker + "';")
    result = cursor.fetchone()

    sock.send("{}".format(
        "200 OK\nBOUGHT: New balance: " + str(result[0]) + " " +
        ticker + ". USD balance " + str(new_bal)
    ))

def sell_command(sock, db, command):
    cursor = db.cursor()
    gain = float(command[2]) * float(command[3])  # quantity * price
    cursor.execute("""SELECT USD_BALANCE FROM USERS
    WHERE ID = 1;""")
    result = cursor.fetchone()
    initial_bal = result[0]
    ticker = command[1]

    cursor.execute("SELECT STOCK_BALANCE FROM STOCKS WHERE "+
    "USER_ID = 1 AND STOCK_SYMBOL = '" + ticker + "';")
    result = cursor.fetchone()

    if result is None:
        sock.send("{}".format(
            "ERROR DON'T HAVE STOCK"  # FIX THIS!!!
        ))
        return
    initial_stock_bal = result[0]

    if float(command[2]) > initial_stock_bal:
        sock.send("{}".format(
            "ERROR DON'T HAVE ENOUGH TO SELL"  # FIX THIS!!!
        ))
        return

    new_bal = initial_bal + gain
    db.execute("UPDATE STOCKS SET STOCK_BALANCE = STOCK_BALANCE - " +
    command[2] + " WHERE USER_ID = 1 AND STOCK_SYMBOL = '" +
    ticker + "';")
    db.execute("UPDATE USERS SET USD_BALANCE = " + str(new_bal) +
    " WHERE ID = 1;")
    db.commit()

    cursor.execute("SELECT STOCK_BALANCE FROM STOCKS WHERE " +
    "USER_ID = 1 AND STOCK_SYMBOL = '" + ticker + "';")
    result = cursor.fetchone()

    sock.send("{}".format(
        "200 OK\nSOLD: New balance: " + str(result[0]) + " " + ticker +
        ". USD balance " + str(new_bal)
    ))

def bal_command(sock, db, command):
    cursor = db.cursor()
    cursor.execute("""SELECT FIRST_NAME, LAST_NAME,
    USD_BALANCE FROM USERS WHERE ID = 1;""")
    result = cursor.fetchone()
    name = result[0] + " " + result[1]
    bal = format(result[2], ".2f")

    sock.send("{}".format(
        "200 OK\nBalance for user " + name + ": " + bal
    ))

def list_command(sock, db, command):
    cursor = db.cursor()
    for row in cursor.execute(""" SELECT ID,STOCK_SYMBOL,STOCK_BALANCE,USER_ID FROM STOCKS """):
        Stock=result[0]+" "+result[1]+" "+result[2]
        User=result[3]
        sock.send("{}".format(
        "200 OK\n The list of records in the Stocks database for user 1: " + Stock + ": " + User
    ))

def start_server():
    # Create database connection and tables
    conn = sqlite3.connect("trading.db")
    print("CONNECTED TO DATABASE")

    # DELETE THIS WHEN EVERTHING WORKS THIS RESETS THE DB
    # conn.execute("DROP TABLE IF EXISTS USERS;")
    # conn.execute("DROP TABLE IF EXISTS STOCKS;")
    # conn.commit()
    # DELETE THE ABOVE WHEN EVERYTHING WORKS THIS RESETS THE DB

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

    # Check if USERS is empty and add user if so
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
                elif words[0] == "SHUTDOWN":
                    client_socket.send("{}".format(
                        "200 OK"
                    ))
                    break
            else:
                client_socket.send("{}".format(
                    "INVALID COMMAND CHECK INPUT"  # FIX THIS!!!
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
