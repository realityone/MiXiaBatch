from __future__ import unicode_literals

import logging
import collections

import requests

import consts
import mixia

namedtuple = collections.namedtuple


class LoginFailed(Exception):
    pass


class MiXiaUser(namedtuple('_MiXiaUser',
                           ['access_token', 'user_id', 'is_vip', 'profile'])):

    def __init__(self, *args, **kwargs):
        super(MiXiaUser, self).__init__(*args, **kwargs)
        self.mixia_client = mixia.MiXiaClient(user_id=self.user_id,
                                              access_token=self.access_token)

    @classmethod
    def from_access_token(cls, access_token):
        mixia_client = mixia.MiXiaClient(access_token=access_token)

        user_profile = mixia_client.show_user_profile()
        user_id = user_profile['user_id']
        is_vip = user_profile['level'] == 'vip'
        return cls(access_token, user_id, is_vip, user_profile)

    def __repr__(self):
        return '<MiXiaUser: {}>'.format(self.user_id)


class LoginMethod(object):

    def __init__(self, username, password):
        super(LoginMethod, self).__init__()
        self.username = username
        self.password = password

    def login(self):
        """
        rtype: `MiXiaUser`
        """
        raise NotImplementedError()


class TaoBaoOAuth(LoginMethod):

    oauth_url = consts.TAOBAO_OAUTH_URL
    client_id = consts.TAOBAO_OAUTH_CLIENT_ID
    client_secret = consts.TAOBAO_OAUTH_CLIENT_SECRET

    def __init__(self, username, password):
        super(TaoBaoOAuth, self).__init__(username, password)
        self.session = requests.session()
        self.mixia_client = mixia.MiXiaClient()

    def taobao_login(self):
        login_payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'password',
            'password': self.password,
            'site': 12,
            'username': self.username
        }

        try:
            logging.debug("Login with payload: %s.", login_payload)
            response = self.session.post(self.oauth_url,
                                         data=login_payload)
            response.raise_for_status()
        except Exception, e:
            raise LoginFailed(
                "Login with username `{}` "
                "and password `{}` failed: {}.".format(
                    self.username,
                    self.password,
                    e
                )
            )
        else:
            response_data = response.json()
        finally:
            logging.debug("Login response: %s.", response.content)

        if response_data.get('error_code'):
            raise LoginFailed("Login with taobao account "
                              "failed: {}.".format(response_data))

        return response_data

    def login(self):
        login_response = self.taobao_login()
        if 'access_token' not in login_response:
            raise LoginFailed("`access_token` field not "
                              "found in response: {}.".format(login_response))

        taobao_token = login_response['access_token']
        logging.debug("Exchange mixia access token with "
                      "taobao access token: %s.", taobao_token)

        mixia_token = self.mixia_client.exchange_taobao_token(taobao_token)
        return MiXiaUser.from_access_token(mixia_token)

if __name__ == '__main__':
    pass
