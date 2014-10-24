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

import sys
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
    import pango
except:
    sys.exit(1)

#------------------------------------------------------------------------------#

class GTKInterface(object):
    """
    An implementation to link the GTK/Glade user interface with the PodBlast
    backend as a collection of python objects. It also provides a collection of
    methods to handle signals from the frontend.
    """

    def __init__(self):
        #--------- -- -- - - -- -  -   -  -      -  -      -
        # User Interface Construction:
        #--------- -- -- - - -- -  -   -  -      -  -      -

        # Define the location of our glade interface file as 'ux_source' and
        # set up the GTK builder to grab objects and signals from that file:
        ux_source = "ux/podblast_ux.glade"
        gtk_builder = gtk.Builder()
        gtk_builder.add_from_file(self.ux_source)

        # Get the window/dialog objects:
        self.main_window = self.gtk_builder.get_object("MainWindow")
        self.add_feed_diag = self.gtk_builder.get_object("AddFeedDiag")
        self.err_diag = self.gtk_builder.get_object("ErrDiag")
        self.confirm_diag = self.gtk_builder.get_object("ConfirmDiag")

        #--------- -- -- - - -- -  -   -  -      -  -      -
        # "MainWindow" Objects:
        #--------- -- -- - - -- -  -   -  -      -  -      -

        # "FeedsTab":
        # self.feed_list = self.gtk_builder.get_object("FeedList")
        self.subscr_treeview = self.gtk_builder.get_object("SubscrTreeview")
        self.subscr_list = self.gtk_builder.get_object("SubscriptionList")
        # Popup Menu:
        self.feed_menu = self.gtk_builder.get_object("FeedMenu")
        self.feed_menu_split = self.gtk_builder.get_object("FeedMenuSplit")
        self.feed_menu_edit = self.gtk_builder.get_object("FeedMenuEdit")
        self.feed_menu_del = self.gtk_builder.get_object("FeedMenuDel")

        # "EpisodesTab":
        self.active_feed_label = self.gtk_builder.get_object("ActiveFeedLabel")
        self.episode_treeview = self.gtk_builder.get_object("EpisodesTreeview")
        self.episode_list = self.gtk_builder.get_object("EpisodesList")

        # "PlaylistTab":
        self.playlist_treeview = self.gtk_builder.get_object("PlaylistTreeview")
        self.playlist_list = self.gtk_builder.get_object("PlaylistList")

        # "FavoritesTab":

        # "DownloadsTab":

        # "TrashTab":

        # "Player" Bar:
        self.play_img = self.gtk_builder.get_object("PlayImg")
        self.play_button = self.gtk_builder.get_object("PlayButton")
        self.stop_button = self.gtk_builder.get_object("StopButton")
        self.ffwd_button = self.gtk_builder.get_object("FfwdButton")
        self.rwnd_button = self.gtk_builder.get_object("RwndButton")
        self.ffwd_button = self.gtk_builder.get_object("NextButton")
        self.prev_button = self.gtk_builder.get_object("PrevButton")

        #--------- -- -- - - -- -  -   -  -      -  -      -
        # "AddFeedDiag" Objects:
        #--------- -- -- - - -- -  -   -  -      -  -      -

        self.ap_url_entry = self.gtk_builder.get_object("AddPodcastURLEntry")

        #--------- -- -- - - -- -  -   -  -      -  -      -
        # "ErrDiag" Objects:
        #--------- -- -- - - -- -  -   -  -      -  -      -

        self.err_diag_label = self.gtk_builder.get_object("ErrDiagLabel")

        #--------- -- -- - - -- -  -   -  -      -  -      -
        # "ConfirmDiag" Objects:
        #--------- -- -- - - -- -  -   -  -      -  -      -

        self.confirm_diag_label = self.gtk_builder.get_object("ConfirmDiagLabel")
        self.confirm_diag_confirm_button = self.gtk_builder.get_object("ConfirmDiagConfirm")
        self.confirm_diag_cancel_button = self.gtk_builder.get_object("ConfirmDiagCancel")

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Window Handling:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def onDeleteMainWindow(self, *args):
        # Stop, save and quit:
        self.save_feeds()
        self.pb.ux.end_program(*args)

    def onDeleteAddFeedDiag(self, *args):
        self.close_add_feed_diag()
        return True

    def close_add_feed_diag(self):
        # Close dialogue and empty fields:
        self.pb.ux.add_feed_diag.hide()
        self.pb.ux.ap_url_entry.set_text("")

    def onDeleteErrDiag(self, *args):
        self.pb.ux.err_diag.hide()
        self.pb.ux.err_diag_label.set_text("")
        return True

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Player Controls:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def onPlayPress(self, button):
        self.play_pause()

    def onStopPress(self, button):
        self.stop()

    # def onPrevPress(self, button):
    #   state.player.prev()

    # def onNextPress(self, button):
    #   state.player.next()

    # def onRwndPress(self, button):
    #   state.player.rwnd()

    # def onFfwdPress(self, button):
    #   state.player.ffwd()

    # def onMovePlayMeter(self, hscale):

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Feed Subscription Management:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def onAddFeed(self, button):
        self.pb.ux.add_feed_diag.show()

    def onAddFeedCancel(self, button):
        self.close_add_feed_diag()

    def onAddFeedAdd(self, button):
        subscribed = self.subscribe_feed()
        if subscribed == True:
            self.close_add_feed_diag()

    def onDeleteFeed(self, button):
        self.unsubscribe_feed()

    def onFeedActivate(self, treeview, iter, tvc):
        self.pb.feed_manager.activate()

    def onFeedRightClick(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, 0)
                self.pb.ux.feed_menu_split.set_visible(True)
                self.pb.ux.feed_menu_edit.set_visible(True)
                self.pb.ux.feed_menu_del.set_visible(True)
                self.pb.ux.feed_menu.popup( None, None, None, event.button, time)
            else:
                self.pb.ux.feed_menu_split.set_visible(False)
                self.pb.ux.feed_menu_edit.set_visible(False)
                self.pb.ux.feed_menu_del.set_visible(False)
                self.pb.ux.feed_menu.popup( None, None, None, event.button, time)
            return True

    def onFeedRefresh (self, button):
        print ("Feed refresh not yet implimented.")

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Episode Management:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def onEpisodeActivate (self, treeview, iter, tvc):
        self.pb.episode_manager.activate()

    def onEpisodeRefreshClicked (self, button):
        print ("Episode refresh not yet implimented.")

#------------------------------------------------------------------------------#

class TVManager:
    """
    A base class to manipulate visual aspects of front-end 'TreeView' objects.
    """
    def __init__(self, pb, treeview):
        # Link to pb parent element:
        self.pb = pb
        # Active 'treeview' status:
        self.treeview = treeview
        self.active_row = self.RowKeys(self.treeview, None)

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Child Class:
    #--------- -- -- - - -- -  -   -  -      -  -      -
    
    class RowKeys:
        """
        A simple object to provide a sensbile titlespace solution to
        linking back-end data to front-end 'TreeIter' objects. It is a cute little
        mini-helper for 'TreeManager'.
        """
        def __init__(self, treeview, row_iter):
            self.treeview = treeview
            self.row_iter = row_iter
            if self.row_iter == None:
                self.pkid = None
            else:
                self.pkid = self.treeview.get_model().get_value(self.row_iter, 0)

        def set (self, row_iter):
            if row_iter == None:
                self.row_iter = None
                self.pkid = None
            else:
                self.row_iter = row_iter
                self.pkid = self.treeview.get_model().get_value(row_iter, 0)

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # User Interface Row Activation/Deactivation:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def ux_activate (self):
        # Embolden the new row:
        select_iter = self.treeview.get_selection().get_selected()[1]
        self.treeview.get_model()[select_iter][-1] = pango.WEIGHT_BOLD
        # Update active 'treeview' row values:
        self.active_row.set(select_iter)

    def ux_deactivate (self):
        # Un-bold all rows in 'self.treeview':
        for row in self.treeview.get_model():
            row[-1] = pango.WEIGHT_NORMAL
        # Reset status variables:
        self.active_row.set(None)


class FeedManager (TVManager):
    """
    'FeedManager' handles 'feed_list'.
    """

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Menu Activation/Deactivation:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def activate (self):
        # If something is already active, deactivate it:
        if self.active_row.pkid is not None:
            self.deactivate()
        # Update user interface:
        self.ux_activate()
        # Update active feed status:
        self.pb.ux.update_feed_actvtn(self.active_row.pkid)


    ## !!! Dead code? !!!
    def deactivate (self):
        # Update user interface:
        self.ux_deactivate()
        # If the current row is active, deactivate it and clear
        # 'ux.episode_list':
        selectd_row = self.RowKeys(self.treeview, self.treeview.get_selection().get_selected()[1])
        if self.active_row.pkid == selectd_row.pkid:
            ux.episode_list.clear()

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Subscription/Unsubscription:
    #--------- -- -- - - -- -  -   -  -      -  -      -


    def validate_feed_url (self, feed_url):
        # This regex string pulled shamelessly from Django:
        regex_url = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        feed_url = re.match(regex_url, feed_url)
        if feed_url == None:
            self.pb.ux.throw_err_diag("Invalid URL.")
            return feed_url
        else:
            return feed_url.group(0)

    def subscribe (self):
        # Get and validate data from user interface:
        feed_url = self.validate_feed_url(
            self.pb.ux.ap_url_entry.get_text()
            )
        feed = self.pb.data.subscribe(feed_url)
        if feed is False:
            self.pb.ux.throw_err_diag("Feed not recognized.")
        elif feed is None:
            self.pb.ux.throw_err_diag("An active subscription with that URL already exists.")
            return False
        else:
            self.pb.ux.refresh_subscr_list()
            return True

    def unsubscribe (self):
        # Get the PKID of the current selection:
        select_iter = self.treeview.get_selection().get_selected()[1]
        subscr_pkid = self.pb.ux.subscr_treeview.get_model().get_value(select_iter, 0)
        # Deactivate any active rows:
        self.deactivate()
        # Pass data management to 'state.data':
        self.pb.data.unsubscribe(subscr_pkid)
        # Update the user interface:
        self.pb.ux.refresh_subscr_list()


class EpisodeManager (TVManager):

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Menu Activation/Deactivation:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def activate (self):
        # If something is already active, deactivate it:
        if self.active_row.pkid is not None:
            self.deactivate()
        # Update user interface:
        self.ux_activate()
        # Update state:
        self.pb.ux.update_episode_actvtn(self.active_row.pkid)
        # Set the new stream url:
        self.pb.player.set(self.pb.data.db["episodes"][self.active_row.pkid]["audio_url"])
        # Start playing podcast:
        self.pb.player.play()

    def deactivate (self):
        # Update user interface:
        self.ux_deactivate()
        # Stop playing podcast:
        self.pb.player.stop()

    def play (self):
        # If nothing is active, activate:
        if self.active_row.pkid is None:
            self.activate()
        else:
            # Start playing podcast:
            self.pb.player.play()

    def stop (self):
        self.deactivate()