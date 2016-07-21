from __future__ import unicode_literals

from account import TaoBaoOAuth
from song import MiXiaAlbum


def main():
    user = TaoBaoOAuth('username', 'password').login()

    album = MiXiaAlbum.from_id('2100362171', user.mixia_client)
    album.to_hq_version(user.mixia_client)

    print album

if __name__ == '__main__':
    main()
