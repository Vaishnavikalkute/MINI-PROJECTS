import socket
import threading

class RedisServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        # In-memory data storage
        self.data = {}
        # Setting up TCP connection request
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the specified host and port
        self.server_socket.bind((self.host, self.port))
        # Allow the server to accept connections, with a queue of up to 5 pending connections
        self.server_socket.listen(5)
        print(f"Listening on {self.host}:{self.port}")

    def start(self):
        # Keep the server active to accept connections
        while True:
            # Accept a new connection request
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address}")
            # Handle the new connection in a separate thread
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        # Automatically close the connection when done
        with client_socket:
            while True:
                # Receive data from the client
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                # Process the command and send a response back to the client
                response = self.process_command(data.strip())
                client_socket.sendall(response.encode())

    def process_command(self, command):
        parts = command.split()
        cmd = parts[0].upper()

        if cmd == "SET" and len(parts) == 3:
            self.data[parts[1]] = parts[2]
            return "OK"
        elif cmd == "GET" and len(parts) == 2:
            return self.data.get(parts[1], "None")
        elif cmd == "DEL" and len(parts) == 2:
            if parts[1] in self.data:
                del self.data[parts[1]]
                return "OK"
            else:
                return "Key does not exist"
        else:
            return "ERR unknown command"

if __name__ == "__main__":
    server = RedisServer()
    server.start()
