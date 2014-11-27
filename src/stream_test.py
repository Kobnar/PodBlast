
import os
import unittest
import time
from stream import Stream
from gi.repository import Gst

class TestStream(unittest.TestCase):

    def setUp(self):
        self.test_audio_uri = 'file://' + os.path.abspath("tests/test_audio.mp3")
        self.bad_uri = 'htg.11/23.p'
        self.stream = Stream()

    def test_init(self):
        # Ensures the object was instantiated to a safe state.
        self.assertEqual('NULL', self.stream.player_state)
        self.assertEqual('NULL', self.stream.channel_url)
        self.assertEqual(None, self.stream.engine.get_property('current-uri'))
        self.assertEqual(None, self.stream.engine.get_property('uri'))
        self.assertEqual(Gst.State.NULL,
            self.stream.engine.get_state(Gst.CLOCK_TIME_NONE)[1])

    def test_set(self):
        # Ensures that 'set()' method correctly sets the state url and the
        # GStreamer sink.
        self.stream.set(self.test_audio_uri)
        self.assertEqual(self.test_audio_uri, self.stream.channel_url)
        self.assertEqual(self.test_audio_uri,
            self.stream.engine.get_property('uri'))

    def test_set_with_bad_uri(self):
        # Ensures that a stream is not set if a bad url is passed.
        self.stream.set(self.bad_uri)
        self.assertEqual('NULL', self.stream.channel_url)
        self.assertEqual(None, self.stream.engine.get_property('uri'))

    def test_play_without_set(self):
        # Ensures that nothing happens if play is called on a 'NULL' stream.
        self.stream.play()
        time.sleep(1)
        self.assertEqual('NULL', self.stream.player_state)
        self.assertEqual(Gst.State.NULL,
            self.stream.engine.get_state(Gst.CLOCK_TIME_NONE)[1])

    def test_set_and_play(self):
        # Ensures that the player state is updated when it is properly set and
        # called to start playing.
        self.stream.set(self.test_audio_uri)
        self.stream.play()
        time.sleep(2)
        self.assertEqual('PLAYING', self.stream.player_state)
        self.assertEqual(Gst.State.PLAYING,
            self.stream.engine.get_state(Gst.CLOCK_TIME_NONE)[1])

    def test_pause(self):
        # Ensures the player pauses correctly.
        self.stream.set(self.test_audio_uri)
        self.stream.play()
        time.sleep(2)
        self.stream.pause()
        time.sleep(2)
        self.assertEqual('PAUSED', self.stream.player_state)
        self.assertEqual(Gst.State.PAUSED,
            self.stream.engine.get_state(Gst.CLOCK_TIME_NONE)[1])

    # def test_pause_without_play(self):
    #     # Not sure what this SHOULD do.
    #     self.assertTrue(False)

    # def test_stop(self):
    #     self.assertTrue(False)

    # def test_null(self):
    #     self.assertTrue(False)

    # def test_ffwd(self):
    #     self.assertTrue(False)

    # def test_rwnd(self):
    #     self.assertTrue(False)

    # def test_get_position(self):
    #     self.assertTrue(False)

    # def test_set_position(self):
    #     self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()