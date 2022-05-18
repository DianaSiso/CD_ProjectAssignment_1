"""CD Chat client program"""
import logging
import sys
import os
import socket
import threading

from .protocol import CDProto, CDProtoBadFormat

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG, filemode='w')


class Client:
    
    def __init__(self, name: str = "Foo", host: str = 'localhost', port: int = 1234):
        self.name = name
        self._host = host
        self.port = port
        self.sock = socket.socket()
        self.protocol = CDProto()


    def connect(self):
        self.sock.connect((self._host, self.port))
        logging.info(f'Connection established with {self._host}:{self.port}')
        
        msg = self.protocol.register(self.name)     #the first message must be the registration message, so we send this message when client connects
        self.protocol.send_msg(self.sock, msg)      

    def read_message(self):
        while True:
            msg = self.protocol.recv_msg(self.sock)
            logging.debug("Received: %s", msg.data)     
            logging.info(msg.data['message'])       #requirement 10
            print(msg.data['message'])
            
        
    def insert_command(self):
        while True:
            command = input()   #requirement 2
            msg = self.protocol.message(command)    #we first treat the message as a text message 

            #if the client just writes "/join" but he doesn't specify the channel, this message will be a text message
            if '/join' in command:
                try:
                    channel = command.split('/join ')[1]
                    msg = self.protocol.join(channel)       #the client writes a channel, so we change the message type to join message
                except:
                    logging.error("Channel not specified")
            
            #if the client writes "exit" we will end the process
            if command == 'exit':
                self.sock.close()
                os._exit(0)
            
            self.protocol.send_msg(self.sock, msg)
            logging.debug("Sent: %s", msg.data)

    def loop(self):
        #we will use threads, so requirement 4 is not a problem
        self.t1 = threading.Thread(target = self.read_message)        #this thread will read the messages receveid 
        self.t2 = threading.Thread(target = self.insert_command)      #this thread will read the command to choose if is a join message or text message and send the message - requirement 6
        self.t1.start()
        self.t2.start()