import socket
import threading


class redisServers():
    def __init__(self,host='127.0.0.1',port=5000):
        self.host=host
        self.port=port
        # setup in machine data storage
        self.data={}
        # setting up tcp connection request
        self.server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # make connection to the specified port
        self.server_socket.bind(self.host,self.port)
        self.server_socket.listen(5)

    def start(self):
        # handle the connection start
        pass
if __name__ == "__main__":
    server=redisServers()
    server.start()