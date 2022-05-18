"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from datetime import datetime
from socket import socket


class Message:
    """Message Type."""
    def __init__(self, msg: str):
         self.data = msg
    
    def __str__(self):
        return json.dumps(self.data)
    
class JoinMessage(Message):
    """Message to join a chat channel."""
    def __init__(self, channel: str):
        data = {"command": "join", "channel": channel}
        super().__init__(data)
    
class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self, user: str):
        data = {"command": "register", "user": user}
        super().__init__(data)

    
class TextMessage(Message):
    """Message to chat with other clients."""
    def __init__(self, msg: str, channel: str = None):
        data = {"command": "message", "message": msg, "ts": round(datetime.today().timestamp())}
        if channel:
            data["channel"] = channel
        super().__init__(data)


class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        return RegisterMessage(username)

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        return JoinMessage(channel)

    @classmethod
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        return TextMessage(message, channel)

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        msgBytes = json.dumps(msg.data).encode('utf-8')
        lenBytes = len(msgBytes).to_bytes(2, 'big')
        connection.sendall(lenBytes + msgBytes)

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        try:
            num = int.from_bytes(connection.recv(2), 'big')
            data = json.loads(connection.recv(num).decode())

            command = data['command']
            if command == 'register':
                return RegisterMessage(data['user'])
            elif command == 'join':
                return JoinMessage(data['channel'])
            elif command == 'message':
                return TextMessage(data['message'])
            else:
                return Message(data)
        except Exception as e:
            raise CDProtoBadFormat(e)
            
class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")
