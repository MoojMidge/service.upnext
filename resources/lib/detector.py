# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import absolute_import, division, unicode_literals
import json
import operator
import os.path
import threading
import timeit
from PIL import Image
import xbmc
import file_utils
import utils


# Create directory where all stored hashes will be saved
SAVE_PATH = os.path.join(
    file_utils.translate_path(
        'special://profile/addon_data/{0}'.format(utils.addon_id())
    ),
    'detector',
    ''
)
file_utils.create_directory(SAVE_PATH)


class HashStore(object):  # pylint: disable=useless-object-inheritance
    __slots__ = (
        'version',
        'hash_size',
        'seasonid',
        'episode',
        'data',
        'timestamps'
    )

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', '0.1')
        self.hash_size = kwargs.get('hash_size', (8, 8))
        self.seasonid = kwargs.get('seasonid', '')
        self.episode = kwargs.get('episode', -1)
        self.data = kwargs.get('data', {})
        self.timestamps = kwargs.get('timestamps', {})

    @classmethod
    def log(cls, msg, level=utils.LOGINFO):
        utils.log(msg, name=cls.__name__, level=level)

    @staticmethod
    def int_to_hash(val, hash_size):
        return tuple([  # pylint: disable=consider-using-generator
            1 if bit_val == "1" else 0
            for bit_val in bin(val)[2:].zfill(hash_size)
        ])

    @staticmethod
    def hash_to_int(image_hash):
        return sum(
            bit_val << i
            for i, bit_val in enumerate(reversed(image_hash))
        )

    def is_valid(self, seasonid=None, episode=None):
        # Non-episodic video is being played
        if not self.seasonid or self.episode == -1:
            return False

        # New episode is being played, invalidate old hashes
        if (seasonid is not None and self.seasonid != seasonid
                or episode is not None and self.episode != episode):
            return False

        return True

    def invalidate(self):
        self.seasonid = ''
        self.episode = -1

    def load(self, identifier):
        filename = file_utils.make_legal_filename(identifier, suffix='.json')
        target = os.path.join(SAVE_PATH, filename)
        try:
            with open(target, mode='r') as target_file:
                hashes = json.load(target_file)
        except (IOError, OSError, TypeError, ValueError):
            self.log('Could not load stored hashes from {0}'.format(target),
                     utils.LOGDEBUG)
            return False

        if not hashes:
            return False

        self.version = hashes.get('version', self.version)
        self.hash_size = hashes.get('hash_size', self.hash_size)
        if 'data' in hashes:
            hash_size = self.hash_size[0] * self.hash_size[1]
            self.data = {
                tuple([utils.get_int(i) for i in key[1:-1].split(', ')]):  # pylint: disable=consider-using-generator
                self.int_to_hash(hashes['data'][key], hash_size)
                for key in hashes['data']
            }
        if 'timestamps' in hashes:
            self.timestamps = {
                utils.get_int(episode): hashes['timestamps'][episode]
                for episode in hashes['timestamps']
            }

        self.log('Hashes loaded from {0}'.format(target))
        return True

    def save(self, identifier):
        output = {
            'version': self.version,
            'hash_size': self.hash_size,
            'data': {
                str(hash_index): self.hash_to_int(self.data[hash_index])
                for hash_index in self.data
            },
            'timestamps': self.timestamps
        }

        filename = file_utils.make_legal_filename(identifier, suffix='.json')
        target = os.path.join(SAVE_PATH, filename)
        try:
            with open(target, mode='w') as target_file:
                json.dump(output, target_file, indent=4)
                self.log('Hashes saved to {0}'.format(target))
        except (IOError, OSError, TypeError, ValueError):
            self.log('Error: Could not save hashes to {0}'.format(target),
                     utils.LOGWARNING)
        return output


class Detector(object):  # pylint: disable=useless-object-inheritance
    """Detector class used to detect end credits in playing video"""

    __slots__ = (
        # Instances
        'capturer',
        'hashes',
        'past_hashes',
        'player',
        'state',
        'thread',
        # Settings
        'match_number',
        'significance_level',
        # Variables
        'capture_size',
        'capture_ar',
        'hash_index',
        'match_count',
        'credits_detected',
        # Signals
        'running',
        'sigstop',
        'sigterm'
    )

    def __init__(self, player, state):
        self.capturer = xbmc.RenderCapture()
        self.player = player
        self.state = state
        self.thread = None

        self.match_count = {
            'hits': 0,
            'misses': 0
        }
        self.credits_detected = False
        self.init_hashes()

        self.running = False
        self.sigstop = False
        self.sigterm = False

        self.log('Init')

    @classmethod
    def log(cls, msg, level=utils.LOGINFO):
        utils.log(msg, name=cls.__name__, level=level)

    @classmethod
    def calc_quartiles(cls, vals):
        """Method to calculate approximate quartiles for a list of values by
           sorting and indexing the list"""

        num_vals = len(vals)
        pivots = [
            int(num_vals * 0.25),
            int(num_vals * 0.50),
            int(num_vals * 0.75)
        ]
        vals = sorted(vals)
        if num_vals % 2:
            return [vals[pivot] for pivot in pivots]
        return [sum(vals[pivot - 1:pivot + 1]) // 2 for pivot in pivots]

    @classmethod
    def calc_significance(cls, vals):
        return 100 * sum(vals) / len(vals)

    @classmethod
    def calc_similarity(
            cls, hash1, hash2,
            function=operator.eq,
            do_zip=False,
            target='all'
    ):
        """Method to compare the similarity between two image hashes.
           By default checks whether each bit in the first hash is equal to the
           corresponding bit in the second hash"""

        # Check that hashes are not empty and that dimensions are equal
        if not hash1 or not hash2:
            return 0
        num_pixels = len(hash1)
        if num_pixels != len(hash2):
            return 0

        # Use zip if comparison function requires an iterator as an argument
        if do_zip:
            bit_compare = sum(map(function, zip(hash1, hash2)))
        else:
            bit_compare = sum(map(function, hash1, hash2))

        # Evaluate similarity as a percentage of all pixels in the hash
        if target == 'all':
            similarity = 100 * bit_compare / num_pixels
        # Or similarity as a percentage of all non-zero pixels in both hashes
        elif target == 'both':
            similarity = 100 * bit_compare / sum(map(any, zip(hash1, hash2)))
        # Or similarity as count of matching pixels
        elif target == 'none':
            similarity = bit_compare

        return similarity

    @classmethod
    def capture_resolution(cls, max_size=None):
        """Method to detect playing video resolution and aspect ratio and
           return a scaled down resolution tuple and aspect ratio for use in
           capturing the video frame buffer at a specific size/resolution"""

        aspect_ratio = float(xbmc.getInfoLabel('Player.Process(VideoDAR)'))

        # Capturing render buffer at higher resolution captures more detail
        # depending on Kodi scaling function used, but slows down processing.
        # Limit captured data to max_size (in kB)
        if max_size:
            max_size = max_size * 8 * 1024
            height = int((max_size / aspect_ratio) ** 0.5)
            width = int(height * aspect_ratio)
        else:
            width = xbmc.getInfoLabel('Player.Process(VideoWidth)')
            width = int(width.replace(',', ''))
            height = xbmc.getInfoLabel('Player.Process(VideoHeight)')
            height = int(height.replace(',', ''))

        return (width, height), aspect_ratio

    @classmethod
    def print_hash(cls, hash1, hash2, size=None, prefix=None):
        """Method to print two image hashes, side by side, to the Kodi log"""

        if not hash1 or not hash2:
            return
        num_pixels = len(hash1)
        if num_pixels != len(hash2):
            return

        if not size:
            size = int(num_pixels ** 0.5)
            size = (size, size)

        cls.log('\n\t\t\t'.join(
            [prefix if prefix else '-' * (7 + 4 * size[0])]
            + ['{0:>3} |{1}|{2}|'.format(
                row,
                ' '.join(
                    ['*' if bit else ' ' for bit in hash1[row:row + size[0]]]
                ),
                ' '.join(
                    ['*' if bit else ' ' for bit in hash2[row:row + size[0]]]
                )
            ) for row in range(0, num_pixels, size[0])]
        ))

    def check_similarity(self, image_hash, index_offset):
        stats = {
            'is_match': False,
            'possible_match': False,
            # Similarity to representative end credits hash
            'credits': 0,
            # Similarity to previous frame hash
            'previous': 0,
            # Significance level - areas of significant deviation in hash
            'significance': 0,
            # Similarity to hash from other episodes
            'episodes': 0
        }

        # Calculate similarity between current hash and representative hash
        stats['credits'] = self.calc_similarity(
            self.hashes.data.get(self.hash_index['credits']),
            image_hash
        )
        # Match if current hash (loosely) matches representative hash
        if stats['credits'] >= self.state.detect_level - 10:
            stats['is_match'] = True
        # Unless debugging, return if match found, otherwise continue checking
        if stats['is_match'] and not self.state.detector_debug:
            return stats

        # Calculate similarity between current hash and previous hash
        stats['previous'] = self.calc_similarity(
            self.hashes.data.get(self.hash_index['previous']),
            image_hash
        )
        # Calculate percentage of significant pixels
        stats['significance'] = self.calc_significance(image_hash)
        # Match if current hash matches previous hash and has few significant
        # regions of deviation
        if stats['previous'] >= self.state.detect_level:
            stats['possible_match'] = True
            stats['is_match'] = (
                stats['significance'] <= self.significance_level
            )
        # Unless debugging, return if match found, otherwise continue checking
        if stats['is_match'] and not self.state.detector_debug:
            return stats

        # Get all previous hash indexes for episodes other than the current
        # episode and where the hash timestamps are approximately equal (+/- an
        # index_offset)
        episode_idx = self.hash_index['current'][1]
        min_time_idx = self.hash_index['current'][0] - index_offset
        max_time_idx = self.hash_index['current'][0] + index_offset
        old_hash_indexes = [
            idx for idx in self.past_hashes.data
            if idx[1] != episode_idx
            and idx[0] >= min_time_idx
            and idx[0] <= max_time_idx
        ]
        old_hash_index = None
        for old_hash_index in old_hash_indexes:
            stats['episodes'] = self.calc_similarity(
                self.past_hashes.data[old_hash_index],
                image_hash
            )
            # Match if current hash matches other episode hashes
            if stats['episodes'] >= self.state.detect_level:
                stats['is_match'] = True
                break
        self.hash_index['episodes'] = old_hash_index

        return stats

    def detected(self):
        # Ignore invalidated hash data
        if not self.hashes.is_valid():
            return False

        # If a previously detected timestamp exists then indicate that credits
        # have been detected
        if self.past_hashes.timestamps.get(self.hashes.episode):
            return True

        self.log('{0}/{1} matches'.format(
            self.match_count['hits'],
            self.match_number
        ), utils.LOGDEBUG)
        self.credits_detected = self.match_count['hits'] >= self.match_number
        return self.credits_detected

    def init_hashes(self):
        # Limit captured data to 16 kB
        self.capture_size, self.capture_ar = self.capture_resolution(
            max_size=16
        )

        self.hash_index = {
            # Current hash index
            'current': (0, 0),
            # Previous hash index
            'previous': None,
            # Representative end credits hash index
            'credits': (0, 0),
            # Other episodes hash index
            'episodes': None,
            # Detected end credits timestamp from end of file
            'detected_at': None,
            # Storing enabled flag
            'store': False
        }

        # Hash size as (width, height)
        hash_size = [8 * self.capture_ar, 8]
        # Round down width to multiple of 2
        hash_size[0] = int(hash_size[0] - hash_size[0] % 2)
        # Hashes for currently playing episode
        self.hashes = HashStore(
            version='0.1',
            hash_size=hash_size,
            seasonid=self.state.season_identifier,
            episode=utils.get_int(self.state.episode),
            # Representative hash of centred end credits text on a dark
            # background stored as first hash
            data={self.hash_index['credits']: (
                [0] * hash_size[0]
                + (
                    (
                        [0] * (4 * hash_size[0] // 16)
                        + [1] * (hash_size[0] - 2 * (4 * hash_size[0] // 16))
                        + [0] * (4 * hash_size[0] // 16)
                    )
                    + (
                        [0] * (6 * hash_size[0] // 16)
                        + [1] * (hash_size[0] - 2 * (6 * hash_size[0] // 16))
                        + [0] * (6 * hash_size[0] // 16)
                    )
                ) * ((hash_size[1] - 2) // 2)
                + [0] * hash_size[0]
            )},
            timestamps={}
        )

        # Calculated maximum allowable significant level
        # self.significance_level = 0.90 * self.calc_significance(
        #    self.hashes.data[self.hash_index['credits']]
        # )
        self.significance_level = 25

        # Hashes from previously played episodes
        self.past_hashes = HashStore(hash_size=hash_size)
        if self.hashes.is_valid():
            self.past_hashes.load(self.hashes.seasonid)

        # Number of consecutive frame matches required for a positive detection
        self.match_number = 5

        self.match_count['hits'] = 0
        self.match_count['misses'] = 0
        self.credits_detected = False

    def run(self):
        """Detection loop captures Kodi render buffer every 1s to create an
           image hash. Hash is compared to the previous hash to determine
           whether current frame of video is similar to the previous frame.

           Hash is also compared to hashes calculated from previously played
           episodes to detect common sequence of frames (i.e. credits).

           A consecutive number of matching frames must be detected to confirm
           that end credits are playing."""

        self.log('Started')
        self.running = True

        if self.state.detector_profile:
            import cProfile
            import pstats
            try:
                from StringIO import StringIO
            except ImportError:
                from io import StringIO

            profiler = cProfile.Profile()
            profiler.enable()

        monitor = xbmc.Monitor()
        while (not monitor.abortRequested()
               and not (self.sigterm or self.sigstop)):
            now = timeit.default_timer()

            with self.player as check_fail:
                play_time = self.player.getTime()
                self.hash_index['store'] = self.state.detect_time <= play_time
                self.hash_index['current'] = (
                    int(self.player.getTotalTime() - play_time),
                    self.hashes.episode
                )
                # Only capture if playing at normal speed
                # check_fail = self.player.get_speed() != 1
                check_fail = False
            if check_fail:
                self.log('No file is playing')
                break

            self.capturer.capture(*self.capture_size)
            image = self.capturer.getImage()

            # Capture failed or was skipped, re-initialise RenderCapture
            if not image or image[-1] != 255:
                continue

            # Convert captured image data from BGRA to RGBA
            image[0::4], image[2::4] = image[2::4], image[0::4]
            # Convert to greyscale to reduce size of data by a factor of 4
            image = Image.frombuffer(
                'RGBA', self.capture_size, image, 'raw', 'RGBA', 0, 1
            ).convert('L')
            # Resize to reduce number of pixels processed for hashing
            if self.hashes.hash_size != self.capture_size:
                image = image.resize(self.hashes.hash_size, resample=Image.BOX)

            # Transform image to show absolute deviation from median pixel luma
            median_pixel = self.calc_quartiles(image.getdata())[1]
            image_hash = image.point(
                [abs(i - median_pixel) for i in range(256)]
            )

            # Calculate median absolute deviation from the median to represent
            # significant pixels and use transformed image as the hash of the
            # current video frame
            median_pixel = self.calc_quartiles(image_hash.getdata())[1]
            image_hash = image_hash.point(
                [i > median_pixel for i in range(256)]
            )
            image_hash = tuple(image_hash.getdata())

            # Check if current hash matches with previous hash, typical end
            # credits hash, or other episode hashes
            stats = self.check_similarity(
                image_hash, self.match_number
            )

            # Increment the number of matches
            if stats['is_match']:
                self.match_count['hits'] += 1
                self.match_count['misses'] = 0
            # Otherwise increment number of mismatches
            elif not stats['possible_match']:
                self.match_count['misses'] += 1
            # If 3 mismatches in a row (to account for bad frame capture), then
            # reset match count
            if self.match_count['misses'] > 2:
                self.match_count['hits'] = 0
                self.match_count['misses'] = 0

            if self.state.detector_debug:
                self.print_hash(
                    self.hashes.data.get(self.hash_index['credits']),
                    image_hash,
                    self.hashes.hash_size,
                    (
                        'Hash compare: {0:2.1f}% similar to typical credits'
                    ).format(stats['credits'])
                )

                self.print_hash(
                    self.hashes.data.get(self.hash_index['previous']),
                    image_hash,
                    self.hashes.hash_size,
                    (
                        'Hash compare: {0:2.1f}% similar to previous frame'
                        ' with {1:2.1f}% significant pixels'
                    ).format(stats['previous'], stats['significance'])
                )

                self.print_hash(
                    self.past_hashes.data.get(self.hash_index['episodes']),
                    image_hash,
                    self.hashes.hash_size,
                    (
                        'Hash compare: {0:2.1f}% similar to other episodes'
                    ).format(stats['episodes'])
                )

                self.log('Hash compare: completed in {0:1.4f}s'.format(
                    timeit.default_timer() - now
                ))

            # Store current hash for comparison with next video frame
            # But delete previous hash if not yet required to save it
            if not self.hash_index['store'] and self.hash_index['previous']:
                del self.hashes.data[self.hash_index['previous']]
            self.hashes.data[self.hash_index['current']] = image_hash
            self.hash_index['previous'] = self.hash_index['current']

            monitor.waitForAbort(max(0.1, 1 - timeit.default_timer() + now))

            if self.state.detector_profile:
                profiler.disable()
                output_stream = StringIO()
                pstats.Stats(
                    profiler,
                    stream=output_stream
                ).sort_stats('cumulative').print_stats()
                self.log(output_stream.getvalue())
                output_stream.close()

        # Free resources
        del monitor

        # Reset thread signals
        self.log('Stopped')
        self.running = False
        self.sigstop = False
        self.sigterm = False

    def start(self, restart=False, resume=False):
        """Method to run actual detection test loop in a separate thread"""

        if restart or self.running:
            self.stop()
        if resume:
            self.match_count['hits'] = 0
            self.match_count['misses'] = 0
            self.credits_detected = False
        # Reset detector data if episode has changed
        if not self.hashes.is_valid(
                self.state.season_identifier,
                utils.get_int(self.state.episode)
        ):
            self.init_hashes()

        self.thread = threading.Thread(target=self.run)
        # Daemon threads may not work in Kodi, but enable it anyway
        self.thread.daemon = True
        self.thread.start()

    def stop(self, reset=False, terminate=False):
        # Exit if detector thread has not been created
        if not self.thread:
            return

        # Set terminate or stop signals if detector is running
        if terminate:
            self.sigterm = self.running
        else:
            self.sigstop = self.running

        # Wait for thread to complete
        if self.running:
            self.thread.join()

        # Free resources
        del self.thread
        self.thread = None

        # Invalidate collected hashes if not needed for later use
        if reset or terminate:
            self.hashes.invalidate()
        # Delete reference to instances if detector will not be restarted
        if terminate:
            del self.capturer
            self.capturer = None
            del self.player
            self.player = None
            del self.state
            self.state = None

    def store_data(self):
        # Only store data for videos that are grouped by season (i.e. same show
        # title, same season number)
        if not self.hashes.is_valid():
            return

        self.past_hashes.hash_size = self.hashes.hash_size
        # If credit were detected only store the previous 5s worth of hashes to
        # reduce false positives when comparing to other episodes
        if self.credits_detected:
            detect_offset = self.hash_index['detected_at'] + self.match_number
            self.past_hashes.data.update({
                hash_index: self.hashes.data[hash_index]
                for hash_index in self.hashes.data
                if hash_index[0] <= detect_offset
            })
            self.past_hashes.timestamps.update(self.hashes.timestamps)
        # Otherwise store all hashes for comparison with other episodes
        else:
            self.past_hashes.data.update(self.hashes.data)

        self.past_hashes.save(self.hashes.seasonid)

    def update_timestamp(self, play_time):
        # Return current playtime if credits were detected
        if self.credits_detected:
            self.hash_index['detected_at'] = self.hash_index['current'][0]
            self.hashes.timestamps[self.hashes.episode] = play_time
            return play_time
        # Otherwise return previously detected timestamp
        return self.past_hashes.timestamps.get(self.hashes.episode)
