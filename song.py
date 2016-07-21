from __future__ import unicode_literals

import logging
import collections

import mixia

namedtuple = collections.namedtuple


class MiXiaHQSong(namedtuple(
        '_MiXiaHQSong', [
            'play_volume', 'listen_file', 'mv_id',
            'flag', 'expire', 'logo',
            'quality', 'song_id', 'song_name',
            'play_authority', 'music_type', 'length'
        ])):

    @classmethod
    def from_dict(cls, hq_song_dict):
        hq_song_data = {
            f: hq_song_dict.get(f)
            for f in cls._fields
        }
        return MiXiaHQSong(**hq_song_data)

    def __repr__(self):
        return '<MiXiaHQSong(song_id={})>'.format(self.song_id)


class MiXiaSong(namedtuple(
        '_MiXiaSong', [
            'song_id', 'recommends', 'listen_file',
            'mv_id', 'album_id', 'track',
            'demo', 'song_name', 'album_logo',
            'flag', 'artist_name', 'play_seconds',
            'length', 'is_check', 'rec_note',
            'singers', 'logo', 'artist_id',
            'album_name', 'cd_serial'
        ])):

    def __init__(self, *args, **kwargs):
        super(MiXiaSong, self).__init__(*args, **kwargs)
        self.hq_version = None

    def set_hq_version(self, hq_version):
        self.hq_version = hq_version

    @classmethod
    def from_dict(cls, song_dict):
        song_data = {
            f: song_dict.get(f)
            for f in cls._fields
        }
        return MiXiaSong(**song_data)

    def __repr__(self):
        return '<MiXiaSong(song_id={}, hq_version={})>'.format(self.song_id,
                                                               self.hq_version)


class MiXiaAlbum(namedtuple(
        '_MiXiaAlbum', [
            'is_play', 'album_id', 'grade',
            'is_musician', 'play_authority', 'is_favorite',
            'is_check', 'logo', 'collects', 'category',
            'ads', 'song_count', 'sub_title', 'comments',
            'album_category', 'artist_id', 'status',
            'recommends', 'description', 'check_rate',
            'company', 'artist_name', 'play_count',
            'artist_logo', 'album_name', 'cd_count',
            'language', 'gmt_publish', 'songs'
        ])):

    @classmethod
    def from_id(cls, album_id, client):
        album_response = client.fetch_album_info(album_id)
        return cls.from_dict(album_response)

    @classmethod
    def from_dict(cls, album_dict):
        songs = album_dict.pop('songs', [])

        album_data = {
            f: album_dict.get(f)
            for f in cls._fields
        }
        album_data['songs'] = [MiXiaSong.from_dict(s) for s in songs]
        return MiXiaAlbum(**album_data)

    def to_hq_version(self, client):
        song_ids = [s.song_id for s in self.songs]
        hq_songs_info = client.fetch_hq_song_info(*song_ids)
        hq_songs = {
            hq_song['song_id']: MiXiaHQSong.from_dict(hq_song)
            for hq_song in hq_songs_info.get('songs', [])
        }
        for song in self.songs:
            song.set_hq_version(hq_songs.get(song.song_id))

    def __repr__(self):
        return '<MiXiaAlbum(album_id={}, songs={})>'.format(
            self.album_id,
            self.songs
        )
