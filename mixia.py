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
    def generate_payload(method, **kwargs):
        # Dumped from MiXia Music 1.3.4
        payload = {
            'method': method,
        }
        payload.update(kwargs)
        return payload

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

    def show_user_profile(self):
        method = 'Members.showUser'
        show_user_payload = self.generate_payload(method)
        response_data = self.get(self.api_url,
                                 params=show_user_payload,
                                 require_token=True,
                                 require_sign=True)
        return response_data

    def album_detail(self, album_id):
        method = 'Albums.detail'
        album_detail_payload = self.generate_payload(
            method, id=str(album_id),
        )
        response_data = self.get(self.api_url,
                                 params=album_detail_payload,
                                 require_token=True,
                                 require_sign=True)
        return response_data

    def get_track_detail(self, track_id, quality=consts.TRACK_LOW_QUALITY):
        method = 'Songs.getTrackDetail'

        track_detail_paylod = self.generate_payload(
            method, id=str(track_id), quality=quality
        )
        response_data = self.get(self.api_url,
                                 params=track_detail_paylod,
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
        for k, v in sorted_payload:
            m.update('{}{}'.format(k, v))

        m.update(cls.sign_hash_radius)
        return m.hexdigest()
