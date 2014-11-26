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
import pbutils
import podblast
import gtkinterface
try:
    from gi.repository import GObject
except:
    print ("Error: Failed to load GObject bindings for Python.")
    sys.exit(1)

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

        # Connecting signnal handlers:
        self.ux.gtk_builder.connect_signals(self)
        self.on_position_changed_id = self.ux.time_scale_adjustment.connect(
            'value_changed', self.on_position_changed)

        # Define timeout loops to update the GUI:
        self.slider_timeout = GObject.timeout_add(100, self.refresh_controls)

    # Populates all of the GUI data before starting the GTK+ loop:
    def main (self):
        self.pb.load()
        self.rebuild_feed_list()
        self.rebuild_episode_list()
        self.ux.main()

    def main_quit (self):
        self.null()
        self.pb.save()
        self.ux.main_quit()

    #---------------- ----- --- --- - - - -  -     -
    # Front-end signals:

    def on_main_window_delete_event (self, widget, *args):
        print('----------------- on_main_window_delete_event ------------------')
        self.main_quit()

    def on_about (self, *args):
        print('-------------------------- on_about ----------------------------')
        self.ux.about_dialog.show()

    def on_about_close_button_clicked (self, button):
        print('---------------- on_about_close_button_clicked -----------------')
        self.ux.about_dialog.hide()

    def on_new (self, *args):
        print('--------------------------- on_new -----------------------------')
        # Reset database:
        self.pb.feeds = []
        self.pb.file_path = self.pb.default_file_path
        self.set(None, None)
        # Refresh GUI:
        self.rebuild_feed_list()
        self.rebuild_episode_list()
        self.ux.set_player_buttons()

    def on_load (self, *args):
        print('--------------------------- on_load ----------------------------')
        file_path = self.ux.load_dialog()
        if file_path != None:
            self.pb.file_path = file_path
            self.pb.load(self.pb.file_path)
            self.pb.stop()
            # Refresh GUI:
            self.rebuild_feed_list()

    def on_save (self, *args):
        print('--------------------------- on_save ----------------------------')
        self.pb.save(self.pb.file_path)
        self.ux.error_dialog('Subscription list saved.')

    def on_saveas (self, *args):
        print('-------------------------- on_saveas ---------------------------')
        file_path = self.ux.save_dialog()
        if file_path != None:
            self.pb.file_path = file_path
            self.pb.save(self.pb.file_path)
            self.ux.error_dialog('Subscription list saved.')

    def on_add_feed (self, button):
        print('------------------------- on_add_feed --------------------------')
        self.ux.add_feed_show()

    def on_add_feed_ok_clicked (self, button):
        print('------------------- on_add_feed_ok_clicked ---------------------')
        feed_url = pbutils.validate_url(
            self.ux.get_add_feed_url()
            )
        if feed_url:
            self.pb.register_feed(feed_url)
            self.ux.add_feed_hide()
            self.rebuild_feed_list()
        else:
            self.ux.error_dialog ('Invalid URL')

    def on_add_feed_cancel_clicked (self, button):
        print('----------------- on_add_feed_cancel_clicked -------------------')
        self.ux.add_feed_hide()

    def on_refresh_feeds (self, *args):
        print('---------------------- on_refresh_feeds ------------------------')
        self.ux.error_dialog('Refresh not yet implemented.')

    def on_configure_feeds (self, *args):
        print('--------------------- on_configure_feeds -----------------------')
        self.ux.error_dialog('Feed configuration not yet implemented.')

    def on_feed_combo_changed (self, feed_combo):
        print('-------------------- on_feed_combo_changed ---------------------')
        # Gets the new feed pkid from the GUI and sets the tracker:
        feed_pkid = self.ux.get_feed_pkid()
        self.set(feed_pkid, None)
        self.rebuild_episode_list()

    def on_episode_treeview_row_activated (self, *args):
        print('-------------- on_episode_treeview_row_activated ---------------')
        # Get PKID data from GUI:
        feed_pkid = self.ux.actv_feed_pkid
        episode_pkid = self.ux.get_epsd_pkid()
        # Set PKID data and start playing:
        self.set(feed_pkid, episode_pkid)
        self.play()

    def on_play_button_clicked (self, button):
        print('-------------------- on_play_button_clicked --------------------')
        if self.pb.actv_epsd_pkid != None:
            # If an episode is already active, trigger the play/pause function:
            self.play_pause()
        else:
            # ...otherwise gets PKID data from GUI:
            feed_pkid = self.ux.actv_feed_pkid
            episode_pkid = self.ux.get_epsd_pkid()
            # ...and sets PKID Data and then starts playing:
            self.set(feed_pkid, episode_pkid)
            self.play_pause()

    def on_stop_button_clicked (self, button):
        print('-------------------- on_stop_button_clicked --------------------')
        self.stop()

    def on_next_button_clicked (self, button):
        print('-------------------- on_next_button_clicked --------------------')
        self.next()

    def on_prev_button_clicked (self, button):
        print('-------------------- on_prev_button_clicked --------------------')
        self.prev()

    def on_ffwd_button_clicked (self, button):
        print('-------------------- on_ffwd_button_clicked --------------------')
        self.ffwd()

    def on_rwnd_button_clicked (self, button):
        print('-------------------- on_rwnd_button_clicked --------------------')
        self.rwnd()

    def on_position_changed (self, slider):
        print('--------------------- on_position_changed ----------------------')
        new_position = self.ux.get_time_scale_position()
        self.pb.set_position(new_position)

    #---------------- ----- --- --- - - - -  -     -
    # GUI timout loop to refresh slider and controls (stops the update to allow
    # seeking via slider):

    def refresh_controls (self):
        # Gets position data from back-end:
        position_data = self.pb.get_position()
        # Blocks position signal:
        self.ux.time_scale_adjustment.handler_block(
            self.on_position_changed_id)
        # Sets time:
        self.ux.set_time_scale(position_data)
        # Unblocks position signal:
        self.ux.time_scale_adjustment.handler_unblock(
            self.on_position_changed_id)
        return True

    #---------------- ----- --- --- - - - -  -     -
    # Front- and back-end component synchronization:

    def sync_ux_state (self):
        print ('GTKHandler\tSyncronizing front-end state.')
        self.ux.actv_feed_pkid = self.pb.actv_feed_pkid
        self.ux.actv_epsd_pkid = self.pb.actv_epsd_pkid
        self.ux.player_state = self.pb.get_player_state()
        self.ux.actv_epsd_duration = self.pb.get_position()[1]

    #---------------- ----- --- --- - - - -  -     -
    # Player control connections:

    def set (self, feed_pkid, episode_pkid):
        print ('GTKHandler:\tSetting new PKID pair: [',
            feed_pkid, ', ', episode_pkid, ']')
        self.pb.set(feed_pkid, episode_pkid)
        self.sync_ux_state()

    def play_pause (self):
        self.pb.play_pause()
        self.sync_ux_state()
        self.ux.play_pause()

    def play (self):
        self.pb.play_pause()
        self.sync_ux_state()
        self.ux.play()

    def stop (self):
        self.pb.stop()
        self.sync_ux_state()
        self.ux.stop()

    def next (self):
        self.pb.next()
        self.sync_ux_state()
        self.ux.play()

    def prev (self):
        self.pb.prev()
        self.sync_ux_state()
        self.ux.play()

    def ffwd (self):
        self.pb.ffwd()

    def rwnd (self):
        self.pb.rwnd()

    def null (self):
        self.pb.null()
        self.sync_ux_state()
        self.ux.null()

    #---------------- ----- --- --- - - - -  -     -
    # GUI data population:

    # Collects feed data from the PodBlast back-end and passes it to the GTK
    # front-end so it can uprate the user interface.
    def rebuild_feed_list (self):
        if self.pb.feeds:
            feed_titles = []
            for index, feed in enumerate(self.pb.feeds):
                feed_titles.append([index, feed.title])
            self.ux.rebuild_feed_list(feed_titles)
        else:
            self.ux.feed_list.clear()

    # Collects episode data from the PodBlast back-end and passes it to the GTK
    # front-end so it can uprate the user interface.
    def rebuild_episode_list (self):
        if self.ux.actv_feed_pkid != None:
            self.ux.episode_treeview.set_sensitive(True)
            if self.pb.feeds[self.ux.actv_feed_pkid].episodes:
                episode_input = []
                for index, episode in enumerate(
                    self.pb.feeds[self.ux.actv_feed_pkid].episodes):
                    episode_input.append([
                        index,                  # Index
                        False,                  # isPlaying
                        episode.title,          # Title
                        episode.is_new,         # isNew
                        400,                    # FontWeight
                        'media-playback-start'  # IconName
                        ])
                self.ux.rebuild_episode_list(episode_input)
        else:
            self.ux.episode_treeview.set_sensitive(False)
            self.ux.episode_list.clear()

    # Does nothing right now.
    def refresh_time_scale (self):
        pass