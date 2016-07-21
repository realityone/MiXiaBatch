from __future__ import unicode_literals

import base64

# TaoBao OAuth

decode = base64.decodestring

TAOBAO_OAUTH_URL = decode('aHR0cHM6Ly9wYXNzcG9ydC5hbGlwYXkuY29tL29hdXRoMi90b2tlbg==')
TAOBAO_OAUTH_CLIENT_ID = decode('NjcwNGE5YzYwMjE0YjkxOTZiYWFkMDMzYzg2NjgyMWY=')
TAOBAO_OAUTH_CLIENT_SECRET = decode('YjUzZmVmZGQ3ZDRlZTIxZTM5MDNkMGNiMTBiNDNmNTc=')

# MiXia

MIXIA_API_URL = decode('aHR0cDovL3NwYXJrLmFwaS54aWFtaS5jb20vYXBp')
MIXIA_API_KEY = decode('MjlhZTZkZGU0ZWM1MTk3YjQ1NTIwNzMxYzZiMjZhZDA=')
MIXIA_SIGN_HASH_RADIUS = decode('MWZiOWViZDEyYmVjMmRiOGMyNTBlMWZhZTliMzdjYTY=')
