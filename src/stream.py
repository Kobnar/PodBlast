#------------------------------------------------------------------------------#
#
#     Copyright 2014 by Konrad R.K. Ludwig.
#
#     This file is part of PodBlast.
#
#     PodBlast is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#     PodBlast is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#   along with PodBlast. If not, see <http://www.gnu.org/licenses/>.
#
#------------------------------------------------------------------------------#

import sys
try:
    # Loading Gst
    from gi.repository import Gst
    Gst.init(None)
except:
    print ("Error: Failed to load GStreamer bindings for Python.")
    sys.exit(1)

#------------------------------------------------------------------------------#

class Stream(object):
    """
    An implementation to stream remote audio using GStreamer. Provides the
    necessary methods to set a stream's url and control playback.
    """

    def __init__(self):
        print ('Initializing GStreamer interface.')

        # Instantiates the 'GStreamer' player 'engine' and defines the current
        #   output sink as 'pulseaudio':
        self.engine = Gst.ElementFactory.make('playbin', 'player')
        self.engine.set_property(
            'audio-sink',
            Gst.ElementFactory.make('pulsesink', 'pulse'
                )
            )

        # Instantiates the 'GStreamer' 'bus':
        bus = self.engine.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        bus.connect('message', self.gst_message_handler)

        # Defines our own state handler for 'GStreamer':
        self.player_state = 'NULL'
        self.channel_url = 'NULL'

    # Handler is disabled for now because I don't need it.
    def gst_message_handler (self, bus, message):
        # if message.type == Gst.MessageType.STATE_CHANGED:
        #     old, new, pending = message.parse_state_changed()
        # elif (message.type is Gst.MessageType.DURATION_CHANGED
        #     and (engine_state is Gst.State.PLAYING
        #         or engine_state is Gst.State.PAUSED)):
        #     print ('Stream:\t\tDuration changed and player can play.')
        #     self.refresh_duration()
        pass

    # Sets the current channel url:
    def set (self, channel_url):
        self.engine.set_property('uri', channel_url)
        self.channel_url = channel_url
        print ('Stream:\t\tStream URL set to "' + channel_url + '"')

    # Begins streaming playback:
    def play (self):
        print ('Stream:\t\tplay()')
        if self.channel_url is 'NULL':
            print ('Stream:\t\tPlease set a media source before calling Stream.play().')
        else:
            self.engine.set_state(Gst.State.PLAYING)
            self.player_state = 'PLAYING'

    # Pauses current playback (in-place):
    def pause (self):
        print ('Stream:\tpause()')
        self.engine.set_state(Gst.State.PAUSED)
        self.player_state = 'PAUSED'

    # Stops current playback (reset):
    def stop (self):
        print ('Stream:\t\tstop()')
        self.engine.set_state(Gst.State.READY)
        self.player_state = 'READY'
        self.set('NULL')

    # Nullifies the stream (for application shutdown):
    def null (self):
        print ('Stream:\t\tnull()')
        self.engine.set_state(Gst.State.NULL)
        self.player_state = 'NULL'
        self.set('NULL')

    # Skips forward 30 seconds.
    def ffwd (self):
        duration, position = self.get_position()
        position += 30
        self.set_position(position)

    # Skips backward 30 seconds.
    def rwnd (self):
        duration, position = self.get_position()
        position -= 30
        self.set_position(position)

    # Returns a tuple with the position and the duration of the stream:
    def get_position (self):
        # Perform duration query:
        duration_query = self.engine.query_duration(Gst.Format.TIME)
        if duration_query[0]:
            duration = duration_query[1] / Gst.SECOND
        else:
            duration = 0
        # Perform position query:
        position_query = self.engine.query_position(Gst.Format.TIME)
        if position_query[0]:
            position = position_query[1] / Gst.SECOND
        else:
            position = 0
        # Return both.
        # print ('Stream:\t\t[', position, ',', duration, ']')
        return (duration, position)

    # Sets the feed to an arbitrary position (in seconds):
    def set_position (self, raw_seconds):
        self.engine.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, raw_seconds * Gst.SECOND)