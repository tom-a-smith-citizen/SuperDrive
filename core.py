# -*- coding: utf-8 -*-
"""
SuperDrive 0.1
Created on Thu Aug 22 06:17:35 2024

@author: TOSmith
"""

import socket, json, keyboard, time, threading

class OnAir(object):
    def __init__(self, _index, slug, shot_name, template_name, transition_name):
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
    
class Prepared(object):
    def __init__(self, _index, slug, shot_name, template_name, transition_name):
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
    def __init__(self, parent, connection_info: tuple):
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
        
    def run(self):
        self.listening = True
        self.parent.statusbar.SetStatusText("SuperDrive is active.",0)
        self.prepared_olv = []
        self.on_air_olv = []
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
                                on_air = OnAir(_index=current_data[0]['index'],
                                               slug=current_data[0]['slug'],
                                               shot_name=current_data[0]['shotName'],
                                               template_name=current_data[0]['templateName'],
                                               transition_name=current_data[0]['transitionName'])
                                self.on_air_olv.append(on_air)
                                prepared = Prepared(_index=current_data[1]['index'],
                                               slug=current_data[1]['slug'],
                                               shot_name=current_data[1]['shotName'],
                                               template_name=current_data[1]['templateName'],
                                               transition_name=current_data[1]['transitionName'])
                                self.prepared_olv.append(prepared)
                                self.previous_data = current_data  # Update the previous data
                                self.parent.set_columns()
                                if prepared.is_super and not on_air.is_super:
                                    keyboard.press_and_release('space')
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