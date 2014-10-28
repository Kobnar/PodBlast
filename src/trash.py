class TreeViewManager:
    """
    A base class to manipulate 'TreeView' objects of PodBlast's GTK/Glade
    front-end.
    """
    def __init__(self, treeview):
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


class FeedManager (TreeViewManager):

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
        self.update_feed_actvtn(self.active_row.pkid)


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

    def subscribe (self):
        # Get and validate data from user interface:
        feed_url = self.validate_feed_url(
            self.ap_url_entry.get_text()
            )
        feed = self.pb.data.subscribe(feed_url)
        if feed is False:
            self.throw_err_diag('Feed not recognized.')
        elif feed is None:
            self.throw_err_diag('An active subscription with that URL already exists.')
            return False
        else:
            self.refresh_subscr_list()
            return True

    def unsubscribe (self):
        # Get the PKID of the current selection:
        select_iter = self.treeview.get_selection().get_selected()[1]
        subscr_pkid = self.subscr_treeview.get_model().get_value(select_iter, 0)
        # Deactivate any active rows:
        self.deactivate()
        # Pass data management to 'state.data':
        self.pb.data.unsubscribe(subscr_pkid)
        # Update the user interface:
        self.refresh_subscr_list()


class EpisodeManager (TreeViewManager):

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
        self.update_episode_actvtn(self.active_row.pkid)
        # Set the new stream url:
        self.pb.player.set(self.pb.data.db['episodes'][self.active_row.pkid]['audio_url'])
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

#------------------------------------------------------------------------------#

class GTKInterface(object):
    """
    An implementation to link the GTK/Glade user interface with the PodBlast
    backend as a collection of python objects. It also provides a collection of
    methods to handle signals from the frontend.
    """
    def __init__(self):
        print ('Initializing GTK/Glade interface...')

        print ('...Connecting to GTK/Glade interface file.')
        # Defines the GTK/Glade interface source file and 'Gtk.Builder' object.
        self.ux_source = 'ux/podblast.glade'
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(self.ux_source)

        print ('...Linking to GTK front-end objects.')
        # Links to main window and dialog window objects:
        self.main_window = self.gtk_builder.get_object('MainWindow')
        self.add_feed_diag = self.gtk_builder.get_object('AddFeedDiag')
        self.err_diag = self.gtk_builder.get_object('ErrDiag')
        self.confirm_diag = self.gtk_builder.get_object('ConfirmDiag')

        # Links to objects in the 'Feeds' tab:
        # self.feed_list = self.gtk_builder.get_object('FeedList')
        self.subscr_treeview = self.gtk_builder.get_object('SubscrTreeview')
        self.subscr_list = self.gtk_builder.get_object('SubscriptionList')

        # Links to objects in the 'Feeds' popup menu:
        self.feed_menu = self.gtk_builder.get_object('FeedMenu')
        self.feed_menu_split = self.gtk_builder.get_object('FeedMenuSplit')
        self.feed_menu_edit = self.gtk_builder.get_object('FeedMenuEdit')
        self.feed_menu_del = self.gtk_builder.get_object('FeedMenuDel')

        # Links to objects in the 'Episodes' tab:
        self.active_feed_label = self.gtk_builder.get_object('ActiveFeedLabel')
        self.episode_treeview = self.gtk_builder.get_object('EpisodesTreeview')
        self.episode_list = self.gtk_builder.get_object('EpisodesList')

        # Links to objects in the 'Player' status bar: 
        self.play_img = self.gtk_builder.get_object('PlayImg')
        self.play_button = self.gtk_builder.get_object('PlayButton')
        self.stop_button = self.gtk_builder.get_object('StopButton')
        self.ffwd_button = self.gtk_builder.get_object('FfwdButton')
        self.rwnd_button = self.gtk_builder.get_object('RwndButton')
        self.ffwd_button = self.gtk_builder.get_object('NextButton')
        self.prev_button = self.gtk_builder.get_object('PrevButton')

        # Links to objects in the 'Add Podcast', error and confirmation
        # dialogue windows:
        self.ap_url_entry = self.gtk_builder.get_object('AddPodcastURLEntry')
        self.err_diag_label = self.gtk_builder.get_object('ErrDiagLabel')
        self.confirm_diag_label = self.gtk_builder.get_object('ConfirmDiagLabel')
        self.confirm_diag_confirm_button = self.gtk_builder.get_object('ConfirmDiagConfirm')
        self.confirm_diag_cancel_button = self.gtk_builder.get_object('ConfirmDiagCancel')

        print ('...Creating to GTK TreeView managers.')
        # Instantiates 'TreeViewManager' objects:
        self.feed_manager = FeedManager(self.subscr_treeview)
        self.episode_manager = EpisodeManager(self.episode_treeview)

    def main (self):
        Gtk.main()

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # Core Generation and Termination:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def end_program (self, *args):
        Gtk.main_quit(*args)

    def throw_err_diag(self, err_diag_text):
        self.err_diag_label.set_text(err_diag_text)
        self.err_diag.show()

    def close_add_feed_diag(self):
        self.add_feed_diag.hide()
        self.ap_url_entry.set_text('')

    #--------- -- -- - - -- -  -   -  -      -  -      -
    # User Interface Updates, Refreshes and Stuffs:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def refresh_subscr_list (self):
        # Clears existing subscription list and builds a new one from scratch.
        self.subscr_list.clear()
        i = 0
        for subscr in self.pb.data.db['subscriptions']:
            feed_pkid = subscr['feed_pkid']
            if subscr['active'] is True:
                feed_url = self.pb.data.db['feeds'][feed_pkid]['url']
                feed_title = self.pb.data.db['feeds'][feed_pkid]['title']
                feed_desc = self.pb.data.db['feeds'][feed_pkid]['desc']
                self.subscr_list.append([i, feed_pkid, feed_title, feed_url, feed_desc, 0])
            i += 1

    def refresh_window_title (self):
        if self.pb.state.active_feed_title == None:
            self.main_window.set_title('PodBlast')
        elif self.pb.state.active_episode_title == None:
            self.main_window.set_title('PodBlast [' + self.pb.state.active_feed_title + ']')
        else:
            self.main_window.set_title('PodBlast [' + self.pb.state.active_episode_feed_title + ' - ' + self.active_episode_title + ']')
        # DEBUG INFO:
        # print ('[' + str(self.active_feed_pkid) + ', ' + str(self.active_episode_pkid )+ ']')

    def refresh_player_buttons_null (self):
            self.play_img.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)

    def refresh_player_buttons_ready (self):
            self.play_img.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)

    def refresh_player_buttons_paused (self):
            self.play_img.set_from_stock(Gtk.STOCK_MEDIA_PLAY, 4)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(True)

    def refresh_player_buttons_playing (self):
            self.play_img.set_from_stock(Gtk.STOCK_MEDIA_PAUSE, 4)
            self.play_button.set_sensitive(True)
            self.stop_button.set_sensitive(True)


    #--------- -- -- - - -- -  -   -  -      -  -      -
    # User Interface Refreshments:
    #--------- -- -- - - -- -  -   -  -      -  -      -

    def update_feed_actvtn (self, feed_pkid):

        # Update states:
        self.active_feed_pkid = self.pb.data.db['subscriptions'][feed_pkid]['feed_pkid']
        self.active_feed_title = self.pb.data.db['feeds'][feed_pkid]['title']
        self.active_feed_url = self.pb.data.db['feeds'][feed_pkid]['url']
        # self.active_episode_pkid = None
        # self.active_episode_title = None
        # Clear and repopulate 'ux.episode_list':
        self.episode_list.clear()
        i = 0
        for episode in self.pb.data.db['episodes']:
            if episode['feed_pkid'] == self.active_feed_pkid:
                self.episode_list.append([i, episode['title'], episode['desc'], 0])
            i += 1
        # Update Active Feed label:
        self.active_feed_label.set_text(self.active_feed_title + '  [' + self.active_feed_url + ']')
        # Refresh the title bar:
        self.refresh_window_title()

    def update_episode_actvtn (self, episode_pkid):
        # Update active feed status:
        self.active_episode_pkid = episode_pkid
        self.pb.state.active_episode_title = self.pb.data.db['episodes'][episode_pkid]['title']
        # Refresh the title bar:
        self.refresh_window_title()