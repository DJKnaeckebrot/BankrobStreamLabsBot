#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Bankob command, replica of the textbased version."""
#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import json
import os
import winsound
import ctypes
import time
#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Bankrob"
Website = "https://github.com/mrdennis1212"
Creator = "mrdennis1212"
Version = "1.0.1"
Description = "Bankrob command"
#---------------------------------------
# Versions
#---------------------------------------
""" Releases (open README.txt for full release notes)
1.0.0 - Initial Release
1.0.1 - Bug Fixes
"""
#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

#---------------------------------------
# Classes
#---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
                # load variables that do not need to be customisable from the ui
                self.ActiveGame = False
                self.ActiveGameAttendees = []
                self.ActiveGameEnd = None
                self.MaxChance = 20
                self.combinedChance = 0.0

        else: #set variables if no custom settings file is found
            self.OnlyLive = False
            self.Command = "!bankrob"
            self.JoinCommand = "!joinheist"
            self.Cost = 10
            self.Chance = 2.0
            self.MaxChance = 20
            self.combinedChance = 0.0
            self.Permission = "Everyone"
            self.PermissionInfo = ""
            self.Usage = "Stream Chat"
            self.UseCD = True
            self.Cooldown = 0
            self.OnCooldown = "{0} the command is still on cooldown for {1} seconds!"
            self.UserCooldown = 0
            self.OnUserCooldown = "{0} the command is still on user cooldown for {1} seconds!"
            self.CasterCD = True
            self.NotEnoughResponse = "{0} you don't have enough {1} to attempt this! You will need atleast {2} {1}."
            self.TargetNotEnoughResponse = "{0} the target {1} has not enough {2} to attempt this!"
            self.ActiveGame = False
            self.ActiveGameAttendees = []
            self.ActiveGameEnd = None
            self.ActiveGameTime = 60
            self.StartMessage = "{0} started a bankrob against {1}! Type {2} to join the heist!"
            self.ActiveGameResponse = "{0} the bankrob against {1} is currently active. Type {2} in the next {3} seconds to join the heist."
            self.NoActiveGameResponse = "{0} there is no bankrob currently active. Type {1} to begin da bankrob!"
            self.JoinedFightResponse = "{0} you joined the heist against {1}! Attendees: {2} - Win Chance {3} - Total Win Points {4} - Win Points per User {5}"
            self.AlreadyJoinedFight = "{0} you already joined the heist!"
            self.NoTeammatesFound = "{0} tried to rob {1} {2} from {3}. But nobody wanted to join him and he got caught!"
            self.WinResponse = "{0} and {1} others managed to rob {2} {3} from {4}'s bank! So everybody got {5} {3}"
            self.LoseResponse = "{0} and {1} others tried to bankrob all {2} {3} from {4} but they got rekt and paided {5} for trying to bankrob him!"
            self.PermissionResponse = "{0} -> only {1} ({2}) and higher can use this command"
            self.InfoResponse = "{0} you have to chose a target to try to bankrob from"
            self.NotHereResponse = "{0} you can only rob from users who are currently in the viewerlist!"
            self.SelfRobResponse = "{0} you can not rob yourself!"
            self.Protected = False
            self.Blacklist = ""
            self.BlacklistResponse = "{0} you can not rob {1}. User is blacklisted."
            self.Timeout = False
            self.TL = 60

    # Reload settings on save through UI
    def ReloadSettings(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        """Save settings to files (json and js)"""
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig', ensure_ascii=False)))
        return
#---------------------------------------
# [OPTIONAL] Settings functions
#---------------------------------------
def SetDefaults():
    """Set default settings function"""

    #play windows sound
    winsound.MessageBeep()

    #open messagebox with a security check
    MessageBox = ctypes.windll.user32.MessageBoxW
    returnValue = MessageBox(0, u"You are about to reset the settings, "
                                "are you sure you want to contine?"
                             , u"Reset settings file?", 4)

    #if user press "yes"
    if returnValue == 6:

        # Save defaults back to file
        Settings.SaveSettings(MySet, settingsFile)

        #show messagebox that it was complete
        MessageBox = ctypes.windll.user32.MessageBoxW
        returnValue = MessageBox(0, u"Settings successfully restored to default values"
                                 , u"Reset complete!", 0)

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    """data on Load, required function"""
    global MySet
    MySet = Settings(settingsFile)

def Execute(data):
    """Required Execute data function"""

    # read blacklist and format traget
    userblacklist = MySet.Blacklist.lower().replace(" ","").split(',')
    global targetname
    global stolenMoney

    if data.IsChatMessage() and data.GetParam(0).lower() == MySet.Command.lower():

        # check if trigger is from valid source
        if not IsFromValidSource(data, MySet.Usage):
            return

        # check if user has permission
        if not Parent.HasPermission(data.User, MySet.Permission, MySet.PermissionInfo):
            message = MySet.PermissionResponse.format(data.User, MySet.Permission, MySet.PermissionInfo)
            SendResp(data, message)

        if not HasPermission(data):
            return

        # check only live variable or is streamer is live
        if not MySet.OnlyLive or Parent.IsLive():

            # quit on cooldown
            if IsOnCooldown(data):
                return
                
            # check if bankrob is active 
            if MySet.ActiveGame:

                # notify that a game is active 
                message = MySet.ActiveGameResponse.format(data.UserName, targetname, MySet.JoinCommand, str(round(MySet.ActiveGameEnd - time.time())))
                SendResp(data, message)
                return

            else:
            
                targetname = data.GetParam(1).lower().replace('@', '')
            
                # check if target is in the blacklist
                if targetname in userblacklist:
                    message = MySet.BlacklistResponse.format(data.UserName, data.GetParam(1))
                    SendResp(data,message)
                    return
            
                # check if target is streamer and protected mode is on
                if targetname == Parent.GetChannelName().lower and MySet.Protected:
                    value = Parent.GetRandom(MySet.Min, MySet.Max)
                    Parent.RemovePoints(data.User, data.UserName, value)
                    message = MySet.LoseResponse.format(data.UserName, Parent.GetCurrencyName(), value, data.GetParam(1))
                    SendResp(data, message)
                    AddCooldown(data)
                    return

                # check if target has been selected
                if data.GetParamCount() < 2:
                    message = MySet.InfoResponse.format(data.UserName)
                    SendResp(data, message)
                    return

                # check if target is not intitator
                if targetname == data.User:
                    message = MySet.SelfRobResponse.format(data.UserName)
                    SendResp(data,message)
                    return
            
                # get current viewers
                viewerlist = Parent.GetViewerList() 
            
                for viewerlistIT in viewerlist:
                    viewerlistIT = viewerlistIT.lower()
                    
                # check if target is in viewerlist     
                if targetname not in viewerlist:
                    message = MySet.NotHereResponse.format(data.UserName)
                    SendResp(data,message)
                    return
                            
                # check if user has enough coins
                if not Parent.RemovePoints(data.User, data.UserName, MySet.Cost):
                    message = MySet.NotEnoughResponse.format(data.UserName, Parent.GetCurrencyName(), MySet.Cost)
                    SendResp(data, message)
                    return
                Parent.AddPoints(data.User, data.UserName, MySet.Cost)

                # setup random values
                userMoney = Parent.GetPoints(targetname)
                stolenMoney = Parent.GetRandom(userMoney/2, userMoney)

                # Subtract cost from user           
                Parent.RemovePoints(data.User, data.UserName, MySet.Cost)
                      
                # enable heist
                MySet.ActiveGame = True
                MySet.ActiveGameEnd = time.time() + MySet.ActiveGameTime
                MySet.ActiveGameAttendees.append(data.User)

                message = MySet.StartMessage.format(data.UserName, targetname, MySet.JoinCommand)
                SendResp(data, message)

    #check if command is join command      
    elif data.IsChatMessage() and data.GetParam(0).lower() == MySet.JoinCommand.lower():
    
        # If command is not from valid source -> quit
        if not IsFromValidSource(data, MySet.Usage):
            return

        # if client has no permission -> quit
        if not Parent.HasPermission(data.User, MySet.Permission, MySet.PermissionInfo):
            message = MySet.PermissionResponse.format(data.User, MySet.Permission, MySet.PermissionInfo)
            SendResp(data, message)

        if not HasPermission(data):
            return

        # check on onlylive setting or if user is live
        if not MySet.OnlyLive or Parent.IsLive():

             # quit on cooldown
            if IsOnCooldown(data):
                return
            
            # check if bankrob is active 
            if MySet.ActiveGame:
            
                # check if user has more points than highest possible lost
                if not Parent.RemovePoints(data.User, data.UserName, MySet.Cost):
                    message = MySet.NotEnoughResponse.format(data.UserName, Parent.GetCurrencyName(), MySet.Cost)
                    SendResp(data, message)
                    return
                Parent.AddPoints(data.User, data.UserName, MySet.Cost)
                
                # check if user already joined and send message if
                if data.User in MySet.ActiveGameAttendees:
                    message = MySet.AlreadyJoinedFight.format(data.UserName, targetname)
                    SendResp(data, message)
                    return
            
                # check if target is not intitator
                if targetname == data.User:
                    message = MySet.SelfRobResponse.format(data.UserName)
                    SendResp(data,message)
                    return
                
                # subtract usage costs
                Parent.RemovePoints(data.User, data.UserName, MySet.Cost)         
                
                # Setup chance
                if MySet.combinedChance <= 20:
                    MySet.combinedChance = MySet.Chance*len(MySet.ActiveGameAttendees)


                # add user to game and notify
                MySet.ActiveGameAttendees.append(data.User)
                
                message = MySet.JoinedFightResponse.format(data.UserName, targetname, len(MySet.ActiveGameAttendees), MySet.combinedChance/10, stolenMoney, stolenMoney/len(MySet.ActiveGameAttendees))
                SendResp(data, message)       
            
            else:
                # notify that no game is active 
                message = MySet.NoActiveGameResponse.format(data.UserName, MySet.Command)
                SendResp(data, message)
                return

def Tick():
    """Required tick function"""
    # check if game time if over
    if MySet.ActiveGame and time.time() >= MySet.ActiveGameEnd:

        if len(MySet.ActiveGameAttendees) == 1:
            message = MySet.NoTeammatesFound.format(MySet.ActiveGameAttendees[0], stolenMoney, Parent.GetCurrencyName(), targetname)
            Parent.SendStreamMessage(message)

            #reset game times
            MySet.ActiveGame = False
            MySet.ActiveGameEnd = None

            # clean up attendees array
            del MySet.ActiveGameAttendees[:]
            Parent.AddCooldown(ScriptName, MySet.Command, MySet.Cooldown)
            return
            
        else:
            #reset game times
            MySet.ActiveGame = False
            MySet.ActiveGameEnd = None
        
            UserWinValue = Parent.GetRandom(1,1001)

            # check if user wins against boss
            if UserWinValue < MySet.combinedChance:
                for ActiveGameAttendeesIT in MySet.ActiveGameAttendees:
                    # Add won points (total/amount attendees = share points) to account and add cooldown to users
                    Parent.AddPoints(ActiveGameAttendeesIT, ActiveGameAttendeesIT, stolenMoney/len(MySet.ActiveGameAttendees))
                    Parent.AddUserCooldown(ScriptName, MySet.Command, ActiveGameAttendeesIT, MySet.UserCooldown)
                    Parent.AddUserCooldown(ScriptName, MySet.JoinCommand, ActiveGameAttendeesIT, MySet.UserCooldown)
                    # todo: change username to @username
                Parent.RemovePoints(targetname, targetname, stolenMoney)
                message = MySet.WinResponse.format(MySet.ActiveGameAttendees[0], len(MySet.ActiveGameAttendees)-1, stolenMoney, Parent.GetCurrencyName(), targetname, stolenMoney/len(MySet.ActiveGameAttendees))
                Parent.SendStreamMessage(message)
                # clean up attendees array
                del MySet.ActiveGameAttendees[:]
                MySet.combinedChance = 0.0
                Parent.AddCooldown(ScriptName, MySet.Command, MySet.Cooldown)
                return
            elif UserWinValue >= MySet.combinedChance:
                # Remove lost points from account and add cooldown to users
                for ActiveGameAttendeesIT in MySet.ActiveGameAttendees:
                    Parent.RemovePoints(ActiveGameAttendeesIT, ActiveGameAttendeesIT, MySet.Cost)
                    Parent.AddUserCooldown(ScriptName, MySet.Command, ActiveGameAttendeesIT, MySet.UserCooldown)
                    Parent.AddUserCooldown(ScriptName, MySet.JoinCommand, ActiveGameAttendeesIT, MySet.UserCooldown)
                Parent.AddPoints(targetname, targetname, MySet.Cost*len(MySet.ActiveGameAttendees))
                message = MySet.LoseResponse.format(MySet.ActiveGameAttendees[0], len(MySet.ActiveGameAttendees)-1, stolenMoney, Parent.GetCurrencyName(), targetname, MySet.Cost*len(MySet.ActiveGameAttendees))
                Parent.SendStreamMessage(message)
                # clean up attendees array
                del MySet.ActiveGameAttendees[:]
                MySet.combinedChance = 0.0
                Parent.AddCooldown(ScriptName, MySet.Command, MySet.Cooldown)
                if MySet.Timeout:
                    Parent.SendStreamMessage("/timeout {0} {1}".format(data.User, MySet.TL))
                    return
            else:
                message = "Hunt hat nen Bug :("
                Parent.SendStreamMessage(message)

#---------------------------------------
# [Optional] Functions for usage handling
#---------------------------------------
def SendResp(data, sendMessage):
    """Sends message to Stream or discord chat depending on settings"""

    if not data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendStreamMessage(sendMessage)

    if not data.IsFromDiscord() and data.IsWhisper():
        Parent.SendStreamWhisper(data.User, sendMessage)

    if data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendDiscordMessage(sendMessage)

    if data.IsFromDiscord() and data.IsWhisper():
        Parent.SendDiscordDM(data.User, sendMessage)

def CheckUsage(data, rUsage):
    """Return true or false depending on the message is sent from
    a source that's in the usage setting or not"""

    if not data.IsFromDiscord():
        l = ["Stream Chat", "Chat Both", "All", "Stream Both"]
        if not data.IsWhisper() and (rUsage in l):
            return True

        l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
        if data.IsWhisper() and (rUsage in l):
            return True

    if data.IsFromDiscord():
        l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
        if not data.IsWhisper() and (rUsage in l):
            return True

        l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
        if data.IsWhisper() and (rUsage in l):
            return True

    return False

def IsOnCooldown(data):
    """Return true if command is on cooldown and send cooldown message if enabled"""
    cooldown = Parent.IsOnCooldown(ScriptName, MySet.Command)
    userCooldown = Parent.IsOnUserCooldown(ScriptName, MySet.Command, data.User)
    caster = (Parent.HasPermission(data.User, "Caster", "") and MySet.CasterCD)

    if (cooldown or userCooldown) and caster is False:

        if MySet.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, MySet.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, MySet.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = MySet.OnCooldown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, message)

            else:
                m_CooldownRemaining = userCDD

                message = MySet.OnUserCooldown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, message)
        return True
    return False

def HasPermission(data):
    """Returns true if user has permission and false if user doesn't"""
    if not Parent.HasPermission(data.User, MySet.Permission, MySet.PermissionInfo):
        message = MySet.PermissionResponse.format(data.UserName, MySet.Permission, MySet.PermissionInfo)
        SendResp(data, message)
        return False
    return True

def IsFromValidSource(data, Usage):
    """Return true or false depending on the message is sent from
    a source that's in the usage setting or not"""
    if not data.IsFromDiscord():
        l = ["Stream Chat", "Chat Both", "All", "Stream Both"]
        if not data.IsWhisper() and (Usage in l):
            return True

        l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
        if data.IsWhisper() and (Usage in l):
            return True

    if data.IsFromDiscord():
        l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
        if not data.IsWhisper() and (Usage in l):
            return True

        l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
        if data.IsWhisper() and (Usage in l):
            return True
    return False

def AddCooldown(data):
    """add cooldowns"""
    if Parent.HasPermission(data.User, "Caster", "") and MySet.CasterCD:
        Parent.AddCooldown(ScriptName, MySet.Command, MySet.Cooldown)
        return

    else:
        Parent.AddUserCooldown(ScriptName, MySet.Command, data.User, MySet.UserCooldown)
        Parent.AddCooldown(ScriptName, MySet.Command, MySet.Cooldown)
