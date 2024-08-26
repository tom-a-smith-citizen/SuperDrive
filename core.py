# -*- coding: utf-8 -*-
"""
SuperDrive 0.1
Created on Thu Aug 22 06:17:35 2024

@author: TOSmith
"""

import socket, json, keyboard, time, threading

class OnAir(object):
    def __init__(self, parent, _index, slug, shot_name, template_name, transition_name):
        self.parent = parent
        self._index = _index
        self.slug = slug
        self.shot_name = shot_name
        self.template_name = template_name
        self.transition_name = transition_name
        self.is_super = self.super_check(self.template_name)
        
    def super_check(self,template_name):
        if template_name == self.parent.super_keyword:
            return True
        return False
    
class Prepared(object):
    def __init__(self, parent, _index, slug, shot_name, template_name, transition_name):
        self.parent = parent
        self._index = _index
        self.slug = slug
        self.shot_name = shot_name
        self.template_name = template_name
        self.transition_name = transition_name
        self.is_super = self.super_check(self.template_name)
        
    def super_check(self,template_name):
        if template_name == "XPN 1 MOS CG":
            return True
        return False
    
class Listener(threading.Thread):
    def __init__(self, parent, connection_info: tuple, super_keyword: str, advance_key: str):
        threading.Thread.__init__(self)
        self.parent = parent
        self.OverDrive_IP = connection_info[0]
        self.OverDrive_port = connection_info[1]
        self.request = {'protocolVersion': '1',
                                  'endpoint': 'shots',
                                  'correlationId': '0'
                                  }
        self.listening = False
        self.previous_data = None
        self.super_keyword = super_keyword
        self.advance_key = advance_key
        
    def run(self):
        self.listening = True
        self.parent.statusbar.SetStatusText("SuperDrive is active.",0)
        self.prepared_olv = []
        self.on_air_olv = []
        self.parent.set_columns()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            try:
                s.connect((self.OverDrive_IP, self.OverDrive_port))
                
                while self.listening:
                    # Send the request
                    s.sendall(bytearray(json.dumps(self.request), 'UTF-8'))
                    
                    # Listen for incoming data
                    data = s.recv(1024)
                    
                    if not data:
                        print("Connection closed by the server.")
                        break  # Exit the loop if the connection is closed

                    try:
                        # Convert the received data to JSON
                        json_data = json.loads(data.decode('UTF-8'))
                        
                        # Check if the "shots" key is in the JSON
                        if 'shots' in json_data:
                            current_data = json_data['shots']
                            
                            # Compare with the previous data and print if different
                            if current_data != self.previous_data:
                                print(current_data)
                                on_air = OnAir(self,_index=str(current_data[0]['index']),
                                               slug=str(current_data[0]['slug']),
                                               shot_name=str(current_data[0]['shotName']),
                                               template_name=str(current_data[0]['templateName']),
                                               transition_name=str(current_data[0]['transitionName']))
                                self.on_air_olv.append(on_air)
                                prepared = Prepared(self,_index=str(current_data[1]['index']),
                                               slug=str(current_data[1]['slug']),
                                               shot_name=str(current_data[1]['shotName']),
                                               template_name=str(current_data[1]['templateName']),
                                               transition_name=str(current_data[1]['transitionName']))
                                self.prepared_olv.append(prepared)
                                self.previous_data = current_data  # Update the previous data
                                self.parent.olv_preview.SetObjects(self.prepared_olv)
                                self.parent.olv_program.SetObjects(self.on_air_olv)
                                if prepared.is_super and not on_air.is_super:
                                    keyboard.press_and_release(self.advance_key)
                                    print('Playing super.')
                                    self.parent.statusbar.SetStatusText('Playing super.',1)
                                else:
                                    self.parent.statusbar.SetStatusText('',1)

                    except json.JSONDecodeError:
                        pass

                self.parent.statusbar.SetStatusText("SuperDrive is not active.",0)

            except socket.error as e:
                print(f"Socket error: {e}")
                
                s.close()
                print('Socket closed.')
                
class Receiver(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = self.parent.superdrive_port
        self.running = True

    def run(self):
        # Set up the socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Listening for incoming data on {self.host}:{self.port}...")

            while self.running:
                client_socket, addr = server_socket.accept()
                with client_socket:
                    print(f"Connection established with {addr}")
                    while self.running:
                        data = client_socket.recv(1024)  # Adjust buffer size as needed
                        data = data.decode('utf-8')
                        print(data)
                        if not data:
                            break
                        if data == 'START':
                            self.parent.on_remote_start()
                        elif data == 'STOP':
                            self.parent.overdrive.listening = False

    def stop(self):
        self.running = False