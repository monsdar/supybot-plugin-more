###
# Copyright (c) 2013, Nils Brinkmann
# All rights reserved.
#
#
###

import os
import cPickle

import supybot.callbacks as callbacks
import supybot.conf as conf
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.plugins as plugins
import supybot.utils as utils
from supybot.commands import *

class InfoItem():
    def __init__(self, name):
        self.name = name
        self.items = {}
        
    def append(self, title, text):
        self.items[title] = text
        
    def clear(self):
        self.items.clear()
        
    def output(self, irc, channel):
        irc.queueMsg( ircmsgs.privmsg(channel, "Information for \x02" + self.name + "\x02:") )
        if( len(self.items) == 0):
            irc.queueMsg( ircmsgs.privmsg(channel, "No information") )
            
        for (title, text) in self.items.items():
            irc.queueMsg( ircmsgs.privmsg(channel, "\x02" + title + "\x02: " + text) )

class Info(callbacks.Plugin):
    """Displays generic information about a specific topic."""
    def __init__(self, irc):
        self.__parent = super(Info, self)
        self.__parent.__init__(irc)
        
        #a dict is easier to search
        self.items = {}
    
        #read the items from file
        filepath = conf.supybot.directories.data.dirize('Info.db')
        if( os.path.exists(filepath) ):
            try:
                self.items = cPickle.load( open( filepath, "rb" ) )
            except EOFError as error:
                irc.reply("Error when trying to load existing data.")
                irc.reply("Message: " + str(error))
        
    def die(self):
        #Pickle the items to a file
        try:
            filepath = conf.supybot.directories.data.dirize('Info.db')
            cPickle.dump( self.items, open( filepath, "wb" ) )
        except cPickle.PicklingError as error:
            print("Info: Error when pickling to file...")
            print(error)
        
    def list(self, irc, msg, args):
        """takes no arguments
        
        Displays all the names which could be outputted"""
        if self.items:
            for name in self.items.keys():
                irc.reply( name )
        else:
            irc.reply( "There are no names stored" )
            
    list = wrap(list)

    def info(self, irc, msg, args, name, channel):
        """<name> [<channel>]
        
        Displays content of the given <name>"""
        if not( name in self.items ):
            irc.error('There is no such name as ' + name)
            return
            
        self.items[name].output(irc, channel)
    info = wrap(info, ['somethingWithoutSpaces', 'channel'])
    
    def add(self, irc, msg, args, name, title, text):
        """<name> <title> <text>

        Adds an item with the given <title> and <text> to the topic <name>.
        The <name> and <title> must be without spaces. The <text> then is everything following.
        If there is no such topic, it will be created
        """
        if( name in  self.items):
            item = self.items[name]
        else:
            item = InfoItem(name)
            
        item.append(title, text)
        self.items[name] = item
        irc.replySuccess()       
    add = wrap(add, ['somethingWithoutSpaces', 'somethingWithoutSpaces', 'text'])
    
    def remove(self, irc, msg, args, name):
        """<name>
        
        Removes the given <name> from the plugin."""
        if not( name in self.items ):
            irc.error('There is no such name as ' + name)
            return
    
        del self.items[name]
        irc.replySuccess()
    remove = wrap(remove, ['somethingWithoutSpaces'])
        
    def clear(self, irc, msg, args, name):
        """<name>
        
        Clears all content from the given <name>."""
        if not( name in self.items ):
            irc.error('There is no such name as ' + name)
            return
            
        self.items[name].clear()
        irc.replySuccess()
    clear = wrap(clear, ['somethingWithoutSpaces'])
    
Class = Info


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
