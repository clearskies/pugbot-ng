#!/usr/bin/env python

import irc.bot
import json
import random

class Pugbot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        super(Pugbot, self).__init__([(config["server"], config["port"])], config["nick"], config["nick"])
        self.channel = config["channel"]
        self.target = self.channel
        self.cmdPrefixes = config["prefixes"]
        self.owner = config["owner"]
        self.password = ""


    def say(self, msg):
        self.connection.privmsg(self.channel, msg)

    def pm(self, nick, msg):
        self.connection.privmsg(nick, msg)
    
    def reply(self, msg):
        self.connection.privmsg(self.target, msg)

    def on_welcome(self, conn, e):
        conn.join(self.channel)

        alpha = "abcdefghijklmopqrstuvwxyz"
        password = ""
        for _ in range(5):
            password += random.choice(alpha)
        self.password = password

        print("The password is: " + password)
        if self.owner != "":
            self.pm(self.owner, "The password is: " + password)

    def on_privmsg(self, conn, e):
        self.executeCommand(conn, e, True)

    def on_pubmsg(self, conn, e):
        if (e.arguments[0][0] in self.cmdPrefixes):
            self.executeCommand(conn, e)

    def executeCommand(self, conn, e, private = False):
        issuedBy = e.source.nick
        text = e.arguments[0][1:].split(" ")
        command = text[0].lower()
        data = " ".join(text[1:])

        if private:
            self.target = issuedBy
        else:
            self.target = self.channel

        try:
            commandFunc = getattr(self, "cmd_" + command)
            commandFunc(issuedBy, data)
        except AttributeError:
            self.reply("Command not found: " + command)

    def cmd_help(self, issuedBy, data):
        """.help [command] - displays this message"""
        if data == "":
            attrs = sorted(dir(self))
            self.reply("Commands:")
            for attr in attrs:
                if attr[:4] == "cmd_":
                    self.reply(getattr(self, attr).__doc__)
        else:
            try:
                command = getattr(self, data)
                self.reply(command.__doc__)
            except AttributeError:
                self.reply("Command not found: " + data)
    
    def cmd_plzdie(self, issuedBy, data):
        """.plzdie - kills the bot"""
        if (data == self.password):
            self.die("{} doesn't like me :<".format(issuedBy))
        else:
            self.reply("You can't run that command without a password")

    def cmd_hello(self, issuedBy, data):
        """.hello - greets you"""
        self.reply("Hello, {}!".format(issuedBy))

if __name__ == "__main__":
    try:
        configFile = open("config.json", "r")
        config = json.loads(configFile.read())
    except IOError:
        config = {
            "server": "irc.quakenet.org",
            "port": 6667,
            "prefixes": "!@>.",
            "channel": "#nuubs",
            "nick": "pugbot-ng",
            "owner": ""
        }

    bot = Pugbot(config)
    bot.start()
