import socket

def send_command(command):
    host = '127.0.0.1'  # The server's hostname or IP address
    port = 5000         # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode())
        response = s.recv(1024).decode()
        print(f"Response: {response}")

if __name__ == "__main__":
    # Test SET command
    send_command("SET key1 value1")

    # Test GET command
    send_command("GET key1")

    # Test DEL command
    send_command("DEL key1")

    # Test GET command for a non-existent key
    send_command("GET key1")

    # Test unknown command
    send_command("UNKNOWN key1 value1")
