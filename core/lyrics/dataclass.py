class Lyric:
    def __init__(self, q, title, artist, lyrics, raw_dict, images, images_saved_before):
        self.lyrics = self.lyric = lyrics
        self.raw = self.raw_dict = self.dict = raw_dict
        self.title = title
        self.artist = self.by = artist
        self._images_saved_before = images_saved_before
        self.images = images or {}

        if not images_saved_before or not images:
            try:
                if 'track' in raw_dict:
                    if 'images' in raw_dict['track']:
                        if raw_dict['track']['images'].get('background'):
                            self.images['background'] = raw_dict['track']['images']['background']

                        if raw_dict['track']['images'].get('coverart'):
                            self.images['track'] = raw_dict['track']['images']['coverart']
                        elif raw_dict['track']['images'].get('coverarthq'):
                            self.images['track'] = raw_dict['track']['images']['coverarthq']
            except:
                pass

        self.images['track'] = self.images.get('track') or None
        self.images['background'] = self.images.get('background') or None

    def __str__(self):
        return self.lyrics
