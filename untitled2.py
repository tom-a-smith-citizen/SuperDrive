# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 08:41:28 2024

@author: TOSmith
"""

import socket, json
from json_repair import repair_json

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.connect(('10.10.78.10', 8760))
    '''
    request = {'protocolVersion': '1',
               'endpoint': 'subscription',
               'reqData': 'type=optOut',
               'correlationId': '1000001'
               }
    s.sendall(bytearray(json.dumps(request), 'UTF-8'))
    data = s.recv(4096)
    print(data)
    '''
    request = {'protocolVersion': '1',
                              'endpoint': 'shots',
                              'correlationId': '0'
                              }
    s.sendall(bytearray(json.dumps(request), 'UTF-8'))
    while True:
        # Listen for incoming data
        data = s.recv(4096)
        
        if not data:
            print("Connection closed by the server.")
            break  # Exit the loop if the connection is closed
        
        else:
            decoded = data.decode('UTF-8')
            try:
                jsonified = json.loads(data)
            except json.JSONDecodeError:
                jsonified = repair_json(data)
            if 'shots' in jsonified:
                print(jsonified)