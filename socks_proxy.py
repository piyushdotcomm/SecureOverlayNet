# socks_proxy.py
import socket
import threading
import logging
from client import OnionClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SOCKS5Proxy")

class SOCKS5Proxy:
    def __init__(self, host='localhost', port=1080):
        self.host = host
        self.port = port
        self.onion_client = OnionClient()
    
    def handle_client(self, conn, addr):
        """Handle SOCKS5 client connection"""
        try:
            logger.info(f"New SOCKS5 connection from {addr}")
            
            # SOCKS5 handshake
            version = conn.recv(1)
            if version != b'\x05':
                conn.close()
                return
            
            nmethods = conn.recv(1)[0]
            methods = conn.recv(nmethods)
            
            # Accept no authentication
            conn.send(b'\x05\x00')
            
            # Read request
            request = conn.recv(4)
            if len(request) < 4:
                conn.close()
                return
                
            version, cmd, rsv, atyp = request
            if version != 5 or cmd != 1:  # Only support CONNECT command
                conn.close()
                return
            
            if atyp == 1:  # IPv4
                dest_addr = socket.inet_ntoa(conn.recv(4))
            elif atyp == 3:  # Domain name
                domain_length = conn.recv(1)[0]
                dest_addr = conn.recv(domain_length).decode('utf-8')
            else:
                conn.close()
                return
            
            dest_port = int.from_bytes(conn.recv(2), 'big')
            
            logger.info(f"SOCKS5 request: {dest_addr}:{dest_port}")
            
            # Send success response (simplified)
            conn.send(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
            
            # Tunnel data through onion network
            self.tunnel_data(conn, dest_addr, dest_port)
            
        except Exception as e:
            logger.error(f"Error handling SOCKS5 client: {e}")
            conn.close()
    
    def tunnel_data(self, client_conn, dest_addr, dest_port):
        """Tunnel data through onion network"""
        try:
            # For simplicity, we'll create a mock HTTP request through onion
            # In a real implementation, you'd properly handle the protocol
            
            http_request = f"GET / HTTP/1.1\r\nHost: {dest_addr}:{dest_port}\r\n\r\n"
            
            # Send through onion network
            response = self.onion_client.send_message(f"PROXY:{dest_addr}:{dest_port}:{http_request}")
            
            # Send response back to client
            client_conn.send(response)
            
        except Exception as e:
            logger.error(f"Tunneling error: {e}")
        finally:
            client_conn.close()
    
    def start(self):
        """Start the SOCKS5 proxy server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            logger.info(f"SOCKS5 proxy listening on {self.host}:{self.port}")
            
            while True:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()

if __name__ == "__main__":
    proxy = SOCKS5Proxy()
    proxy.start()