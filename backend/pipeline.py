from pathlib import Path

import requests


def get_avatar(backend, strategy, details, response, user=None,
               *args, **kwargs):
    if backend.name == 'telegram':
        if response.get('photo_url', None):
            path = Path(__file__).parent.parent.parent
            path = path / f'static/media/images/{user.username}.jpg'
            picture = requests.get(response.get('photo_url')).content
            with open(path.as_posix(), 'wb') as file:
                file.write(picture)

            user.avatar = f'/static/media/images/{user.username}.jpg'
            user.save()
