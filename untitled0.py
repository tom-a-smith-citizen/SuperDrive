# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 07:38:05 2024

@author: TOSmith
"""

import languagemodels as lm
lm.config['max_ram'] = '4gb'
a_input = """
Return space 'XPN 1 MOS CG' appears only once.
INFO:__main__:Prepared: H18 
 CLOSE SHOT-INET2 
 99 - XPN 1 MOS CG 
 XPN 1 MOS CG 
 --
INFO:__main__:On Air: H17 
 CLOSE SHOT-ON CAM 
 99 - XPN 1 MOS CG 
 XPN 1 MOS CG 
 --"""
_input = """Return space if prepared equals true and On Air is False. Else, return no space.
Prepared = True
On Air = True
"""
result = lm.do(_input,['space','no space'])
print(result)