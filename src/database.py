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

import feedparser
import json
import time

#------------------------------------------------------------------------------#
#     The following class is used as a convenient wrapper to translate Python's
#   9-Tupile time format into something 'JSON' can handle and back again.
#------------------------------------------------------------------------------#

class TimeTerp(object):
    """
    A simple wrapper to "pack" and "unpack" a Python 9-tuple time variable
    to/from a python dictionary format that 'JSON' can handle.
    """
    @staticmethod
    def pack_time(timeinfo):
        return {
            'tm_year' : timeinfo.tm_year,
            'tm_mon' : timeinfo.tm_mon,
            'tm_mday' : timeinfo.tm_mday,
            'tm_hour' : timeinfo.tm_hour,
            'tm_min' : timeinfo.tm_min,
            'tm_sec' : timeinfo.tm_sec,
            'tm_wday' : timeinfo.tm_wday,
            'tm_yday' : timeinfo.tm_yday,
            'tm_isdst' : timeinfo.tm_isdst
        }

    @staticmethod
    def unpack_time(timeinfo):
        return time.struct_time([
            timeinfo['tm_year'],
            timeinfo['tm_mon'],
            timeinfo['tm_mday'],
            timeinfo['tm_hour'],
            timeinfo['tm_min'],
            timeinfo['tm_sec'],
            timeinfo['tm_wday'],
            timeinfo['tm_yday'],
            timeinfo['tm_isdst']
            ])

#------------------------------------------------------------------------------#
#     The following two classes are the core data containers for 'Feed' (aka:
#   "podcast") and 'Episode' data.
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
#   The following three classes are designed to work around Python's single
#   constructor limitation by enforcing a uniform input standard for the 'Feed'
#   and 'Episode' classes.
#------------------------------------------------------------------------------#

class LDEpisodeSource(object):
    """
    Translates data loaded from the program's 'JSON' formatted database so it
    can be passed to the 'Episode' class in a uniform matter.
    """
    def __init__(self, source):
        # Loads episode data:
        self.link = source['url']
        self.title = source['title']
        self.description = source['description']
        self.published_parsed = source['dtg_published']
        self.media_content = []
        # Loads episode metadata:
        self.downloaded = source['downloaded']


class LDFeedSource(object):
    """
    Translates data loaded from the program's 'JSON' formatted database so it
    can be passed to the 'Feed' class in a uniform matter.
    """
    def __init__(self, source):
        # Loads feed data:
        self.url = source['url']
        self.title = source['title']
        self.description = source['description']
        self.entries = []
        # Loads feed metadata:
        self.valid = source['valid']
        self.subscribed = source['subscribed']


class FHFeedSource(object):
    """
    Fetches and parses data for a given feed from a remote loation using
    'feedparser' and maintains relevant data for the 'Feed' constructor.
    (Used to workaround Python's single constructor limitation.)
    """
    def __init__(self, feed_url):
        # Tries to parse the podcast feed, prints error if it fails:
        # try:
            self.url = feed_url
            source = feedparser.parse(feed_url)
            self.title = source.feed.title
            self.description = source.feed.description
            self.entries = source.entries
            for entry in self.entries:
                entry.downloaded = False
            self.valid = True
            self.subscribed = True
        # except:
        #     print ("Failed to parse feed: " + feed_url)
        #     self.url = feed_url
        #     self.valid = False
        #     self.subscribed = False

#------------------------------------------------------------------------------#
#     The following class handles all PodBlast's data, including feed
#   registrations and subscriptions, as well as saving and loading data to
#   persistant storage.
#------------------------------------------------------------------------------#

class Database(object):
    """
    An implementation to save and load data from a JSON formatted file, fetch
    feed data from remote urls, and manage feed registrations/subscriptions.
    """
    def __init__(self):
        print ("Initializing Database.")
        self.feeds = []

    # Loads data from a 'JSON' formatted database file and reconstructs that
    # data into 'Feed' and 'Episode' objects:
    def load(self):
        loaded = False
        try:
            # Open 'JSON' database and load data:
            with open('data/podblast_db', 'r') as json_file:
                data_cache = json.load(json_file)
            loaded = True
        except:
            print ("Failed to read database.")

        if loaded:
            # Reconstruct objects:
            for feed in data_cache:
                feed_source = LDFeedSource(feed)
                for episode in feed['episodes']:
                    episode['dtg_published'] = TimeTerp.unpack_time(
                        episode['dtg_published']
                        )
                    episode_source = LDEpisodeSource(episode)
                    for media in episode['media']:
                        episode_source.media_content.append({'url' : media})
                    feed_source.entries.append(episode_source)
                self.feeds.append(Feed(feed_source))

    # Compiles feed, episode and media data into a monolythic 'JSON' compatible
    # dictionary so it can be saved to disk;
    def save(self):
        if self.feeds:
            # Compile a cache of data:
            data_cache = []
            for feed in self.feeds:
                if feed.valid:
                    feed_cache = {
                        'url' : feed.url,
                        'title' : feed.title,
                        'description' : feed.description,
                        'episodes': [],
                        'valid' : feed.valid,
                        'subscribed' : feed.subscribed
                        }
                    for episode in feed.episodes:
                        episode_cache = {
                            'url' : episode.url,
                            'title' : episode.title,
                            'description' : episode.description,
                            'media' : [],
                            'dtg_published' : TimeTerp.pack_time(
                                episode.dtg_published
                                ),
                            'downloaded' : episode.downloaded
                        }
                        for media in episode.media:
                            episode_cache['media'].append(media)
                        feed_cache['episodes'].append(episode_cache)
                    data_cache.append(feed_cache)

            try:
                # Open 'JSON' database and save the cache to disk:
                with open('data/podblast_db', 'w') as json_file:
                    json.dump(data_cache, json_file)
            except:
                print ("Failed to write database.")

        else:
            print ("No feeds to save.")

    # Marks a registered feed as 'subscribed':
    def subscribe_feed(self, feed_url):
        search_results = [search for search in self.feeds if search.url == feed_url]
        if search_results:
            for feed in search_results:
                feed.subscribed = True
        else:
            print ("Could not find a valid feed to set subscription: " + feed_url)

    # Unmarks a registered feed as 'subscribed':
    def unsubscribe_feed(self, feed_url):
        search_results = [search for search in self.feeds if search.url == feed_url]
        if search_results:
            for feed in search_results:
                feed.subscribed = False
        else:
            print ("Could not find a valid feed to unset subcription: " + feed_url)

    # Registers a new feed with PodBlast if it has not already been registered:
    def register_feed(self, feed_url):
        search_results = [search for search in self.feeds if search.url == feed_url]
        if search_results:
            print ("Feed already registered: " + feed_url)
        else:
            try:
                source = FHFeedSource(feed_url)
                self.feeds.append(
                    Feed(source)
                    )
            except:
                print ("Failed to register feed: " + feed_url)

    # Deletes a feed from PodBlast's database:
    def delete_feed(self, feed_url):
        for feed in [search for search in self.feeds if search.url == feed_url]:
            self.feeds.remove(feed)