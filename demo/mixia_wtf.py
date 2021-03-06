#!/usr/bin/env python
# encoding=utf-8

from __future__ import unicode_literals

import os
import sys
import base64
import shutil
import urllib
import subprocess
import collections

import requests

try:
    import eyed3
except Exception:
    eyed3 = None
    print "eyed3 not imported"

namedtuple = collections.namedtuple

WTF_URL = base64.decodestring(
    'aHR0cDovL3d3dy54aWFtaS5jb20vc29uZy9wbGF5bGlzdC9pZC97fS90eXBlLzEvY2F0L2pzb24=')
WTF_HQ_URL = base64.decodestring('aHR0cDovL3d3dy54aWFtaS5jb20vc29uZy9nZXRocXNvbmcvc2lkL3t9')


def usage():
    print "usage:"
    print "    {} ALBUM_IDS...".format(sys.argv[0])
    print ""


def ensure_dir(dir_name):
    dir_name = './' + dir_name
    shutil.rmtree(dir_name, ignore_errors=True)
    try:
        os.mkdir(dir_name)
    except Exception, e:
        pass


def validate_fields(required_fields, data_dict):
    for f in required_fields:
        if f not in data_dict:
            raise Exception("Invalid track dict, field {} missed".format(f))


class Audio(namedtuple('_Audio', ['audioQualityEnum', 'filePath', 'rate'])):
    @classmethod
    def from_dict(cls, audio_dict):
        validate_fields(cls._fields, audio_dict)
        audio_data = {f: audio_dict[f] for f in cls._fields}
        return cls(**audio_data)


class Track(
        namedtuple('_Track', ['song_id', 'name', 'artist_name', 'album_id', 'album_name',
                              'cd_serial', 'track', 'album_pic', 'allAudios', 'artist'])):
    @classmethod
    def from_dict(cls, track_dict):
        validate_fields(cls._fields, track_dict)
        track_data = {f: track_dict[f] for f in cls._fields}
        track_data['allAudios'] = [
            Audio.from_dict(audio_dict) for audio_dict in track_data['allAudios']
        ]
        return cls(**track_data)

    @property
    def hq_audio(self):
        return next((audio for audio in self.allAudios
                     if audio.audioQualityEnum == 'HIGH' and audio.rate == 320), None)

    @staticmethod
    def decrypt_location(location):
        block_count, content = int(location[0]), location[1:]
        content_len = len(content)
        block_size = int(content_len / block_count)
        last = content_len % block_count

        parts = [content[i * (block_size + 1):(i + 1) * (block_size + 1)] for i in xrange(last)]
        for i in xrange(block_count - 1):
            parts.append(content[(block_size + 1) * last:][i * block_size:(i + 1) * block_size])

        max_len = max([len(p) for p in parts])
        fixed_parts = [
            (list(p) + [''] * (max_len - len(p))) if len(p) < max_len else list(p) for p in parts
        ]
        url = urllib.unquote(''.join(c for cs in zip(*fixed_parts) for c in cs)).replace('^', '0')
        return url

    def fetch_hq(self):
        hq_url = WTF_HQ_URL.format(self.song_id)
        hq_resp = requests.get(
            hq_url,
            headers={
                'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
                'Referer': 'http://www.xiami.com/'
            })
        hq_resp.raise_for_status()

        hq_data = hq_resp.json()
        if 'location' not in hq_data:
            raise Exception("invalid hq song response: {}".format(hq_data))

        return self.decrypt_location(hq_data['location'])


class Album(object):
    _fields = ('trackList', 'type', 'type_id')

    def __init__(self, album_id, tracks):
        self.tracks = tracks
        self.album_id = album_id

    @property
    def cd_count(self):
        return len({t.cd_serial for t in self.tracks})

    @property
    def song_count(self):
        return len(self.tracks)

    @property
    def big_logo(self):
        return next((t.album_pic for t in self.tracks))

    @classmethod
    def from_dict(cls, album_dict):
        validate_fields(cls._fields, album_dict)
        album_data = {f: album_dict[f] for f in cls._fields}
        if album_data['type'] != 'album':
            raise Exception("data type is not album")
        album_id = album_data['type_id']
        tracks = [Track.from_dict(t_dict) for t_dict in album_data['trackList']]
        return cls(album_id, tracks)


def request_album(album_id):
    url = WTF_URL.format(album_id)
    album_resp = requests.get(
        url,
        headers={
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        })
    album_resp.raise_for_status()

    album_resp_json = album_resp.json()
    validate_fields(('data', ), album_resp_json)

    album_dict = album_resp_json['data']
    album = Album.from_dict(album_dict)

    return album


def main():
    try:
        album_ids = sys.argv[1:]
    except Exception:
        raise FetchFailed("Album id not found.")

    for aid in album_ids:
        try:
            album = request_album(aid)
        except Exception as e:
            print "fetch album {} failed".format(aid)

        ensure_dir(str(album.album_id))
        album_logo_resp = requests.get(
            album.big_logo,
            headers={
                'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
            })
        album_logo_resp.raise_for_status()
        album_logo = album_logo_resp.content
        for t in album.tracks:
            filename = './{}/{}.mp3'.format(album.album_id, t.song_id)
            print filename
            if not t.hq_audio:
                hq_url = t.fetch_hq()
            else:
                hq_url = t.hq_audio.filePath
            subprocess.call(['wget', '-O', filename, hq_url])

            song_name = '{}_{}_{}'.format(t.cd_serial, t.track, t.name.replace('/', '_'))

            if not eyed3:
                print "no eyed3, skip update ID3."
                if not song_name.endswith('.mp3'):
                    song_name += '.mp3'
                os.rename(filename, os.path.join(album.album_id, song_name))
                continue

            song_id3 = eyed3.load(filename)
            song_id3.initTag()
            song_id3.rename(song_name)
            song_id3.tag.images.set(type_=3, img_data=album_logo, mime_type='image/jpeg')
            song_id3.tag.title = t.name
            song_id3.tag.album = t.album_name
            song_id3.tag.album_artist = t.artist_name
            song_id3.tag.artist = t.artist
            song_id3.tag.disc_num = (t.cd_serial, album.cd_count)
            song_id3.tag.track_num = (t.track, album.song_count)

            song_id3.tag.save()


if __name__ == '__main__':
    usage()
    main()