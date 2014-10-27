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

import database
import player
import gtkinterface
import gtkhandler

#------------------------------------------------------------------------------#

class PodBlast (database.Database, gtkhandler.GTKHandler):
    """
    The "core" PodBlast class with all of the necessary implementatons to fetch
    data from a remote feed, save/load data from CSV files, set and control a
    streaming audio, and interface with the PodBlast GTK/Glade frontend.
    """
    def __init__(self):
        print ("Initializing PodBlast.")
        database.Database.__init__(self)
        # gtkinterface.GTKInterface.__init__(self)
        self.stream = player.Player()
        # State tracking:
        self.feed_pkid = None
        self.episode_pkid = None

    def main (self):
        self.gtk_builder.connect_signals(self)
        self.refresh_subscr_list()
        gtk.main()

    #---------------- ----- --- --- - - - -  -     -
    # Player controls:

    def set (self, feed_pkid, episode_pkid):
        self.feed_pkid = feed_pkid
        self.episode_pkid = episode_pkid
        self.reset()

    def reset(self):
        feed = self.feeds[self.feed_pkid]
        episode = feed.episodes[self.episode_pkid]
        media_url = episode.media[0]
        self.stream.stop()
        self.stream.set(media_url)

    def play_pause (self):
        self.stream.play_pause()

    def stop (self):
        self.stream.stop()

    def next (self):
        self.episode_pkid += 1
        self.reset()
        self.play_pause()

    def prev (self):
        self.episode_pkid -= 1
        self.reset()
        self.play_pause()