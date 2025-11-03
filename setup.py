# setup.py
import subprocess
import time
import sys
import os
from threading import Thread

def run_command_in_terminal(command):
    """Run a command in a new terminal window"""
    if sys.platform == "win32":
        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
    elif sys.platform == "darwin":  # macOS
        subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "{command}"'])
    else:  # Linux
        subprocess.Popen(['xterm', '-e', command])

def main():
    print("Setting up Simple Onion Network...")
    
    # Create directories if needed
    os.makedirs('logs', exist_ok=True)
    
    commands = [
        "python directory_server.py",
        "python relay_node.py relay1", 
        "python relay_node.py relay2",
        "python relay_node.py relay3",
        "python socks_proxy.py",
        "python client.py"
    ]
    
    print("Starting services...")
    
    # Start directory server first
    print("1. Starting Directory Server...")
    subprocess.Popen(['python', 'directory_server.py'])
    time.sleep(2)
    
    # Start relays
    for i in range(1, 4):
        print(f"{i+1}. Starting Relay {i}...")
        subprocess.Popen(['python', 'relay_node.py', f'relay{i}'])
        time.sleep(1)
    
    time.sleep(3)  # Wait for relays to register
    
    # Start SOCKS proxy
    print("5. Starting SOCKS5 Proxy...")
    subprocess.Popen(['python', 'socks_proxy.py'])
    time.sleep(2)
    
    print("\nSetup complete!")
    print("You can now:")
    print("1. Run 'python client.py' to test the onion network")
    print("2. Configure applications to use SOCKS5 proxy at localhost:1080")
    print("3. Or run the test script: python test_onion.py")

if __name__ == "__main__":
    main()