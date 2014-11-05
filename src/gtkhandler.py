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

import pbutils
import podblast
import gtkinterface

#------------------------------------------------------------------------------#
# NOTE:
#     This class handles the signals sent to the PodBlast back-end by its
#   GTK/Glade front-end. It is not designed to invoke or require any GTK/Glade
#   libraries. All members/methods requiring GTK/Glade libraries to work are
#   defined in 'src/gtkinterface.py' and accessed using the user interface
#   component 'ux'.
#------------------------------------------------------------------------------#

class GTKHandler(object):
    """
    The link between the PodBlast front-end and the PodBlast back-end objects.
    Takes signals from the front-end and syncronizes events with the back-end.
    """
    def __init__(self):
        print ('Initializing GTK signal handler...')
        # Instantiates and connects GTK/Glade user interface component:
        self.pb = podblast.PodBlast()
        self.ux = gtkinterface.GTKInterface()

        print ('...Connecting front-end signals to back-end methods.')
        # Player controls:
        self.ux.gtk_builder.connect_signals(self)

    # Populates all of the GUI data before starting the GTK+ loop:
    def main (self):
        self.rebuild_feed_list()
        self.refresh_player_buttons()
        self.ux.main()

    #---------------- ----- --- --- - - - -  -     -
    # Front-end signals:

    def on_main_window_delete_event (self, widget, *args):
        self.pb.stream.null()
        self.ux.main_quit()

    def on_about (self, *args):
        self.ux.about_dialog.show()

    def on_about_close_button_clicked (self, button):
        self.ux.about_dialog.hide()

    def on_new (self, *args):
        # Reset database:
        self.pb.feeds = []
        self.pb.set(None, None)
        self.pb.file_path = self.default_file_path
        # Refresh GUI:
        self.rebuild_feed_list()
        self.rebuild_episode_list()
        self.refresh_player_buttons()

    def on_load (self, *args):
        file_path = self.ux.load_dialog()
        if file_path != None:
            self.pb.file_path = file_path
            self.pb.load(self.pb.file_path)
            self.pb.stop()
            # Refresh GUI:
            self.rebuild_feed_list()
            self.rebuild_episode_list()
            self.refresh_player_buttons()

    def on_save (self, *args):
        self.pb.save(self.pb.file_path)

    def on_saveas (self, *args):
        file_path = self.ux.save_dialog()
        if file_path != None:
            self.pb.file_path = file_path
            self.pb.save(self.pb.file_path)

    def on_add_feed (self, button):
        self.ux.add_feed_show()

    def on_add_feed_ok_clicked (self, button):
        feed_url = pbutils.validate_url(
            self.ux.get_add_feed_url()
            )
        if feed_url:
            self.pb.register_feed(feed_url)
            self.ux.add_feed_hide()
            self.rebuild_feed_list()
            self.refresh_player_buttons()
        else:
            self.ux.error_dialog ('Invalid URL')

    def on_add_feed_cancel_clicked (self, button):
        self.ux.add_feed_hide()

    def on_refresh_feeds (self, *args):
        self.ux.error_dialog('Refresh not yet implemented.')

    def on_configure_feeds (self, *args):
        self.ux.error_dialog('Feed configuration not yet implemented.')

    def on_feed_combo_changed (self, feed_combo):
        # Gets the new feed pkid from the GUI and sets the tracker:
        self.ux.actv_feed_pkid = self.ux.get_feed_pkid()
        self.pb.stop()
        # Refreshes episode treeview:
        self.rebuild_episode_list()
        # self.ux.refresh_episode_list(self.ux.actv_epsd_pkid)

    def on_episode_treeview_row_activated (self, *args):
        # Get the PKIDs for the selected feed and episode:
        feed_pkid = self.ux.actv_feed_pkid
        episode_pkid = self.ux.get_epsd_pkid()
        self.ux.actv_epsd_pkid = episode_pkid
        # Update back-end:
        self.pb.set(feed_pkid, episode_pkid)
        self.pb.play_pause()
        # Update front-end:
        self.ux.mark_old()
        self.ux.refresh_episode_list(self.pb.actv_epsd_pkid)
        self.refresh_player_buttons()

    def on_play_button_clicked (self, button):
        if self.pb.actv_epsd_pkid != None:
            self.pb.play_pause()
            self.ux.mark_old()
            self.refresh_player_buttons()
        else:
            episode_pkid = self.ux.get_epsd_pkid()
            self.pb.actv_epsd_pkid = episode_pkid
            self.ux.actv_epsd_pkid = episode_pkid
            self.pb.reset()
            self.pb.play_pause()
            self.ux.mark_old()
            self.ux.refresh_episode_list(self.pb.actv_epsd_pkid)
            self.refresh_player_buttons()

    def on_stop_button_clicked (self, button):
        self.pb.stop()
        self.ux.stop()
        self.refresh_player_buttons()

    def on_next_button_clicked (self, button):
        self.pb.next()
        self.ux.next()
        self.refresh_player_buttons()

    def on_prev_button_clicked (self, button):
        self.pb.prev()
        self.ux.prev()
        self.refresh_player_buttons()

    def on_rwnd_button_clicked (self, button):
        print ('Rewind feature not yet implemented.')

    def on_ffwd_button_clicked (self, button):
        print ('Rewind feature not yet implemented.')

    #---------------- ----- --- --- - - - -  -     -
    # Refreshing/Rebuilding front-end components based on back-end data:

    def rebuild_feed_list (self):
        # TODO: Need test to pass subscribed feeds only.
        if self.pb.feeds:
            feed_titles = []
            for index, feed in enumerate(self.pb.feeds):
                feed_titles.append([index, feed.title])
            self.ux.rebuild_feed_list(feed_titles)
        else:
            self.ux.feed_list.clear()

    def rebuild_episode_list (self):
        if self.ux.actv_feed_pkid != None:
            if self.pb.feeds[self.ux.actv_feed_pkid].episodes:
                episode_input = []
                for index, episode in enumerate(
                    self.pb.feeds[self.ux.actv_feed_pkid].episodes
                    ):
                    episode_input.append([
                        index,              # Index
                        False,              # isPlaying
                        episode.title,      # Title
                        episode.is_new,     # isNew
                        400                 # FontWeight
                        ])
                self.ux.rebuild_episode_list(episode_input)
                self.ux.refresh_episode_list(self.ux.actv_feed_pkid)
        else:
            self.ux.episode_list.clear()

    def refresh_player_buttons (self):
        state = self.pb.stream.player_state
        if self.pb.actv_feed_pkid == None:
            self.ux.set_player_buttons('DEAD')
        elif self.pb.actv_epsd_pkid != None:
            if state == 'NULL':
                self.ux.set_player_buttons('NULL')
            elif state == 'READY':
                self.ux.set_player_buttons('READY')
            elif state == 'PAUSED':
                self.ux.set_player_buttons('PAUSED')
            elif state == 'PLAYING':
                self.ux.set_player_buttons('PLAYING')
        else:
            self.ux.set_player_buttons('NULL')