#!/usr/bin/python3
"""
Program: Project 1 TCP client-server chat - chatserve.py.

Class: CS 372 - Intro To Networking
Author: KC
Date: July 27 2018
Description: chatserve.py is a chat server for chatclient.c, accepting incoming
connections while communicating with the client. After a connection is
established, strictly alternating messages can be sent and received from UI.
Sources Used: CS 372 lecture 15 slide 9 "Example application: TCP server"
"""
import sys
import threading
import socket
from signal import signal, SIGINT

MAX_SIZE = 500

STOP_SIGNAL = False
GOT_CLIENT_INPUT = False
SOCKET_LIST: list = []


def main():
    """Run server and accept new client connections.

    Close if a connections if initiations fails or the continue state is false.
    """
    server_socket = start_up()
    while 1:
        global STOP_SIGNAL
        STOP_SIGNAL = False
        global GOT_CLIENT_INPUT
        GOT_CLIENT_INPUT = False

        # Open a new connection socket
        cxn_socket, addr = server_socket.accept()

        # Initial messaging transaction with client
        cxn_status = initiate_contact(cxn_socket)
        register_socket(cxn_socket)

        # Loop until receive '\quit' from user or client
        if cxn_status == 1:
            args_tuple = (cxn_socket,)

            # Create threads
            thread_recv = threading.Thread(target=recv_msg, args=args_tuple)
            thread_send = threading.Thread(target=send_msg, args=args_tuple)

            # Put thread in bg to allow signal to kill all threads
            thread_recv.daemon = True
            thread_send.daemon = True

            # Get msg from user and send to client
            thread_recv.start()
            thread_send.start()

            # Wait for threads to complete
            thread_recv.join()
            thread_send.join()

        # Close the connection with the client
        cxn_socket.close()
        deregister_socket(cxn_socket)


def register_socket(cxn_socket):
    """Resister socket.

    Maintains a list of sockets currently open
    """
    found = False
    for i in SOCKET_LIST:
        if i == cxn_socket:
            found = True

    if found is False:
        SOCKET_LIST.append(cxn_socket)
        return 0

    return 1


def deregister_socket(cxn_socket):
    """Deregister socket.

    Removes socket from list of open sockets
    """
    for i in SOCKET_LIST:
        if i == cxn_socket:
            SOCKET_LIST.remove(cxn_socket)
            return 0

    return 1


def start_up():
    """Server socket start up.

    Description: Standard socket initializion procedure, creates a TCP
    socket on port from command line. Listens for incoming client
    connections.
    """
    incoming_ip = '0.0.0.0'  # Allows server to bind to any incoming IP
    server_port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((incoming_ip, server_port))
    server_socket.listen(1)
    print("The server is up.")
    print("- enter '\\quit' to end session with client")
    print("- ctrl-C to exit server application")
    print("Waiting for client connections...")
    return server_socket


def recv_msg(cxn_socket):
    r"""Receive message from client.

    Description: Gets msg from client thorugh TCP socket. If client sent
    '\quit' then return 0 and print termination msg. Otherwise return 1 and
    print client msg.
    """
    global STOP_SIGNAL
    global GOT_CLIENT_INPUT
    while not STOP_SIGNAL:
        # Get client message and display to user
        GOT_CLIENT_INPUT = False
        byte_client_msg = cxn_socket.recv(MAX_SIZE)
        GOT_CLIENT_INPUT = True
        string_client_msg = byte_client_msg.decode('ASCII')

        # If client sends quit, print message and return 0
        if string_client_msg == r'\quit':
            print("Client session terminated by client")
            STOP_SIGNAL = True

        # Otherwise execute normally and print client message
        else:
            print("")
            print('{}'.format(string_client_msg))
            sys.stdout.flush()

    return 0


def send_msg(cxn_socket):
    r"""Get msg from user and send to client.

    Description: Get user input. If '\quit', print termination msg, send to
    client and return 0. Otherwise send msg to client and return 1.
    """
    global STOP_SIGNAL
    global GOT_CLIENT_INPUT

    while not STOP_SIGNAL:
        string_server_msg = input('\nserverH> ')

        if string_server_msg == r'\quit':
            print("Client session terminated by server")
            STOP_SIGNAL = True

        elif len(string_server_msg) == 0:
            string_server_msg = "  "

        byte_server_msg = string_server_msg.encode('ASCII')
        cxn_socket.send(byte_server_msg)

    return 0


def initiate_contact(cxn_socket):
    """Initialize messaging transaction with client.

    Description: Get initial msg from client. If client sent "CXN_C", send
    "CXN_S" and return 1 to continue the chat session.
    """
    cxn_msg = cxn_socket.recv(MAX_SIZE)
    string_cxn_msg = cxn_msg.decode('ASCII')
    # If recv proper msg, send handshake message to client
    if string_cxn_msg == 'CXN_C':
        print('Initial msg from client: {}'.format(string_cxn_msg))
        byte_serv_cxn_msg = b'CXN_S'
        cxn_socket.send(byte_serv_cxn_msg)
        return 1
    return 0


def exit_handler(signum, frame):
    """Handle signal for exiting program.

    Exits program after closing socket
    """
    global STOP_SIGNAL
    STOP_SIGNAL = True

    # Close open sockets and send '\quit' message to client
    msg = r'\quit'
    byte_msg = msg.encode('ASCII')
    for i in SOCKET_LIST:
        i.send(byte_msg)
        i.close()

    print("\nServer shutting down...goodbye.")
    sys.exit(0)


if __name__ == "__main__":
    signal(SIGINT, exit_handler)
    main()
