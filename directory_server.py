# directory_server.py
import socket
import threading
import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DirectoryServer")

class DirectoryServer:
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        self.relays: Dict[str, dict] = {}  # relay_id -> relay_info
        self.lock = threading.Lock()
        
    def handle_client(self, conn, addr):
        """Handle requests from clients or relays"""
        try:
            data = conn.recv(4096).decode('utf-8')
            if not data:
                return
                
            request = json.loads(data)
            command = request.get('command')
            
            if command == 'REGISTER_RELAY':
                relay_id = request['relay_id']
                relay_info = {
                    'host': request['host'],
                    'port': request['port'],
                    'public_key': request.get('public_key', 'dummy_key')
                }
                
                with self.lock:
                    self.relays[relay_id] = relay_info
                    logger.info(f"Registered relay {relay_id} at {relay_info['host']}:{relay_info['port']}")
                
                response = {'status': 'success', 'message': f'Relay {relay_id} registered'}
                conn.send(json.dumps(response).encode('utf-8'))
                
            elif command == 'GET_RELAYS':
                with self.lock:
                    relay_list = list(self.relays.values())
                
                response = {'status': 'success', 'relays': relay_list}
                conn.send(json.dumps(response).encode('utf-8'))
                logger.info(f"Sent {len(relay_list)} relays to {addr}")
                
            else:
                response = {'status': 'error', 'message': 'Unknown command'}
                conn.send(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
        finally:
            conn.close()
    
    def start(self):
        """Start the directory server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            logger.info(f"Directory server listening on {self.host}:{self.port}")
            
            while True:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()

if __name__ == "__main__":
    server = DirectoryServer()
    server.start()