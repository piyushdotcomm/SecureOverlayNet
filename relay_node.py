import socket
import threading
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class RelayNode:
    def __init__(self, relay_id, host='localhost', port=0, directory_host='localhost', directory_port=9000):
        self.relay_id = relay_id
        self.host = host
        self.port = port
        self.directory_host = directory_host
        self.directory_port = directory_port
        self.logger = logging.getLogger(f"Relay-{relay_id}")
        
    def register_with_directory(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.directory_host, self.directory_port))
                request = {
                    'command': 'REGISTER_RELAY',
                    'relay_id': self.relay_id,
                    'host': self.host,
                    'port': self.port,
                    'public_key': 'simple_key'
                }
                sock.send(json.dumps(request).encode('utf-8'))
                response = json.loads(sock.recv(4096).decode('utf-8'))
                self.logger.info(f"Registered: {response}")
        except Exception as e:
            self.logger.error(f"Registration failed: {e}")
    
    def handle_client(self, conn, addr):
        try:
            data = conn.recv(4096).decode('utf-8')
            if not data:
                return
            
            message = json.loads(data)
            
            if message.get('type') == 'onion':
                # Forward to next relay
                next_hop = message['next_hop']
                payload = message['payload']
                
                self.logger.info(f"Forwarding to {next_hop['host']}:{next_hop['port']}")
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as next_sock:
                    next_sock.connect((next_hop['host'], next_hop['port']))
                    next_sock.send(json.dumps(payload).encode('utf-8'))
                    
                    response = next_sock.recv(4096).decode('utf-8')
                    conn.send(response.encode('utf-8'))
                    
            else:
                # Final destination - echo the message
                response_data = f"Relay {self.relay_id} received: {message['message']}"
                conn.send(response_data.encode('utf-8'))
                
        except Exception as e:
            self.logger.error(f"Error: {e}")
            conn.send(f"Error: {e}".encode('utf-8'))
        finally:
            conn.close()
    
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.port = server_socket.getsockname()[1]
            self.logger.info(f"Relay {self.relay_id} on {self.host}:{self.port}")
            
            self.register_with_directory()
            
            while True:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()

if __name__ == "__main__":
    import sys
    relay_id = sys.argv[1]
    relay = RelayNode(relay_id)
    relay.start()