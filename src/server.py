"""CD Chat server program."""
import logging
import socket
import threading
from queue import Queue

from .protocol import CDProto, CDProtoBadFormat

logging.basicConfig(filename="server.log", level=logging.DEBUG, filemode='w')
class Server:
    def __init__(self, host='localhost', port=1234):
        self._host = host 
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self._host, self.port))
        self.sock.listen(100)
        self.channels = { 'general': [] }       #we will save all the clients that participate in each channel here
        self.clients_channels = {}              #we will save client: [list with all the channels that client participate] here
    
    def process_join(self, msg, client): 
        channel = msg.data['channel']
       
        if channel not in self.channels:
            self.channels[channel] = [ client ]     #we add the channel and associate the client
        else:
            self.channels[channel].append(client)   
         
        if channel not in self.clients_channels[client]:
            self.clients_channels[client].append(channel)   
        else:
            self.clients_channels[client].remove(channel)
            self.clients_channels[client].append(channel)   #we need to remove and add again for the most recent join stay in last index
       
        
    def process_message(self, msg, client):
        channel = self.clients_channels[client][-1]        #we need send the message for the last channel that this client joined

        for conn in self.channels[channel]:     #we will send the message for all clients of the channel - requirement 5 and 3
            self.protocol.send_msg(conn, msg)
            logging.debug("Sent '%s' to %s", msg, conn.getpeername())

    def process_command(self, msg, client):     #we will check type of message
        command = msg.data['command']
        if command == 'join':
            self.process_join(msg, client)
        
        if command == 'message':
            self.process_message(msg, client)
    
    def close_connection(self, client):
        for ch in self.clients_channels[client]:    #we will check all channels that this client participate for remove him
            self.channels[ch].remove(client)
            
        del self.clients_channels[client]       #we delete this client from channels information, as the next messages will not be send to him 
        
    def read_message(self, client, address):
        self.protocol = CDProto()
        while True:
            try:
                msg = self.protocol.recv_msg(client)
                logging.debug("Received: %s", msg.data)
                if msg:
                    self.process_command(msg, client)
            except:
                self.close_connection(client)
                return False
            
    def loop(self):
        while True:
            client, address = self.sock.accept()
            logging.debug('Connection established with %s', address)
            self.channels['general'].append(client)     #when client signs up, he will join to channel general
            self.clients_channels[client] = ['general']     #when client signs up, we add pair client-general
            threading.Thread(target = self.read_message, args = (client, address)).start()
