from __future__ import unicode_literals

import base64

decode = base64.decodestring

# MiXia

MIXIA_API_URL = decode('aHR0cDovL2FwaS54aWFtaS5jb20vYXBpLw==') # 000000010013db47
MIXIA_API_KEY = decode('OWZmODU3YjJiMmQwMDFkNWMxNzQ0NzYxMzQ1MmJlZWI=') # 000000010013dd12
MIXIA_SIGN_HASH_RADIUS = decode('MmRmNTk2NWViZTQyZTZhNzQ4Yjg2Y2E0ODFkYjJmYjA=') # 000000010013e049

TRACK_LOW_QUALITY = 'l'
TRACK_HIGH_QUALITY = 'h'