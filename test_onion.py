# test_onion.py
import time
from client import OnionClient

def test_onion_network():
    print("Testing Onion Network...")
    client = OnionClient()
    
    # Test messages
    test_messages = [
        "Hello, Onion Network!",
        "This is a secret message",
        "Test message 3"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: Sending '{message}'")
        response = client.send_message(message)
        print(f"Response: {response.decode('utf-8')}")
        time.sleep(1)

if __name__ == "__main__":
    test_onion_network()