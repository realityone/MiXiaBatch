from __future__ import unicode_literals

import logging
import collections

import mixia
import consts

namedtuple = collections.namedtuple


class MiXiaTrackDetail(namedtuple(
        '_MiXiaTrackDetail', [
            'recommends', 'hash', 'mv_id', 'album_id',
            'track', 'demo', 'track_url', 'lyric_text',
            'lyric_trc', 'artist_name', 'play_seconds',
            'flag', 'lyric', 'lyric_karaok', 'rec_note',
            'singers', 'logo', 'album_name', 'quality',
            'level', 'song_id', 'name', 'title',
            'song_name', 'album_logo', 'lyric_file',
            'artist_logo', 'favourite', 'length', 'play_counts',
            'default_resource_id', 'artist_id', 'res_id',
            'cd_serial'
        ])):

    @classmethod
    def from_dict(cls, track_detail):
        track_detail_data = {
            f: track_detail.get(f)
            for f in cls._fields
        }
        return cls(**track_detail_data)

    def __repr__(self):
        return '<MiXiaTrackDetail(song_id={}, quality={})>'.format(
            self.song_id,
            self.quality
        )


class MiXiaSong(namedtuple('_MiXiaSong', ['track'])):

    class MiXiaTrack(namedtuple(
            '_MiXiaTrack', [
                'song_id', 'recommends', 'listen_file',
                'mv_id', 'album_id', 'track',
                'demo', 'song_name', 'album_logo',
                'flag', 'artist_name', 'play_seconds',
                'length', 'is_check', 'rec_note',
                'singers', 'logo', 'artist_id',
                'album_name', 'cd_serial'
            ])):

        @classmethod
        def from_dict(cls, track_dict):
            track_data = {
                f: track_dict.get(f)
                for f in cls._fields
            }
            return cls(**track_data)

    @classmethod
    def from_dict(cls, song_dict):
        return cls(cls.MiXiaTrack.from_dict(song_dict))

    def __init__(self, *args, **kwargs):
        super(MiXiaSong, self).__init__(*args, **kwargs)
        self.track_detail = None

    @property
    def song_id(self):
        return self.track.song_id

    def fetch_detail(self, client,
                     quality=consts.TRACK_LOW_QUALITY, force=False):
        if not self.track_detail or force:
            track_detail = client.get_track_detail(
                self.song_id, quality=quality
            )
            self.track_detail = MiXiaTrackDetail.from_dict(track_detail)
        return self.track_detail

    def __repr__(self):
        return '<MiXiaSong(song_id={}, track_detail={})>'.format(
            self.song_id,
            self.track_detail
        )


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
        album_response = client.album_detail(album_id)
        return cls.from_dict(album_response)

    @classmethod
    def from_dict(cls, album_dict):
        songs = album_dict.pop('songs', [])

        album_data = {
            f: album_dict.get(f)
            for f in cls._fields
        }
        album_data['songs'] = [MiXiaSong.from_dict(s) for s in songs]
        return cls(**album_data)

    def __repr__(self):
        return '<MiXiaAlbum(album_id={}, songs={})>'.format(
            self.album_id,
            self.songs
        )
