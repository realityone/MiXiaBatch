from __future__ import unicode_literals

import logging
import collections

import requests

import consts
import mixia

namedtuple = collections.namedtuple

__all__ = ['LoginFailed', 'MiXiaUser']


class LoginFailed(Exception):
    pass


class MiXiaUser(namedtuple('_MiXiaUser', ['access_token', 'profile'])):

    class UserProfile(namedtuple(
            '_UserProfile', [
                'credit_level', 'collect_capacity', 'artists',
                'listens', 'city', 'user_id', 'introduction',
                'vip_expire', 'gmt_create', 'fans', 'followers',
                'email', 'agoo_token', 'province', 'tone_type',
                'birthday', 'capacity', 'level', 'nick_name',
                'gender', 'events_expire', 'avatar',
                'signature', 'songs'
            ])):

        @classmethod
        def from_dict(cls, user_dict):
            user_data = {
                f: user_dict.get(f)
                for f in cls._fields
            }
            return cls(**user_dict)

    @property
    def user_id(self):
        return self.profile.user_id

    @property
    def is_vip(self):
        return self.profile.level == 'vip'

    def __init__(self, *args, **kwargs):
        super(MiXiaUser, self).__init__(*args, **kwargs)
        self.mixia_client = mixia.MiXiaClient(user_id=self.user_id,
                                              access_token=self.access_token)

    @classmethod
    def from_access_token(cls, access_token):
        mixia_client = mixia.MiXiaClient(access_token=access_token)

        user_profile = mixia_client.show_user_profile()
        profile = cls.UserProfile.from_dict(user_profile)
        return cls(access_token, profile)

    def __repr__(self):
        return '<MiXiaUser: {}>'.format(self.user_id)
