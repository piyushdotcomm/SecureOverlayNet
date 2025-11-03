import socket
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Client")

class OnionClient:
    def __init__(self, directory_host='localhost', directory_port=9000):
        self.directory_host = directory_host
        self.directory_port = directory_port
        self.relays = []
        
    def get_relays_from_directory(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.directory_host, self.directory_port))
                request = {'command': 'GET_RELAYS'}
                sock.send(json.dumps(request).encode('utf-8'))
                response = json.loads(sock.recv(4096).decode('utf-8'))
                
                if response['status'] == 'success':
                    self.relays = response['relays']
                    logger.info(f"Got {len(self.relays)} relays")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error getting relays: {e}")
            return False
    
    def create_onion_route(self, message):
        if not self.relays:
            if not self.get_relays_from_directory():
                raise Exception("No relays available")
        
        relays_to_use = self.relays[:3]  # Use 3 relays
        
        logger.info(f"Creating route through {len(relays_to_use)} relays")
        
        # Build from last to first
        current_payload = {'type': 'final', 'message': message}
        
        for i in range(len(relays_to_use)-1, -1, -1):
            if i == len(relays_to_use)-1:
                # Last relay
                current_payload = {
                    'type': 'final',
                    'message': message
                }
            else:
                # Intermediate relay
                next_relay = relays_to_use[i+1]
                current_payload = {
                    'type': 'onion', 
                    'next_hop': {
                        'host': next_relay['host'],
                        'port': next_relay['port']
                    },
                    'payload': current_payload
                }
        
        return json.dumps(current_payload).encode('utf-8'), relays_to_use[0]
    
    def send_message(self, message):
        try:
            encrypted_payload, first_relay = self.create_onion_route(message)
            
            logger.info(f"Sending via {first_relay['host']}:{first_relay['port']}")
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((first_relay['host'], first_relay['port']))
                sock.send(encrypted_payload)
                
                response = sock.recv(4096).decode('utf-8')
                return response
                
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

def main():
    client = OnionClient()
    
    print("Simple Onion Routing Client")
    print("Type 'quit' to exit")
    
    while True:
        message = input("Enter message: ")
        if message.lower() == 'quit':
            break
            
        response = client.send_message(message)
        print(f"Response: {response}")

if __name__ == "__main__":
    main()