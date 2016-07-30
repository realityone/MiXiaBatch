#!/usr/bin/env python
# encoding=utf-8

from __future__ import unicode_literals

import os
import sys
import shutil
import subprocess
from multiprocessing.pool import ThreadPool

import requests

from mixia_batch import account
from mixia_batch import song
from mixia_batch import consts

try:
    import eyed3
except Exception:
    eyed3 = None
    print "eyed3 not imported"


class FetchFailed(Exception):
    pass


def usage():
    print "usage:"
    print "export MIXIA_ACCESS_TOKEN=\"your token\""
    print "    {} ALBUM_IDS...".format(sys.argv[0])
    print ""


def ensure_dir(dir_name):
    dir_name = './' + dir_name
    shutil.rmtree(dir_name, ignore_errors=True)
    try:
        os.mkdir(dir_name)
    except Exception, e:
        pass


def main():
    ACCESS_TOKEN = os.getenv('MIXIA_ACCESS_TOKEN')
    if not ACCESS_TOKEN:
        raise FetchFailed("`MIXIA_ACCESS_TOKEN` not found.")

    user = account.MiXiaUser.from_access_token(ACCESS_TOKEN)
    client = user.mixia_client

    try:
        album_ids = sys.argv[1:]
    except Exception:
        raise FetchFailed("Album id not found.")

    for aid in album_ids:
        thread_pool = ThreadPool(processes=10)
        album = song.MiXiaAlbum.from_id(aid, client)
        thread_pool.map_async(
            lambda s: s.fetch_detail(
                client, consts.TRACK_HIGH_QUALITY
            ), album.songs
        )
        thread_pool.close()
        thread_pool.join()

        ensure_dir(str(album.album_id))
        album_logo_resp = requests.get(
            album.big_logo,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
            }
        )
        album_logo_resp.raise_for_status()
        album_logo = album_logo_resp.content
        for s in album.songs:
            detail = s.track_detail
            filename = './{}/{}.mp3'.format(album.album_id, s.song_id)
            print filename
            subprocess.call(['wget', '-O', filename, detail.track_url])

            song_name = '{}_{}_{}'.format(
                detail.cd_serial, detail.track,
                detail.song_name.replace('/', '_')
            )

            if not eyed3:
                print "no eyed3, skip update ID3."
                os.rename(filename, song_name)
                continue

            song_id3 = eyed3.load(filename)
            song_id3.initTag()
            song_id3.rename(song_name)
            song_id3.tag.images.set(type_=3,
                                    img_data=album_logo,
                                    mime_type='image/jpeg')
            song_id3.tag.title = detail.song_name
            song_id3.tag.album = detail.album_name
            song_id3.tag.album_artist = detail.artist_name
            song_id3.tag.artist = detail.artist_name
            song_id3.tag.disc_num = (detail.cd_serial, album.cd_count)
            song_id3.tag.track_num = (detail.track, album.song_count)

            song_id3.tag.save()


if __name__ == '__main__':
    usage()
    main()
