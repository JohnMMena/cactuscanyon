##
## This mode controls the saloon
## for now it's just popping the ball back out of the mine if it gets in there
##

from procgame import *
import cc_modes
import ep
import random
import locale

class Saloon(game.Mode):
    """Game mode for controlling the skill shot"""
    def __init__(self, game,priority):
        super(Saloon, self).__init__(game, priority)
        # set up the number of barts required
        self.bartsForStar = self.game.user_settings['Gameplay (Feature)']['Bart Brothers for Star']
        # setup the difficulty
        difficulty = self.game.user_settings['Gameplay (Feature)']['Bart Brothers Difficulty']
        # Easy version
        print "Difficulty is set to - " + difficulty
        if difficulty == 'Easy':
            self.hitsToDefeatBart = [2,4,5,6,7,8]
        # Hard version
        else:
            self.hitsToDefeatBart = [3,5,6,7,8,8]
        # hits banners list
        self.banners = ['bam','biff','ouch','pow','wham','zoink']

    def mode_started(self):
        # activate the first bart
        self.game.set_tracking('bartStatus',"RUNNING")
        self.setup_bart()

    def sw_saloonPopper_closed_for_200ms(self,sw):
        if self.game.show_tracking('isBountyLit'):
            self.collect_bounty()
        print "PULSE THE KICKER FOR THE SALOON"

    def sw_saloonBart_active(self,sw):
        # a direct smack to el barto
        self.hit_bart()

    def sw_saloonGate_active(self,sw):
        # play the sound.
        # add some points
        self.game.score(2530)
        # exciting!

    def sw_jetBumpersExit_active(self,sw):
        # if there's an active bart, play a quote
        if self.game.show_tracking('bartStatus') == "RUNNING":
            self.game.sound.play_voice(self.tauntQuote)
        # score some points
        self.game.score(2530)

    ###
    ###  ____                    _
    ### | __ )  ___  _   _ _ __ | |_ _   _
    ### |  _ \ / _ \| | | | '_ \| __| | | |
    ### | |_) | (_) | |_| | | | | |_| |_| |
    ### |____/ \___/ \__,_|_| |_|\__|\__, |
    ###                              |___/
    ###

    def light_bounty(self):
        # set the tracking
        self.game.set_tracking('isBountyLit', True)
        # show something on the screen
        backdrop = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'stars-border.dmd').frames[0])
        topText = dmd.TextLayer(128/2, 4, self.game.assets.font_9px_az, "center", opaque=False).set_text("COLLECT BOUNTY",blink_frames=10)
        bottomText = dmd.TextLayer(128/2, 16, self.game.assets.font_9px_az, "center", opaque=False).set_text("IS LIT",blink_frames=10)
        self.layer = dmd.GroupedLayer(128,32,[backdrop,topText,bottomText])
        # play a voice clip about the bounty being ready
        self.game.sound.play_voice(self.game.assets.quote_bountyLit)
        # lights and whatnot
        self.delay(delay=1.6,handler=self.clear_layer)

    def collect_bounty(self):
        # TODO award the prize
        # turn off the tracking
        self.game.set_tracking('isBountyLit', False)
        # select an award
        # give the award

    ###
    ###  ____             _     ____            _   _
    ### | __ )  __ _ _ __| |_  | __ ) _ __ ___ | |_| |__   ___ _ __ ___
    ### |  _ \ / _` | '__| __| |  _ \| '__/ _ \| __| '_ \ / _ \ '__/ __|
    ### | |_) | (_| | |  | |_  | |_) | | | (_) | |_| | | |  __/ |  \__\
    ### |____/ \__,_|_|   \__| |____/|_|  \___/ \__|_| |_|\___|_|  |___/
    ###

    def hit_bart(self):
        # pick a random banner to use
        banner = random.choice(self.banners)
        # set up the banner layer
        self.bannerLayer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+banner+'-banner.dmd').frames[0])

        # lookup the status
        status = self.game.show_tracking('bartStatus')
        print "BART STATUS: " + status
        print "CURRENT BART: " + str(self.game.show_tracking('currentBart'))
        # if no bart is currently running, a new challenger appears
        if status == "OPEN":
            self.game.set_tracking('bartStatus',"RUNNING")
            self.activate_bart()
        # else, register the hit
        elif status == "RUNNING":
            self.damage_bart()
        # if there is one active and it's the last hit, defeat
        elif status == "LAST":
            self.defeat_bart()
        # not running? do this
        else:
            # he's dead waiting for a gun fight - TODO have to research what happens
            # no points - play a sound?
            pass

    def activate_bart(self):
        # set up all the strings & quotes
        self.setup_bart()
        # show the 'challenges you' display
        # clear the banner layer
        textLayer1 = dmd.TextLayer(42,2,self.game.assets.font_7px_bold_az,justify="center",opaque=False)
        textLayer1.set_text(self.nameLine)
        textLayer2 = dmd.TextLayer(42,16,self.game.assets.font_7px_bold_az,justify="center",opaque=False)
        textLayer2.set_text("CHALLENGES")
        textLayer3 = dmd.TextLayer(42,24,self.game.assets.font_7px_bold_az,justify="center",opaque=False)
        textLayer3.set_text("YOU")

        textLayer = dmd.GroupedLayer(128,32,[self.wantedFrameB,textLayer1,textLayer2,textLayer3])
        transition = ep.EP_Transition(self,self.game.score_display.layer,textLayer,ep.EP_Transition.TYPE_PUSH,ep.EP_Transition.PARAM_NORTH)
        self.delay(delay=1.5,handler=self.clear_layer)

        # if there's only 1 hit to defeat this bart, set the status to last
        if self.hitsThisBart == 1:
            self.game.set_tracking('bartStatus',"LAST")

    def setup_bart(self):
        # our cast of characters
        names = ('big','bandelero','bubba')
        hits = (self.game.assets.quote_hitBigBart, self.game.assets.quote_hitBandeleroBart,self.game.assets.quote_hitBubbaBart)
        taunts = (self.game.assets.quote_tauntBigBart, self.game.assets.quote_tauntBandeleroBart,self.game.assets.quote_tauntBubbaBart)
        defeats = (self.game.assets.quote_defeatBigBart, self.game.assets.quote_defeatBandeleroBart,self.game.assets.quote_defeatBubbaBart)
        # look up which one is current
        index = self.game.show_tracking('currentBart')
        # setting up all the bits like name for text display
        self.brother = names[index].upper()
        # wanted poster
        self.wantedFrameA = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'wanted-'+ self.brother +'-A.dmd').frames[0])
        self.wantedFrameA.composite_op = "blacksrc"
        self.wantedFrameB = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'wanted-'+ self.brother +'-B.dmd').frames[0])
        # hit quotes
        self.hitQuote = hits[index]
        # taunt quotes
        self.tauntQuote = taunts[index]
        # death quote
        self.defeatQuote = defeats[index]
        defeated = self.game.show_tracking('bartsDefeated')
        # setup the points value? 120,000 + 5,000 times the number of defeated barts
        self.hitValue = 120000 + (5000 * defeated)
        self.hitString = locale.format("%d", self.hitValue, True) # Add commas
        # setup the defeat value 150,000 for first + 50,000 times the number of defeated barts
        self.defeatValue = 150000 + (50000 * defeated)
        self.defeatString = locale.format("%d", self.defeatValue, True) # Add commas
        # setup the hits needed to defeat this bart
        self.hitsThisBart = self.hitsToDefeatBart[index]
        # set up the name line for the cards
        print self.brother + " IS THE BROTHER"
        if self.brother != "BANDELERO":
            self.nameLine = self.brother.upper() + " BART"
        else:
            self.nameLine = self.brother


    def damage_bart(self):
        print "DAMAGE BART"
        # play a quote appropriate to the current bart
        self.game.sound.play_voice(self.hitQuote)
        # score the points
        self.game.score(self.hitValue)
        # flash the light and move the dude
        # display the info
        # register the hit
        # increase the hits on bart - and store the new amount
        currentHits = self.game.increase_tracking('bartHits')
        # check to see if we're on the last hit now - meaning, our hit total is one less than defeat
        # math the remaining hits
        print "HITS FOR THIS BART: " + str(self.hitsThisBart)
        print "CURRENT HITS: " + str(currentHits)
        hitsLeft = self.hitsThisBart - currentHits
        if hitsLeft <= 1:
            # if it is, set the status to last
            self.game.set_tracking('bartStatus',"LAST")
        theText = str(hitsLeft) + " MORE HITS"
        textLayer1 = dmd.TextLayer(42,1,self.game.assets.font_7px_bold_az,justify="center",opaque=False).set_text(self.nameLine)
        textLayer2 = dmd.TextLayer(42,9,self.game.assets.font_7px_bold_az,justify="center",opaque=False).set_text(str(self.hitString))
        textLayer3 = dmd.TextLayer(42,17,self.game.assets.font_6px_az,justify="center",opaque=False).set_text(theText)
        textLayer4 = dmd.TextLayer(42,24,self.game.assets.font_6px_az,justify="center",opaque=False).set_text("TO COLLECT")
        self.textLayer = dmd.GroupedLayer(128,32,[textLayer1,textLayer2,textLayer3,textLayer4])
        self.textLayer.composite_op = "blacksrc"
        self.display_damage_one()

    def defeat_bart(self):
        print "DEFEATING BART"
        # add to the defeated barts
        currentTotal = self.game.increase_tracking('bartsDefeated')
        # play a defeated quote
        self.game.sound.play_voice(self.defeatQuote)
        # set the status to dead - gunfight has to set it back to open
        self.game.set_tracking('bartStatus',"DEAD")
        # if we're at the end of the line, reset to 0
        if self.game.show_tracking('currentBart') == 2:
            self.game.set_tracking('currentBart',0)
        # if not tick up the current bart for next time
        else:
            self.game.increase_tracking('currentBart')
        # score some points
        self.game.score(self.defeatValue)
        # reset the hits on bart
        self.game.set_tracking('bartHits',0)
        backdrop = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'weave-border.dmd').frames[0])
        textLayer1 = dmd.TextLayer(64,2,self.game.assets.font_9px_az,justify="center",opaque=False).set_text("BART DEFEATED")
        textLayer2 = dmd.TextLayer(64,12,self.game.assets.font_9px_az,justify="center",opaque=False).set_text(str(self.defeatString))
        if currentTotal < self.bartsForStar:
            thetext = str(self.bartsForStar - currentTotal) + " MORE FOR BADGE"
        elif currentTotal == self.bartsForStar:
            thetext = "BADGE COLLECTED!"
            # TODO actually collect the badge :P
        else:
            thetext = str(currentTotal) + " DEFEATED!"
        textLayer3 = dmd.TextLayer(64,24,self.game.assets.font_6px_az,justify="center",opaque=False).set_text(thetext)
        self.layer = dmd.GroupedLayer(128,32,[backdrop,textLayer1,textLayer2,textLayer3])

        # light gunfight?
        self.delay(delay=2,handler=self.light_gunfight)

    def display_damage_one(self):
        # set up the top layer
        layerOne = dmd.GroupedLayer(128,32,[self.bannerLayer,self.wantedFrameA])
        # activate it
        self.layer = layerOne
        self.delay(delay=0.2,handler=self.display_damage_two,param=layerOne)

    def display_damage_two(self,layerOne):
        # set up the second layer
        layerTwo = dmd.GroupedLayer(128,32,[self.wantedFrameB,self.textLayer])
        transition = ep.EP_Transition(self,layerOne,layerTwo,ep.EP_Transition.TYPE_PUSH,ep.EP_Transition.PARAM_NORTH)
        self.delay(delay = 1.5,handler=self.clear_layer)

    def clear_layer(self):
        self.layer = None


    ## Gunfight

    def light_gunfight(self):
        print "GUNFIGHT IS LIT"
        # turn on the lights
        # show the display
        backdrop = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'single-cowboy-border.dmd').frames[0])
        textLayer1 = dmd.TextLayer(77,2,self.game.assets.font_12px_az,justify="center",opaque=False)
        textLayer1.set_text("GUNFIGHT")
        textLayer2 = dmd.TextLayer(77,15,self.game.assets.font_12px_az,justify="center",opaque=False)
        textLayer2.set_text("IS LIT")
        textLayer2.composite_op = "blacksrc"
        self.layer = dmd.GroupedLayer(128,32,[backdrop,textLayer1,textLayer2])
        # play a quote
        self.game.sound.play_voice(self.game.assets.quote_gunfightLit)
        # set the tracking
        self.game.set_tracking('gunfightStatus',"READY")
        self.delay(delay=2,handler=self.clear_layer)