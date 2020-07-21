"""
This module contains all messages that will be sent between Master and Slaves to establish connection and etc.
"""


class ClientMessages:
    GREET_SERVER = b'Request for connection'
    SEND_DATA_REQUEST = b'Ready to receive data'
    READY = b'Ready'


class ServerMessages:
    GREET_CLIENT = b'Connection established'
