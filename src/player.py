#------------------------------------------------------------------------------#\
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

import pygst
pygst.require("0.10")
import gst

#------------------------------------------------------------------------------#

class Player(object):
    """
    An implementation to stream remote audio with GStreamer. Provides the
    necessary methods to set a stream's url and control playback.
    """

    def __init__(self):
        # Instantiates the 'GStreamer' player "engine" and defines the current
        #   output sink as 'pulseaudio':
        self.engine = gst.element_factory_make("playbin", "player")
        self.engine.set_property(
            "audio-sink",
            gst.element_factory_make("pulsesink", "pulse"
                )
            )
        # Instantiates the 'GStreamer' "bus":
        bus = self.engine.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        bus.connect('message', self.gst_message_handler)
        # Defines our own state handler for 'GStreamer':
        self.player_state = "NULL"

    # Bus message handler (triggers 'refresh_player_state()'):
    def gst_message_handler(self, bus, message):
        if message.type == gst.MESSAGE_STATE_CHANGED:
            old, new, pending = message.parse_state_changed()
            self.refresh_player_state(new)

    # Syncs 'player_state' with the GStreamer bus:
    def refresh_player_state (self, state_msg):
        if state_msg == gst.STATE_NULL:
            self.player_state = "NULL"
        elif state_msg == gst.STATE_READY:
            self.player_state = "READY"
        elif state_msg == gst.STATE_PAUSED:
            self.player_state = "PAUSED"
        elif state_msg == gst.STATE_PLAYING:
            self.player_state = "PLAYING"

    # Sets the current channel url:
    def set (self, channel_url):
        self.engine.set_property('uri', channel_url)

    # Basic play/pause function based on 'player_state':
    def play_pause (self):
        if self.player_state is not "PLAYING":
            self.engine.set_state(gst.STATE_PLAYING)
        else:
            self.pause()

    # Begins streaming playback:
    def play (self):
        self.engine.set_state(gst.STATE_PLAYING)

    # Pauses current playback (in-place):
    def pause (self):
        self.engine.set_state(gst.STATE_PAUSED)

    # Stops current playback (reset):
    def stop (self):
        self.engine.set_state(gst.STATE_READY)