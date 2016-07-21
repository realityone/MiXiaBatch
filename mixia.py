from __future__ import unicode_literals

import json
import time
import hashlib
import logging

import requests
import consts


class MiXiaError(Exception):
    pass


class MiXiaClient(requests.Session):

    api_url = consts.MIXIA_API_URL
    api_key = consts.MIXIA_API_KEY
    sign_hash_radius = consts.MIXIA_SIGN_HASH_RADIUS

    @staticmethod
    def parse_response(response):
        logging.debug("Got response "
                      "from mixia: %s.", response.content)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get('err'):
            raise MiXiaError("Fetch error from mixia "
                             "API: {}.".format(response_data))
        return response_data.get('data')

    def __init__(self, user_id=None, access_token=None, *args, **kwargs):
        super(MiXiaClient, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.access_token = access_token

    @property
    def is_login(self):
        return bool(self.user_id and self.access_token)

    def update_user_identify(self, user_id, access_token):
        self.user_id = user_id
        self.access_token = access_token

    def request(self, *args, **kwargs):
        logging.debug("Sending request with "
                      "arguments: %s, %s.", args, kwargs)
        params = kwargs.get('params', {})
        require_token = kwargs.pop('require_token', False)
        require_sign = kwargs.pop('require_sign', True)

        if require_sign:
            params = self._sign_payload(params)
        if require_token:
            params.setdefault('access_token', self.access_token)

        kwargs['params'] = params
        response = super(MiXiaClient, self).request(*args, **kwargs)
        return self.parse_response(response)

    def exchange_taobao_token(self, token):
        exchange_payload = {
            'app_v': '4010000',
            'method': 'Oneid.get',
            'lg': '1',
            'device_id': '5C:95:AE:78:7F:A3',
            'platform_id': '2',
            'proxy': '0',
            'ch': '201200',
            'token': token,
            'name': 'oneid.xiami.token.exchange',
            'v': '1.1',
            'network': '1',
        }
        response_data = self.get(self.api_url,
                                 params=exchange_payload,
                                 require_token=False,
                                 require_sign=True)

        access_token = response_data.get('result', {}).get('access_token')
        if not access_token:
            raise MiXiaError("MiXia access token not found in "
                             "response: {}".format(response_data))

        return access_token

    def show_user_profile(self):
        show_user_payload = {
            'app_v': '4010000',
            'method': 'Members.showUser',
            'lg': '1',
            'device_id': '5C:95:AE:78:7F:A3',
            'platform_id': '2',
            'proxy': '0',
            'ch': '201200',
            'v': '1.1',
            'network': '1'
        }
        response_data = self.get(self.api_url,
                                 params=show_user_payload,
                                 require_token=True,
                                 require_sign=True)
        return response_data

    def fetch_album_info(self, album_id):
        album_info_payload = {
            'app_v': '4010000',
            'av': 'ios_4.1.0',
            'ch': '201200',
            'device_id': '5C:95:AE:78:7F:A3',
            'h_uid': self.user_id,
            'id': str(album_id),
            'lg': '1',
            'method': 'Albums.detail',
            'network': '1',
            'platform_id': '2',
            'v': '1.1'
        }

        response_data = self.get(self.api_url,
                                 params=album_info_payload,
                                 require_token=True,
                                 require_sign=True)
        return response_data

    def fetch_hq_song_info(self, *song_ids):
        hq_song_info_payload = {
            'app_v': '4010000',
            'ch': '201200',
            'device_id': '5C:95:AE:78:7F:A3',
            'h_uid': self.user_id,
            'ids': ','.join([str(sid) for sid in song_ids]),
            'lg': '1',
            'method': 'Songs.getSimpleSongs',
            'network': '1',
            'platform_id': '2',
            'proxy': '0',
            'quality': 'h',
            'v': '1.1',
        }

        response_data = self.get(self.api_url,
                                 params=hq_song_info_payload,
                                 require_token=True,
                                 require_sign=True)
        return response_data

    @classmethod
    def _sign_payload(cls, payload):
        payload = payload.copy()
        payload['call_id'] = '{:.5f}'.format(time.time())
        payload['api_key'] = cls.api_key
        payload['api_sig'] = cls.calc_payload_signature(payload)
        return payload

    @classmethod
    def calc_payload_signature(cls, payload):
        m = hashlib.md5()

        sorted_payload = sorted(payload.iteritems(), key=lambda o: o[0])
        print sorted_payload
        for k, v in sorted_payload:
            m.update('{}{}'.format(k, v))

        m.update(cls.sign_hash_radius)
        return m.hexdigest()
