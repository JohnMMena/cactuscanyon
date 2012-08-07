##   ____           _                ____
##  / ___|__ _  ___| |_ _   _ ___   / ___|__ _ _ __  _   _  ___  _ __
## | |   / _` |/ __| __| | | / __| | |   / _` | '_ \| | | |/ _ \| '_ \
## | |__| (_| | (__| |_| |_| \__ \ | |__| (_| | | | | |_| | (_) | | | |
##  \____\__,_|\___|\__|\__,_|___/  \____\__,_|_| |_|\__, |\___/|_| |_|
##                                                   |___/
##           ___ ___  _  _ _____ ___ _  _ _   _ ___ ___
##          / __/ _ \| \| |_   _|_ _| \| | | | | __|   \
##         | (_| (_) | .` | | |  | || .` | |_| | _|| |) |
##          \___\___/|_|\_| |_| |___|_|\_|\___/|___|___/
##
## A P-ROC Project by Eric Priepke
## Built on the PyProcGame Framework from Adam Preble and Gerry Stellenberg
## Original Cactus Canyon software by Matt Coriale
##
###
###
### Save Poor Polly from getting run over by the train!
###

from procgame import *
import cc_modes
import random
import ep

class BankRobbery(ep.EP_Mode):
    """Polly Peril - Hostage at the bank"""
    def __init__(self,game,priority):
        super(BankRobbery, self).__init__(game,priority)
        self.running = False
        self.halted = False
        self.position = [-49,-4,43]
        self.y_pos = 7
        self.isActive = [True,True,True]
        self.shots = [self.game.left_ramp,self.game.center_ramp,self.game.right_ramp]
        self.won = False

    def mode_started(self):
        self.modeTimer = 0
        # point value for shots
        self.shotValue = 250000
        self.isActive = [True,True,True]
        self.won = False
        self.have_won = False
        self.banner = False
        # stuff for the random shootering
        self.shotTimer = 0
        self.shotTarget = 0
        self.shooting = False
        self.shooter = 0
        self.shotWait = 0

        # set up the dude standing layers
        self.dude0 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH + 'dude-shoots-bank.dmd').frames[0])
        self.dude0.set_target_position(self.position[0],self.y_pos)
        self.dude0.composite_op = "blacksrc"
        self.dude1 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH + 'dude-shoots-bank.dmd').frames[0])
        self.dude1.set_target_position(self.position[1],self.y_pos)
        self.dude1.composite_op = "blacksrc"
        self.dude2 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH + 'dude-shoots-bank.dmd').frames[0])
        self.dude2.set_target_position(self.position[2],self.y_pos)
        self.dude2.composite_op = "blacksrc"

        # set the dude layers to the starting layer
        self.dude0Layer = self.dude0
        self.dude1Layer = self.dude1
        self.dude2Layer = self.dude2
        self.layers = [self.dude0Layer,self.dude1Layer,self.dude2Layer]

        # load the shot animation
        self.shotAnim = dmd.Animation().load(ep.DMD_PATH+'dude-gets-shot-full-body.dmd')
        # create the layer
        self.deathWait = len(self.shotAnim.frames) / 10.0


        # foreground
        self.foreground = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH + 'bank-interior.dmd').frames[0])
        self.foreground.composite_op = "blacksrc"


    def ball_drained(self):
        if self.game.trough.num_balls_in_play == 0:
            if self.game.show_tracking("rightRampStage") == 4:
                self.game.base.busy = True
                self.polly_died()

    # bonus lanes pause save polly
    def sw_leftBonusLane_active(self,sw):
        if not self.halted:
            self.halt()

    def sw_rightBonusLane_active(self,sw):
        if not self.halted:
            self.halt()

    # bumpers pause quickdraw
    def sw_leftJetBumper_active(self,sw):
        if not self.halted:
            self.halt()

    def sw_rightJetBumper_active(self,sw):
        if not self.halted:
            self.halt()

    def sw_bottomJetBumper_active(self,sw):
        if not self.halted:
            self.halt()

    # so does the mine and both pass the 'advanced' flag to avoid moo sounds
    def sw_minePopper_active_for_390ms(self,sw):
        if not self.halted:
            self.halt()

    def sw_saloonPopper_active_for_290ms(self,sw):
        if not self.halted:
            self.halt()

    def sw_saloonPopper_inactive(self,sw):
        if self.running and self.halted:
            self.halted = False
            self.in_progress()

    # resume when exit
    def sw_jetBumpersExit_active(self,sw):
        if self.running and self.halted:
            # kill the halt flag
            self.halted = False
            self.in_progress()

    def sw_centerRampMake_active(self,sw):
        if self.running:
            self.game.sound.play(self.game.assets.sfx_trainWhistle)
            self.process_shot(1)
        return game.SwitchStop

    def sw_leftRampEnter_active(self,sw):
        if self.running:
            self.game.sound.play(self.game.assets.sfx_leftRampEnter)
            self.process_shot(0)
        return game.SwitchStop

    def sw_rightRampMake_active(self,sw):
        if self.running:
            self.game.sound.play(self.game.assets.sfx_thrownCoins)
            self.process_shot(2)
        return game.SwitchStop

    def process_shot(self,shot):
        # kill the mode timer for good measure
        self.cancel_delayed("Mode Timer")
        # combos
        if self.game.combos.myTimer > 0:
        # register the combo and reset the timer - returns true for use later
            combo = self.game.combos.hit()
        else:
            # and turn on the combo timer - returns false for use later
            combo = self.game.combos.start()

        if self.isActive[shot]:
            # if we hit an active shot, it's a hit
            # set that shot to inactive
            self.isActive[shot] = False
            # update the lamps
            self.shots[shot].update_lamps()
            # score points
            self.game.score(self.shotValue)
            # kill the guy
            self.kill_dude(shot)
        else:
            self.game.score(2370)
            # if we did't hit a shot, restart the mode timer
            self.in_progress()

    def start_bank_robbery(self,step=1):
        if step == 1:
            # set the level 1 stack flag
            self.game.set_tracking('stackLevel',True,1)
            # set the running flag
            self.running = True
            # clear any running music
            print "start_bank_robbery IS KILLING THE MUSIC"
            self.game.sound.stop_music()
            self.game.right_ramp.update_lamps()
            self.game.center_ramp.update_lamps()
            self.game.left_ramp.update_lamps()

            # start the music
            self.game.base.music_on(self.game.assets.music_pollyPeril)
            # run the animation
            anim = dmd.Animation().load(ep.DMD_PATH+'polly-peril.dmd')
            myWait = len(anim.frames) / 30
            animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=True,repeat=False,frame_time=2)
            self.layer = animLayer

            # set the timer for the mode
            self.modeTimer = 30
            # loop back for the title card
            self.delay(delay=myWait,handler=self.start_bank_robbery,param=2)
        if step == 2:
            # pick a shoot delay
            self.set_shot_target()
            # set up the title card
            titleCard = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'polly-peril-hatb.dmd').frames[0])
            # transition to the title card
            self.transition = ep.EP_Transition(self,self.layer,titleCard,ep.EP_Transition.TYPE_WIPE,ep.EP_Transition.PARAM_EAST)
            # delay the start process
            self.delay("Get Going",delay=2,handler=self.in_progress)
            self.delay(delay=2,handler=self.game.base.play_quote,param=self.game.assets.quote_mayhemBank)

    ## this is the main mode loop - not passing the time to the loop because it's global
    ## due to going in and out of pause
    def in_progress(self):
        if self.running:
            #print "IN PROGRESS " + str(self.modeTimer)
            #print "Shooter info: Target - " + str(self.shotTarget) + " Timer - " + str(self.shotTimer)
            # and all the text
            p = self.game.current_player()
            scoreString = ep.format_score(p.score)
            scoreLine = dmd.TextLayer(34, 6, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text(scoreString,blink_frames=8)
            timeString = str(int(self.modeTimer))
            self.timeLine = dmd.TextLayer(128,26, self.game.assets.font_5px_AZ, "right", opaque=False).set_text(timeString)

            # stick together the animation and static text with the dynamic text
            composite = dmd.GroupedLayer(128,32,[self.dude0Layer,self.dude1Layer,self.dude2Layer,self.foreground,self.timeLine])
            self.layer = composite

            # increment the shot timer
            self.shotTimer += 1
            # check if time to shoot
            if self.shotTimer == self.shotTarget:
                # if it is that time, generate a firing guy
                self.dude_shoots()

            # did we just kill the last guy?
            if self.have_won:
                self.have_won = False
                # delay for the dude getting shot animation to finish
                self.delay(delay=self.deathWait,handler=self.polly_saved)
            # how about any guy?
            if self.banner:
                self.banner = False
                # if we need to show a dude killed banner, do that
                self.delay(delay=self.deathWait,handler=self.banner_display)
            # is a guy shooting?
            if self.shooting:
                self.shooting = False
                # set a delay to put the plain guy back after
                self.delay(delay=self.shotWait,handler=self.end_shot_sequence)
            # both of those bail before ticking down the timer and looping back

            ## tick down the timer
            self.modeTimer -= 0.1
            ## hurry quote at 5 seconds
            if abs(self.modeTimer - 5) < 0.00000001:
                self.game.base.play_quote(self.game.assets.quote_hurry)
            if self.modeTimer <= 0:
                # go to a grace period
                self.polly_died()
            # otherwise ...
            else:
                # set up a delay to come back in 1 second with the lowered time
                self.delay(name="Mode Timer",delay=0.1,handler=self.in_progress)

    def kill_dude(self,shot):
        # if the guy died was about to shot, that should be stopped
        if shot == self.shooter and self.shooting:
            # turn the flag off
            self.shooting = False
            # and get a new time/guy
            self.set_shot_target()

        # killing the get going delay just in case a guy is shot before we're started
        if self.modeTimer > 29:
            self.cancel_delayed("Get Going")
        print "KILLING DUDE " + str(shot)
        animLayer = dmd.AnimatedLayer(frames=self.shotAnim.frames,hold=True,opaque=False,repeat=False,frame_time=6)
        animLayer.composite_op = "blacksrc"
        # set the target position based on the shot
        animLayer.set_target_position(self.position[shot],self.y_pos)
        # set the layer
        if shot == 0:
            self.dude0Layer = animLayer
        elif shot == 1:
            self.dude1Layer = animLayer
        elif shot == 2:
            self.dude2Layer = animLayer
        else:
            # WAT?
            pass
        # play a shot sound
        self.game.sound.play(self.game.assets.sfx_gunfightShot)
        # set a won flag if they're all dead
        if True not in self.isActive:
            self.have_won = True
            self.won = True
        else:
            self.banner = True
        # then go to in_progress to restart the timer
        self.in_progress()

    def halt(self):
        print "HALTING -- BUMPERS/MINE/SALOON"
        # cancel delays
        self.cancel_delayed("Mode Timer")
        # this is the initial delay - have to include it in case of a straight shot to the mine off the ramp
        self.cancel_delayed("Get Going")
        # set the flag
        self.halted = True

    # success
    def polly_saved(self):
        self.game.score(750000)
        self.running = False
        self.cancel_delayed("Mode Timer")
        self.game.sound.stop_music()
        self.win_display()

    # fail
    def polly_died(self):
        self.running = False
        self.cancel_delayed("Mode Timer")
        self.end_bank_robbery()

    def win_display(self,step=1):
        if step == 1:
            self.game.base.play_quote(self.game.assets.quote_victory)
            # frame layer of the dead guy
            self.layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'our-hero.dmd').frames[0])
            self.delay("Display",delay=0.5,handler=self.win_display,param=2)
        if step == 2:
            # the pan up
            anim = dmd.Animation().load(ep.DMD_PATH+'our-hero.dmd')
            # math out the wait
            myWait = len(anim.frames) / 60.0
            # set the animation
            animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=1)
            # turn it on
            self.layer = animLayer
            # loop back for the finish animation
            self.delay("Display",delay=myWait,handler=self.win_display,param=3)
        if step == 3:
            anim = dmd.Animation().load(ep.DMD_PATH+'bank-victory-animation.dmd')
            myWait = len(anim.frames) / 8.57
            animLayer = ep.EP_AnimatedLayer(anim)
            animLayer.hold=True
            animLayer.frame_time = 7

            animLayer.add_frame_listener(7,self.game.sound.play,param=self.game.assets.sfx_blow)
            animLayer.add_frame_listener(14,self.game.sound.play,param=self.game.assets.sfx_grinDing)
            # play animation
            self.layer = animLayer
            self.delay("Display",delay=myWait,handler=self.win_display,param=4)
        if step == 4:
            # saved banner goes here
            awardTextString = "POLLY SAVED"
            awardScoreString = "750,000"
            # combine them
            completeFrame = self.build_display(awardTextString,awardScoreString)
            # swap in the new layer
            self.layer = completeFrame
            self.delay(name="Display",delay=2,handler=self.end_bank_robbery)
            # show combo display if the chain is high enough
            if self.game.combos.chain > 1:
                self.delay(name="Display",delay=2,handler=self.game.combos.display)

    def banner_display(self):
        # halt the mode timer for a second
        self.cancel_delayed("Mode Timer")
        # turn the banner off
        self.banner = False
        total = 0
        # count up the remaining shots
        for shot in self.isActive:
            if shot:
                total += 1
        # build a text line with that
        awardTextString = str(total) + " MORE TO GO"
        # build the display layer
        banner = self.build_display(awardTextString,"250,000")
        # activate it
        self.layer = banner
        # delay a return to in progress
        self.delay(delay=1.5,handler=self.in_progress)

    def build_display(self,awardTextString,awardScoreString):
        # create the two text lines
        awardTextTop = dmd.TextLayer(128/2,3,self.game.assets.font_5px_bold_AZ_outline,justify="center",opaque=False)
        awardTextBottom = dmd.TextLayer(128/2,11,self.game.assets.font_15px_az_outline,justify="center",opaque=False)
        awardTextBottom.composite_op = "blacksrc"
        awardTextTop.composite_op = "blacksrc"
        awardTextTop.set_text(awardTextString)
        awardTextBottom.set_text(awardScoreString)
        # combine them
        completeFrame = dmd.GroupedLayer(128, 32, [self.layer,awardTextTop,awardTextBottom])
        # swap in the new layer
        return completeFrame

    def end_bank_robbery(self):
        # stop the polly music
        print "end_river_chase IS KILLING THE MUSIC"
        self.game.sound.stop_music()
        self.layer = None
        # set the tracking on the ramps
        self.game.set_tracking('rightRampStage',5)
        self.game.update_lamps()
        self.end_save_polly()

    # clean up and exit
    def end_save_polly(self):
        print "ENDING SAVE POLLY"
        # turn the level 1 stack flag back off
        self.game.set_tracking('stackLevel',False,1)
        # check to see if stampede is ready - if we're not ending due to ball fail
        if self.game.trough.num_balls_in_play != 0:
            self.game.base.check_stampede()
            # unset the busy flag
        self.game.base.busy = False
        # turn the music back on
        if not self.game.show_tracking('stackLevel',1) and self.game.trough.num_balls_in_play != 0:
            self.game.base.music_on(self.game.assets.music_mainTheme)
            # unload the mode
        self.unload()

    def set_shot_target(self):
        # pick a random target time
        self.shotTarget = random.randrange(35, 50, 1)
        # reset the counter
        self.shotTimer = 0

    def dude_shoots(self):
        # load the animation
        anim = dmd.Animation().load(ep.DMD_PATH+'dude-shoots-bank.dmd')
        # math out the wait
        self.shotWait = len(anim.frames) / 10.0
        # the shoots back animation
        eGuy0 = ep.EP_AnimatedLayer(anim)
        eGuy0.hold=True
        eGuy0.frame_time=6
        eGuy0.composite_op = "blacksrc"
        eGuy0.add_frame_listener(2,self.game.sound.play,param=self.game.assets.sfx_explosion11)
        eGuy0.add_frame_listener(4,self.game.sound.play,param=self.game.assets.sfx_explosion11)

        # get the available bad guys into a list
        dudes = []
        if self.isActive[0]: dudes.append(0)
        if self.isActive[1]: dudes.append(1)
        if self.isActive[2]: dudes.append(2)
        print "DUDES:"
        print dudes
        # pick a random guy to shoot
        self.shooter = random.choice(dudes)
        print "THE SHOOTER IS: " + str(self.shooter)
        # set the position of the layer based on choice
        eGuy0.set_target_position(self.position[self.shooter],self.y_pos)
        # assign the layer to the positon of the shooter
        if self.shooter == 0:
            self.dude0Layer = eGuy0
        elif self.shooter == 1:
            self.dude1Layer = eGuy0
        elif self.shooter == 2:
            self.dude2Layer = eGuy0
            # set a flag
        self.shooting = True

    def end_shot_sequence(self):
        # if the guy who was shooting is still alive, reset their layer
        if self.shooter == 0 and self.isActive[0]:
            self.dude0Layer = self.dude0
        elif self.shooter == 1 and self.isActive[1]:
            self.dude1Layer = self.dude1
        elif self.shooter == 2 and self.isActive[2]:
            self.dude2Layer = self.dude2
        # assign a new dude
        self.set_shot_target()

    def abort_display(self):
        # if we're done, we should quit
        if True not in self.isActive:
            self.end_bank_robbery()
        self.cancel_delayed("Display")
        self.layer = None



