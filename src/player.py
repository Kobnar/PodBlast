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
        print ('...Creating Gstreamer engine.')
        self.engine = Gst.ElementFactory.make('playbin', 'player')
        self.engine.set_property(
            'audio-sink',
            Gst.ElementFactory.make('pulsesink', 'pulse'
                )
            )

        # Instantiates the 'GStreamer' 'bus':
        print ('...Creating Gstreamer bus.')
        bus = self.engine.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        # bus.connect('message', self.gst_message_handler)

        print ('...Defining custom player state handler.')
        # Defines our own state handler for 'GStreamer':
        self.player_state = 'NULL'
        self.channel_url = 'NULL'

    # Sets the current channel url:
    def set (self, channel_url):
        self.engine.set_property('uri', channel_url)
        self.channel_url = channel_url
        print ('Stream URL set to "' + channel_url + '"')

    # Begins streaming playback:
    def play (self):
        if self.channel_url is 'NULL':
            print ('Please set a media source to stream.')
        else:
            self.engine.set_state(Gst.State.PLAYING)
            self.player_state = 'PLAYING'
            print ('Stream is now playing. (' + self.player_state + ')')

    # Pauses current playback (in-place):
    def pause (self):
        self.engine.set_state(Gst.State.PAUSED)
        self.player_state = 'PAUSED'
        print ('Stream is now paused. (' + self.player_state + ')')

    # Stops current playback (reset):
    def stop (self):
        self.engine.set_state(Gst.State.READY)
        self.player_state = 'READY'
        print ('Stream is now stopped. (' + self.player_state + ')')
        self.set('NULL')

    # Nullifies the stream (for application shutdown):
    def null (self):
        self.engine.set_state(Gst.State.NULL)
        self.player_state = 'NULL'
        self.set('NULL')
        print ('Stream is nullified. (' + self.player_state + ')')