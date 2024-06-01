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
        # only 5 pending connection are accepted to stay in queue
        self.server_socket.listen(5)

    def start(self):
        # purpose of while true is to keep our server active 
        # accept will ne on stand by until new connection request is coming
        while True:
            # handle the connection start
            # accept method will accept the connection request and return the new socket and client addresss
            client_server,addres=self.server_socket.accept()
            # make the new socket run on new thread 
            threading.Thread(target=self.handle_client,args=(client_server,)).start()

    def handle_client(self,client_server):
        # with will make to close the connection after the process 
        with client_server:
            # run the loop until client_server is connected
            while True:
                # condiiton to check the data from client
                data=client_server.recv(1024).decode()
                if not data():
                    break
                # condition to prcess data and send i back to client
            

    def process_command(self,command):
        pass


        
if __name__ == "__main__":
    server=redisServers()
    server.start()