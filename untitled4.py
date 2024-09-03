# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 06:31:49 2024

@author: TOSmith
"""

import json
from json_repair import repair_json

json_str = """{"shots":[{"type":"onair","slug":"5AM LABOR DAY EXPLAINER-PKG","index":"NA","shotName":"99 - XPN 1 MOS CG","templateName":"XPN 1 MOS CG","transitionName":"--"},{"type":"prepared","slug":"SHORT WX OPEN-OPEN","index":"C2","shotName":"94 - XPN 6 MOS CG","templateName":"XPN 6 MOS CG","transitionName":"--"}],"meta":{"serverDate":"2024-09-02T06:17:16,856-0400","odHost":"10.10.78.10","odVersion":"22.3.8","correlationId":"0"}}
{"cues":{"lastOnAirMsg":"-","lastOnAirMsgDate":"-","lastPreparedMsg":"-","lastPreparedMsgDate":"-"},"meta":{"serverDate":"2024-09-02T06:17:16,872-0400","odHost":"10.10.78.10","odVersion":"22.3.8"}}"""

try:
    jsonified = json.loads(json_str)
except json.JSONDecodeError:
    jsonified = repair_json(json_str)
    jsonified = json.loads(jsonified)