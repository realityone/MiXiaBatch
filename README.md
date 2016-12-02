# MiXiaBatch
Fetch music from mixia.com.

## Install

```
pip install https://github.com/realityone/MiXiaBatch/archive/master.zip
```

### Usage

```python
from __future__ import unicode_literals

import logging
from multiprocessing.pool import ThreadPool

from mixia_batch.account import MiXiaUser
from mixia_batch.song import MiXiaAlbum
from mixia_batch.consts import TRACK_HIGH_QUALITY

logging.basicConfig(level=logging.DEBUG)


def main():
    user = MiXiaUser.from_access_token(
        'token from browser'
    )

    album = MiXiaAlbum.from_id('2100362171', user.mixia_client)

    thread_pool = ThreadPool(processes=10)
    for s in album.songs:
        thread_pool.apply_async(
            s.fetch_detail, (user.mixia_client, TRACK_HIGH_QUALITY)
        )

    thread_pool.close()
    thread_pool.join()

    print album


if __name__ == '__main__':
    main()
```


