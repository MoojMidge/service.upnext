# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals
import random
import constants

LIBRARY = {
    'tvshows': {
        'Game of Thrones': {
            'tvshowid': constants.UNDEFINED,
        },
        'Breaking Bad': {
            'tvshowid': constants.UNDEFINED,
        },
        'The Mandalorian': {
            'tvshowid': constants.UNDEFINED,
        },
        'The Handmaid\'s Tale': {
            'tvshowid': constants.UNDEFINED,
        },
        'Mad Men': {
            'tvshowid': constants.UNDEFINED,
        }
    },
    'episodes': [
        {
            'episodeid': constants.UNDEFINED,
            'tvshowid': constants.UNDEFINED,
            'title': 'Garden of Bones (Jardín de huesos)',
            'art': {
                'thumb': 'https://artworks.thetvdb.com/banners/episodes/121361/4245773.jpg',
                'tvshow.fanart': 'https://artworks.thetvdb.com/banners/fanart/original/121361-5.jpg',
                'tvshow.landscape': 'https://artworks.thetvdb.com/banners/fanart/original/121361-4.jpg',
                'tvshow.poster': 'https://artworks.thetvdb.com/banners/posters/121361-4.jpg',
            },
            'season': 2,
            'episode': 4,
            'showtitle': 'Game of Thrones',
            'plot': 'Lord Baelish arrives at Renly\'s camp just before he faces off against Stannis. '
                    'Daenerys and her company are welcomed into the city of Qarth. Arya, Gendry, and '
                    'Hot Pie find themselves imprisoned at Harrenhal.',
            'playcount': 0,
            'lastplayed': '2012-04-22 22:00:00',
            'resume': {
                'position': 300,
                'total': 3000,
            },
            'rating': 8.8,
            'firstaired': '2012-04-22',
            'runtime': 3000,
            'file': 'file://media/tvshows/Game of Thrones/Season 02/Game of Thrones - S02E04 - Garden of Bones (Jardín de huesos).mkv'
        },
        {
            'episodeid': constants.UNDEFINED,
            'tvshowid': constants.UNDEFINED,
            'title': 'The Ghost of Harrenhal (하렌할의 유령)',
            'art': {
                'thumb': 'https://artworks.thetvdb.com/banners/episodes/121361/4245774.jpg',
                'tvshow.fanart': 'https://artworks.thetvdb.com/banners/fanart/original/121361-5.jpg',
                'tvshow.landscape': 'https://artworks.thetvdb.com/banners/fanart/original/121361-4.jpg',
                'tvshow.poster': 'https://artworks.thetvdb.com/banners/posters/121361-4.jpg',
            },
            'season': 2,
            'episode': 5,
            'showtitle': 'Game of Thrones',
            'plot': 'Tyrion investigates a secret weapon that King Joffrey plans to use against Stannis. '
                    'Meanwhile, as a token for saving his life, Jaqen H\'ghar offers to kill three people '
                    'that Arya chooses.',
            'playcount': 0,
            'lastplayed': '',
            'resume': {
                'position': 0,
                'total': 3300,
            },
            'rating': 8.8,
            'firstaired': '2012-04-29',
            'runtime': 3300,
            'file': 'file://media/tvshows/Game of Thrones/Season 02/Game of Thrones - S02E05 - The Ghost of Harrenhal (하렌할의 유령).mkv'
        },
        {
            'episodeid': constants.UNDEFINED,
            'tvshowid': constants.UNDEFINED,
            'title': 'Full Measure (מידה מלאה)',
            'art': {
                'thumb': 'https://artworks.thetvdb.com/banners/episodes/81189/2106601.jpg',
                'tvshow.fanart': 'https://artworks.thetvdb.com/banners/fanart/original/81189-21.jpg',
                'tvshow.landscape': 'https://artworks.thetvdb.com/banners/fanart/original/81189-15.jpg',
                'tvshow.poster': 'https://artworks.thetvdb.com/banners/posters/81189-10.jpg',
            },
            'season': 3,
            'episode': 13,
            'showtitle': 'Breaking Bad',
            'plot': 'With Jesse on the run, Walt negotiates a bargain with Gus and concocts a plan '
                    'to provide for his and Jesse\'s safety.',
            'playcount': 1,
            'lastplayed': '2010-06-13 22:00:00',
            'resume': {
                'position': 0,
                'total': 2820,
            },
            'rating': 9.6,
            'firstaired': '2010-06-13',
            'runtime': 2820,
            'file': 'file://media/tvshows/Breaking Bad/Season 03/Breaking Bad - S03E13 - Full Measure (מידה מלאה).mkv'
        },
        {
            'episodeid': constants.UNDEFINED,
            'tvshowid': constants.UNDEFINED,
            'title': 'Box Cutter (เครื่องตัดกล่อง)',
            'art': {
                'thumb': 'https://artworks.thetvdb.com/banners/episodes/81189/2639411.jpg',
                'tvshow.fanart': 'https://artworks.thetvdb.com/banners/fanart/original/81189-21.jpg',
                'tvshow.landscape': 'https://artworks.thetvdb.com/banners/fanart/original/81189-15.jpg',
                'tvshow.poster': 'https://artworks.thetvdb.com/banners/posters/81189-10.jpg',
            },
            'season': 4,
            'episode': 1,
            'showtitle': 'Breaking Bad',
            'plot': 'Walt and Jesse face the deadly consequences of their actions. '
                    'Skyler deals with a puzzling disappearance, as Marie struggles to help Hank with his recovery.',
            'playcount': 0,
            'lastplayed': '',
            'resume': {
                'position': 0,
                'total': 2880,
            },
            'rating': 9.2,
            'firstaired': '2011-07-17',
            'runtime': 2880,
            'file': 'file://media/tvshows/Breaking Bad/Season 04/Breaking Bad - S04E01 - Box Cutter (เครื่องตัดกล่อง).mkv'
        }
    ],
    'sets': {
        'The Avengers Collection': {
            'setid': constants.UNDEFINED,
        },
        'The Lord of the Rings Collection': {
            'setid': constants.UNDEFINED,
        }
    },
    'movies': [
        {
            'movieid': constants.UNDEFINED,
            'setid': constants.UNDEFINED,
            'title': 'The Avengers',
            'art': {
                'poster': 'https://www.themoviedb.org/t/p/original/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg',
                'fanart': 'https://www.themoviedb.org/t/p/original/9BBTo63ANSmhC4e6r62OJFuK2GL.jpg',
            },
            'set': 'The Avengers Collection',
            'plot': 'When an unexpected enemy emerges and threatens global safety and security, '
                    'Nick Fury, director of the international peacekeeping agency known as S.H.I.E.L.D., '
                    'finds himself in need of a team to pull the world back from the brink of disaster. '
                    'Spanning the globe, a daring recruitment effort begins!',
            'playcount': 1,
            'lastplayed': '2012-06-01 22:00:00',
            'resume': {
                'position': 0,
                'total': 8580,
            },
            'rating': 8.0,
            'premiered': '2012-04-25',
            'year': 2012,
            'runtime': 8580,
            'file': 'file://media/movies/The Avengers (2012)/The Avengers (2012).mkv'
        },
        {
            'movieid': constants.UNDEFINED,
            'setid': constants.UNDEFINED,
            'title': 'Avengers: Age of Ultron',
            'art': {
                'poster': 'https://www.themoviedb.org/t/p/original/4ssDuvEDkSArWEdyBl2X5EHvYKU.jpg',
                'fanart': 'https://www.themoviedb.org/t/p/original/6YwkGolwdOMNpbTOmLjoehlVWs5.jpg',
            },
            'set': 'The Avengers Collection',
            'plot': 'When Tony Stark and Bruce Banner try to jump-start a dormant peacekeeping program '
                    'called Ultron, things go horribly wrong and it\'s up to Earth\'s mightiest heroes '
                    'to stop the villainous Ultron from enacting his terrible plan.',
            'playcount': 1,
            'lastplayed': '2015-06-01 22:00:00',
            'resume': {
                'position': 0,
                'total': 8460,
            },
            'rating': 7.3,
            'premiered': '2015-04-22',
            'year': 2015,
            'runtime': 8460,
            'file': 'file://media/movies/Avengers - Age of Ultron (2015)/Avengers - Age of Ultron (2015).mkv'
        },
        {
            'movieid': constants.UNDEFINED,
            'setid': constants.UNDEFINED,
            'title': 'Avengers: Infinity War',
            'art': {
                'poster': 'https://www.themoviedb.org/t/p/original/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg',
                'fanart': 'https://www.themoviedb.org/t/p/original/mDfJG3LC3Dqb67AZ52x3Z0jU0uB.jpg',
            },
            'set': 'The Avengers Collection',
            'plot': 'The Avengers and their allies must be willing to sacrifice all in an attempt to '
                    'defeat the powerful Thanos before his blitz of devastation and ruin puts an end '
                    'to the universe.',
            'playcount': 0,
            'lastplayed': '',
            'resume': {
                'position': 0,
                'total': 8940,
            },
            'rating': 8.4,
            'premiered': '2018-04-25',
            'year': 2018,
            'runtime': 8940,
            'file': 'file://media/movies/Avengers - Infinity War (2018)/Avengers - Infinity War (2018).mkv'
        },
        {
            'movieid': constants.UNDEFINED,
            'setid': constants.UNDEFINED,
            'title': 'Avengers: Endgame',
            'art': {
                'poster': 'https://www.themoviedb.org/t/p/original/or06FN3Dka5tukK1e9sl16pB3iy.jpg',
                'fanart': 'https://www.themoviedb.org/t/p/original/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg',
            },
            'set': 'The Avengers Collection',
            'plot': 'After the devastating events of Avengers: Infinity War (2018), the universe is in ruins. '
                    'With the help of remaining allies, the Avengers assemble once more in order to reverse '
                    'Thanos\' actions and restore balance to the universe.',
            'playcount': 0,
            'lastplayed': '',
            'resume': {
                'position': 0,
                'total': 10860,
            },
            'rating': 8.4,
            'premiered': '2019-04-24',
            'year': 2019,
            'runtime': 10860,
            'file': 'file://media/movies/Avengers - Endgame (2019)/Avengers - Endgame (2019).mkv'
        },
    ]
}


def update_library_ids():
    tvshow_ids = []
    episode_ids = []
    set_ids = []
    movie_ids = []

    for idx, tvshow in enumerate(LIBRARY['tvshows'], start=1):
        min_id = idx * 10
        max_id = min_id + 9
        tvshow_id = random.randint(min_id, max_id)
        while tvshow_id in tvshow_ids:
            tvshow_id = random.randint(min_id, max_id)
        tvshow_ids.append(tvshow_id)
        LIBRARY['tvshows'][tvshow]['tvshowid'] = tvshow_id

    for idx, episode in enumerate(LIBRARY['episodes'], start=1):
        min_id = idx * 10
        max_id = min_id + 9
        episode_id = random.randint(min_id, max_id)
        while episode_id in episode_ids:
            episode_id = random.randint(min_id, max_id)
        episode_ids.append(episode_id)
        episode['episodeid'] = episode_id

        tvshow = LIBRARY['tvshows'].get(episode['showtitle'], {})
        episode['tvshowid'] = tvshow.get('tvshowid', constants.UNDEFINED)

    for idx, _set in enumerate(LIBRARY['sets'], start=1):
        min_id = idx * 10
        max_id = min_id + 9
        set_id = random.randint(min_id, max_id)
        while set_id in set_ids:
            set_id = random.randint(min_id, max_id)
        set_ids.append(set_id)
        LIBRARY['sets'][_set]['setid'] = set_id

    for idx, movie in enumerate(LIBRARY['movies'], start=1):
        min_id = idx * 10
        max_id = min_id + 9
        movie_id = random.randint(min_id, max_id)
        while movie_id in movie_ids:
            movie_id = random.randint(min_id, max_id)
        movie_ids.append(movie_id)
        movie['movieid'] = movie_id

        _set = LIBRARY['sets'].get(movie['set'], {})
        movie['setid'] = _set.get('setid', constants.UNDEFINED)


update_library_ids()
