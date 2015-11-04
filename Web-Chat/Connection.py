import socket

class Connection:
    """Wraps the socket object and contains an ignore list and username"""
    def __init__(self, s):
        self.sock = s
        self.ignore_list = []
        self.username = ""


