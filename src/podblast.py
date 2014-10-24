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

#------------------------------------------------------------------------------#

class PodBlast (
    database.Database,
    player.Player,
    gtkinterface.GTKInterface,
    gtkhandler.GTKSignalHandler ):
    """
    The "core" PodBlast class with all of the necessary implementatons to fetch
    data from a remote feed, save/load data from CSV files, set and control a
    streaming audio, and interface with the PodBlast GTK/Glade frontend.
    """
    def __init__(self):
        # try:
            self.feeds = self.load_feeds()
        # except:
        #     print ("Failed to load feeds.")