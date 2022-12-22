class Lyric:
    def __init__(self, q, title, artist, lyrics, raw_dict, track_img, bg_img, images_saved_before):
        self.lyrics = self.lyric = lyrics
        self.raw = self.raw_dict = self.dict = raw_dict
        self.title = title
        self.artist = self.by = artist
        self._images_saved_before = images_saved_before
        self.images = {}

        if track_img:
            self.images['track'] = track_img

        if bg_img:
            self.images['background'] = bg_img

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

    def __str__(self):
        return self.lyrics
