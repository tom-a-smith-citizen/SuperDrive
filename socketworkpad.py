# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 06:39:09 2024

@author: TOSmith
"""

import socket, time, json, struct, ast
import json_repair

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    previous_data = None
    #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    correlation_id = 0
    s.connect(('10.10.78.10',8760))
    request = {'protocolVersion': '1',
               'endpoint': 'subscription',
               'reqData': 'type=optOut',
               'correlationId': '1000001'
               }
    s.sendall(bytearray(json.dumps(request), 'UTF-8'))
    data = s.recv(4096)
    print(data)
    
    while True:
        
        request = {'protocolVersion': '1',
                              'endpoint': 'shots',
                              'correlationId': str(correlation_id)
                              }
        s.sendall(bytearray(json.dumps(request), 'UTF-8'))
        data = s.recv(4096)
        if not data:
            print("Connection closed by the server.")
            break  # Exit the loop if the connection is closed
        try:
            _input = data.decode('UTF-8')
            if "shots" in _input:
                current_data = json_repair.loads(_input)
                current_data = current_data['shots']
                if previous_data != current_data:
                    print(current_data)
                    previous_data = current_data
        except Exception as e:
            print(f'Invalid JSON syntax: {e}')
            break
        if correlation_id == 10000:
            correlation_id = 0
        else:
            correlation_id += 1
