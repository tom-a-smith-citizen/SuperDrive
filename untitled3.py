# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 09:04:55 2024

@author: TOSmith
"""

import socket
import json
import time
import keyboard  # This library is used to simulate key presses
import select  # For checking if the socket has data to read

HOST = '10.10.78.10'
PORT = 8760

request_data = {
    'protocolVersion': '1',
    'endpoint': 'shots',
    'correlationId': '0'
}

previous_data = None
buffer_size = 4096

def check_and_press_spacebar(response_json):
    global previous_data

    if response_json == previous_data:
        return

    previous_data = response_json

    shots = response_json.get('shots', [])
    prepared_shot = next((shot for shot in shots if shot['type'] == 'prepared'), None)
    onair_shot = next((shot for shot in shots if shot['type'] == 'onair'), None)

    if prepared_shot and onair_shot:
        prepared_template = prepared_shot.get('templateName')
        print(prepared_template)
        onair_template = onair_shot.get('templateName')
        print(onair_template)

        if prepared_template == 'XPN1 MOS CG' and onair_template != 'XPN1 MOS CG':
            keyboard.press_and_release('space')

def receive_complete_json(sock):
    data = ""
    while True:
        ready = select.select([sock], [], [], 1.0)  # Wait for up to 1 second for data to be ready
        if ready[0]:
            part = sock.recv(buffer_size).decode('utf-8')
            if not part:
                break
            data += part

            try:
                return json.loads(data)
            except json.JSONDecodeError:
                continue
        else:
            break  # No more data to read

    return None

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            s.sendall(json.dumps(request_data).encode('utf-8'))

            response_json = receive_complete_json(s)

            if response_json:
                check_and_press_spacebar(response_json)

            time.sleep(0.5)

if __name__ == "__main__":
    main()

