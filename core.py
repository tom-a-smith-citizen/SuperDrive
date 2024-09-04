# -*- coding: utf-8 -*-
"""
SuperDrive Core 1.0.3
Created on Thu Aug 22 06:17:35 2024

@author: TOSmith
"""

import socket, json, keyboard, time, threading
from json_repair import repair_json

class OnAir(object):
    def __init__(self, parent, _index, slug, shot_name, template_name, transition_name, auto_played):
        self.parent = parent
        self._index = _index
        self.slug = slug
        self.shot_name = shot_name
        self.template_name = template_name
        self.transition_name = transition_name
        self.is_super = self.super_check(self.template_name)
        self.auto_played = bool
    
    def __eq__(self, other):
        return self._index == other._index and self.slug == other.slug and self.shot_name == other.shot_name and self.template_name == other.template_name and self.transition_name == other.transition_name and self.is_super == other.is_super
    
    def __str__(self):
        return f"On Air: {self._index} \n {self.slug} \n {self.shot_name} \n {self.template_name} \n {self.transition_name}"
    
    def super_check(self,template_name):
        if template_name == self.parent.super_keyword:
            return True
        return False
    
class Prepared(object):
    def __init__(self, parent, _index, slug, shot_name, template_name, transition_name, auto_played):
        self.parent = parent
        self._index = _index
        self.slug = slug
        self.shot_name = shot_name
        self.template_name = template_name
        self.transition_name = transition_name
        self.is_super = self.super_check(self.template_name)
        self.auto_played = bool
      
    def __eq__(self, other):
        return self._index == other._index and self.slug == other.slug and self.shot_name == other.shot_name and self.template_name == other.template_name and self.transition_name == other.transition_name and self.is_super == other.is_super  
     
    def __str__(self):
        return f"Prepared: {self._index} \n {self.slug} \n {self.shot_name} \n {self.template_name} \n {self.transition_name}"   
     
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
        self.prepared = None
        self.on_air = None
    
    def validate_data(self, data):
        decoded = data.decode('UTF-8')
        try:
            jsonified = json.loads(decoded)
            if 'shots' in jsonified:
                return (True, jsonified)
            elif 'cues' in jsonified:
                return (False, None)
            return (False, None)
        except json.JSONDecodeError:
            self.parent.log.error(f'JSON Decode error: {decoded} \n Trying to repair.')
            try:
                jsonified = repair_json(decoded)
                jsonified = json.loads(jsonified)
                if 'shots' in jsonified:
                    return (True, jsonified)
                elif 'cues' in jsonified:
                    return (False, None)
                return (False, None)
            except Exception as e:
                self.parent.log.error(f"Couldn't repair JSON: {e}. Discarding.")
            return(False, None)
    
    def parse_data(self, data):
        prepared = data['shots'][1]
        on_air = data['shots'][0]
        prepared = Prepared(self,
                            _index = prepared['index'],
                            slug = prepared['slug'],
                            shot_name = prepared['shotName'],
                            template_name = prepared['templateName'],
                            transition_name = prepared['transitionName'],
                            auto_played = bool)
        on_air = OnAir(self,
                       _index = on_air['index'],
                       slug = on_air['slug'],
                       shot_name = on_air['shotName'],
                       template_name = on_air['templateName'],
                       transition_name = on_air['transitionName'],
                       auto_played = bool)
        return prepared, on_air
    
    def present_data(self, data):
        prepared = data[0]
        prepared_changed = False
        on_air = data[1]
        on_air_changed = False
        if self.first_pass:
            #Add the items to the lists for the OLV's
            self.prepared_olv.append(prepared)
            self.on_air_olv.append(on_air)
            
            #Set the mutables
            self.prepared = prepared
            self.on_air = on_air
            self.last_check = [prepared, on_air]
            
            #Add them to the log
            self.parent.log.info(prepared)
            self.parent.log.info(on_air)
            
            #Set the OLV's
            self.parent.olv_preview.SetObjects(self.prepared_olv)
            self.parent.olv_program.SetObjects(self.on_air_olv)
            
            #Set the first pass flag
            self.first_pass = False
        else:
            #Check if prepared or on air have changed
            if prepared != self.prepared:
                #Add the item to the list for the OLV
                self.prepared_olv.append(prepared)
                
                #Set the mutables
                self.prepared = prepared
                self.last_check[0] = prepared
                prepared_changed = True
                
                #Add to the log
                self.parent.log.info(prepared)
                
                #Refresh the OLV
                self.parent.olv_preview.SetObjects(self.prepared_olv)
                print(self.prepared)
            if on_air != self.on_air:
                #Add the item to the list for the OLV
                self.on_air_olv.append(on_air)
                
                #Set the mutables
                self.on_air = on_air
                self.last_check[1] = on_air
                on_air_changed = True
                
                #Add to the log
                self.parent.log.info(on_air)
                
                #Refresh the OLV
                self.parent.olv_program.SetObjects(self.on_air_olv)
                print(self.on_air)
            if prepared_changed or on_air_changed:
                print('Handling super')
                self.handle_super(prepared,on_air)
            
    
    def handle_super(self, prepared, on_air):
        try:
            if prepared._index == on_air._index:
                print('Index match.')
                if prepared.is_super == True and on_air.is_super != True and self.last_super_index != prepared._index:
                    time.sleep(self.parent.press_delay)
                    keyboard.press_and_release(self.parent.advance_key)
                    self.last_super_index = prepared._index
        except AttributeError as e:
            print(f'Error advancing super: {e}')
            self.parent.log.error(e)
    
    def run(self):
        self.listening = True
        self.parent.statusbar.SetStatusText("SuperDrive is active.", 0)
        self.prepared_olv = []
        self.on_air_olv = []
        self.last_check = []
        self.prepared = None
        self.on_air = None
        self.last_super_index = None
        self.first_pass = True
        self.parent.set_columns()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            try:
                #Turn off timer updates to reduce network traffic.
                s.connect((self.OverDrive_IP, self.OverDrive_port))
                request = {'protocolVersion': '1',
                           'endpoint': 'subscription',
                           'reqData': 'type=optOut',
                           'correlationId': '1000001'
                           }
                s.sendall(bytearray(json.dumps(request), 'UTF-8'))
                data = s.recv(1026)
                
                while self.listening:
                    s.sendall(bytearray(json.dumps(self.request), 'UTF-8'))
                    
                    # Listen for incoming data
                    data = s.recv(1026)
                    
                    if not data:
                        print("Connection closed by the server.")
                        break  # Exit the loop if the connection is closed
                    
                    else:
                        validation = self.validate_data(data)
                        if validation[0]:
                            try:
                                parsed = self.parse_data(validation[1])
                                self.present_data(parsed)
                            except TypeError as e:
                                print(f"Type error in data: {e}")
                                self.parent.log.error(e)

            except socket.error as e:
                print(f"Socket error: {e}")
                
                s.close()
                print('Socket closed.')
                
            self.parent.statusbar.SetStatusText("SuperDrive is not active.", 0)