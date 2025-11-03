Simple Onion Network
A minimal implementation of onion routing with layered encryption, SOCKS5 proxy support, and local testing.

Quick Start
Install dependencies:

bash
pip install cryptography
Run automated setup:

bash
python setup.py
Manual Setup
Terminal 1 - Directory Server:

bash
python directory_server.py
Terminals 2-4 - Relay Nodes:

bash
python relay_node.py relay1
python relay_node.py relay2  
python relay_node.py relay3
Terminal 5 - SOCKS5 Proxy:

bash
python socks_proxy.py
Terminal 6 - Test:

bash
python client.py
# or
python test_onion.py
Usage
Interactive Client
bash
python client.py
SOCKS5 Proxy
Configure apps to use:

Host: localhost

Port: 1080

Type: SOCKS5

Example:

bash
curl --socks5 localhost:1080 http://example.com
Architecture
text
App → SOCKS5 Proxy → Client → Relay1 → Relay2 → Relay3 → Destination
                      ↑
               Directory Server
Components
directory_server.py - Relay registry (port 9000)

relay_node.py - Traffic forwarding nodes

client.py - Onion route builder

socks_proxy.py - SOCKS5 interface (port 1080)

setup.py - Auto-start all services

test_onion.py - Verification tests

Features
3-hop onion routing with layered encryption

SOCKS5 proxy for application tunneling

Localhost testing with automatic relay discovery

Simple Fernet encryption between hops

Educational Use Only - Not for production privacy protection