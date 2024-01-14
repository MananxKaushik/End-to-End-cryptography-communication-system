import socket
import threading
from cryptography.fernet import Fernet
def generate_key():
    return Fernet.generate_key()
def encrypt_message(key, message):
    fernet = Fernet(key)
    return fernet.encrypt(message.encode())

def decrypt_message(key, encrypted_message):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_message).decode()
class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.key = generate_key()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()
            self.clients.append((client_socket, self.key))

    def handle_client(self, client_socket):
        try:
            while True:
                encrypted_message = client_socket.recv(1024)
                if not encrypted_message:
                    break

                sender_key = None
                for _, key in self.clients:
                    if client_socket in self.clients and client_socket == _:
                        sender_key = key

                if sender_key:
                    decrypted_message = decrypt_message(sender_key, encrypted_message)
                    print(f"Received: {decrypted_message}")

                for client, key in self.clients:
                    if client != client_socket:
                        client.send(encrypted_message)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.clients.remove((client_socket, self.key))
            client_socket.close()
class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.key = generate_key()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def send_message(self, message):
        encrypted_message = encrypt_message(self.key, message)
        self.client_socket.send(encrypted_message)

    def receive_messages(self):
        try:
            while True:
                encrypted_message = self.client_socket.recv(1024)
                if not encrypted_message:
                    break

                decrypted_message = decrypt_message(self.key, encrypted_message)
                print(f"Received: {decrypted_message}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()

if __name__ == '__main__':
    server = ChatServer('0.0.0.0', 12345)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    client = ChatClient('127.0.0.1', 12345)
    receive_thread = threading.Thread(target=client.receive_messages)
    receive_thread.start()

    while True:
        message = input("Type your message: ")
        client.send_message(message)
