class Lyric:
    def __init__(self, title, artist, lyrics, raw_dict, images, images_from_redis):
        self.lyrics = lyrics
        self.lyric = lyrics
        self.raw = raw_dict
        self.raw_dict = raw_dict
        self.dict = raw_dict
        self.title = title
        self.artist = artist
        self.by = artist
        self._images_from_redis = images_from_redis
        self.images = images or {}

        if not images_from_redis or not images:
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

    def __str__(self):
        return self.lyrics