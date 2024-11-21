#!/bin/python3

"""
This module starts a server that listens for connections from ChristmasTreeClient.
"""

import socket

import time
from christmas_tree_client import ChristmasTreeClient


def start_server():
    """
    Start the server that listens for connections from ChristmasTreeClient.
    """
    bind_ip = "0.0.0.0"
    bind_port = 3355

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # resuse the socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)

    print(f"Binding to {bind_ip}:{bind_port}")
    while True:
        try:
            server.bind((bind_ip, bind_port))
            break
        except OSError as e:
            if e.errno == 98:
                print(f"Port {bind_port} is already in use. Await 1 second before retrying.")
                time.sleep(1)
            else:
                raise e

    server.listen()

    while True:
        client, address = server.accept()
        print(f"Accepted connection from {address}")
        client_handler = ChristmasTreeClient(client)
        client_handler.start()


if __name__ == "__main__":
    start_server()
