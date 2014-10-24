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

import csv
import feedparser

#------------------------------------------------------------------------------#

class Episode(object):
    """
    A data structure containing the important data about a single episode of a
    podcast (aka: "feed"). It includes a list of urls pointing to each piece
    of media embeded in the podcast.
    """
    def __init__(self, episode_source):
        # Defines episode data:
        self.url = episode_source.link
        self.title = episode_source.title
        self.description = episode_source.description
        self.dtg_published = episode_source.published_parsed
        # Compiles a list of embeded media urls:
        self.media = []
        for media_source in episode_source.media_content:
            self.media.append(media_source['url'])
        # Defines episode metadata:
        self.downloaded = episode_source.downloaded


class Feed(object):
    """
    A data structure containing the important data about a single podcast
    (aka: "feed"). It includes a list of 'Episode' objects.
    """
    def __init__(self, feed_source):
        # Extracts feed data:
        self.url = feed_source.url
        self.title = feed_source.title
        self.description = feed_source.description
        # Compiles a list of episodes:
        self.episodes = []
        for episode_source in feed_source.entries:
            self.episodes.append(Episode(episode_source))
        # Extracts feed metadata:
        self.valid = feed_source.valid
        self.subscribed = feed_source.subscribed

#------------------------------------------------------------------------------#

class LDEpisodeSource(object):
    """
    Accepts data from a row of CSV data and maintains that data for the
    'Episode' constructor. (Used to workaround Python's single constructor
    limitation.)
    """
    def __init__(self, csv_row):
        # Loads episode data:
        self.link = csv_row[1]
        self.title = csv_row[2]
        self.description = csv_row[3]
        self.published_parsed = csv_row[4]
        self.media_content = []
        # Loads episode metadata:
        self.downloaded = csv_row[5]


class LDFeedSource(object):
    """
    Accepts data from a row of CSV data and maintains that data for the 'Feed'
    constructor. (Used to workaround Python's single constructor limitation.)
    """
    def __init__(self, csv_row):
        # Loads feed data:
        self.url = csv_row[0]
        self.title = csv_row[1]
        self.description = csv_row[2]
        self.entries = []
        # Loads feed metadata:
        self.valid = csv_row[3]
        self.subscribed = csv_row[4]


class FHFeedSource(object):
    """
    Fetches and parses data for a given feed from a remote loation using
    'feedparser' and maintains relevant data for the 'Feed' constructor.
    (Used to workaround Python's single constructor limitation.)
    """
    def __init__(self, feed_url):
        # Tries to parse the podcast feed, prints error if it fails:
        try:
            self.url = feed_url
            source = feedparser.parse(feed_url)
            self.title = source.feed.title
            self.description = source.feed.description
            self.entries = source.entries
            for entry in self.entries:
                entry.downloaded = False
            self.valid = True
            self.subscribed = True
        except:
            print ("Failed to parse feed: " + feed_url)
            self.url = feed_url
            self.valid = False
            self.subscribed = False

#------------------------------------------------------------------------------#

class Database(object):
    """
    An implementation to save and load data from CSV files, fetch feed data
    from remote urls, and manage feed subscriptions.
    """
    def __init__(self):
        self.feeds = []

    # Loads all of the media content urls of a given episode:
    def load_media(self, episode_url):
        with open('media.csv', 'rb') as csvfile:
            media_reader = csv.reader(csvfile)
            media_content = []
            (media_content.append({ 'url': url }) for url in
                [media[1] for row in media_reader if row[0] is episode_url])
            return media_content

    # Loads all of the episodes of a given feed:
    def load_episodes(self, feed_url):
        with open('episodes.csv', 'rb') as csvfile:
            episode_reader = csv.reader(csvfile)
            entries = []
            for row in episode_reader:
                print ("Loading: " + row[0] + " == " + feed_url)
                if row[0] == feed_url:
                    source = LDEpisodeSource(row)
                    episode_url = row[1]
                    source.media_content = self.load_media(episode_url)
                    entries.append(
                        Episode(source)
                        )
            return entries

    # Loads all of the feeds which have been saved by the user:
    def load_feeds(self):
        with open('feeds.csv', 'rb') as csvfile:
            feed_reader = csv.reader(csvfile)
            feeds = []
            for row in feed_reader:
                feed_url = row[0]
                source = LDFeedSource(row)
                source.entries = self.load_episodes(feed_url)
                feeds.append(
                    Feed(source)
                    )
            return feeds

    # Saves an episode's media urls to a CVS file:
    def save_media(self, episode):
        with open('media.csv', 'wb') as csvfile:
            filewriter = csv.writer(csvfile)
            for media_url in episode.media:
                filewriter.writerow([
                    episode.url,
                    media_url
                    ])

    # Saves all of a feed's valid episodes to a CVS file:
    def save_episodes(self, feed):
        with open('episodes.csv', 'wb') as csvfile:
            filewriter = csv.writer(csvfile)
            for episode in feed.episodes:
                filewriter.writerow([
                    feed.url,
                    episode.url,
                    episode.title,
                    episode.description,
                    episode.dtg_published,
                    episode.downloaded
                    ])
                self.save_media(episode)

    # Saves all registered and valid feeds to a CVS file:
    def save_feeds(self):
        if self.feeds:
            with open('feeds.csv', 'wb') as csvfile:
                filewriter = csv.writer(csvfile)
                for feed in self.feeds:
                    if feed.valid:
                        filewriter.writerow([
                            feed.url,
                            feed.title,
                            feed.description,
                            feed.valid,
                            feed.subscribed
                            ])
                        self.save_episodes(feed)
        else:
            print ("No feeds to save.")

    # If a feed with the given url is found, sets 'subscribed' to 'True',
    #   otherwise prints error to console.
    def subscribe_feed(self, feed_url):
        feed_search = [feed for feed in self.feeds if feed.url is feed_url]
        if feed_search:
            for feed in feed_search:
                feed.subscribed = True
        else:
            print ("Could not find a valid feed to set subscription: " + feed_url)

    # If a feed with the given url is found, sets 'subscribed' to 'False':
    def unsubscribe_feed(self, feed_url):
        feed_search = [feed for feed in self.feeds if feed.url is feed_url]
        if feed_search:
            for feed in feed_search:
                feed.subscribed = False
        else:
            print ("Could not find a valid feed to unset subcription: " + feed_url)

    # Fetches feed data if the given feed_url is not already registered.
    def register_feed(self, feed_url):
        feed_search = [feed for feed in self.feeds if feed.url is feed_url]
        if feed_search:
            print ("Feed already registered: " + feed_url)
        else:
            # try:
                source = FHFeedSource(feed_url)
                self.feeds.append(
                    Feed(source)
                    )
            # except:
                # print ("Failed to register feed: " + feed_url)

    # Deletes any feed objects with a url matching the given 'feed_url':
    def delete_feed(self, feed_url):
        feed_search = [feed for feed in self.feeds if feed.url is feed_url]
        for feed in (feeds for feed in feed_search if feed_search):
            feed_index = self.feeds.index(feed)
            self.feeds.remove(feed_index)