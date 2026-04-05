#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import core, visual

from psychopy.event import Mouse
from psychopy import locale_setup
from psychopy import prefs
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding
import random
import math
import pandas as pd
from psychopy.hardware import keyboard
from psychopy import data

# Set up path
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Demographic information
expName = 'cape'  # You can put here whatever you want
expInfo = {'participant': '01_aa','gender':'male', 'age':'20','session': '1'}
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
datum = data.getDateStr()  # add a simple timestamp
pp = expInfo['participant']
sessnr = int(expInfo['session'])
gender = expInfo['gender']
age = int(expInfo['age'])

# Name each file
filename = _thisDir + os.sep + u'data/%s_%s' % (pp, expName)
fp = open(filename, 'a')

filename2 = 'ppnumber_%s_%s' % (pp, expName)
if os.path.exists(filename2):
    #read out number in this file
    fp2 = open(filename2, 'r')
    anr = int(fp2.read())
else:
    anr = random.randint(1,1000)
    fp2 = open(filename2, 'w')
    fp2.write('%d' % (anr))
fp2.close()

# ---- Set up item ----

# Stimuli drawing function
def draw_items(shape, colors, pos):
    for i in range(len(pos)):
        if shape[i] == 0:
            item = visual.Rect(
                win, 
                units='pix', 
                size=(50,50),
                colorSpace='rgb',
                lineWidth=5,
                fillColor=colors[i])
        else:
            item = visual.Circle(
                win,
                units='pix',
                radius=np.sqrt(50*50/np.pi),
                colorSpace='rgb',
                lineWidth=5,
                fillColor=colors[i])
        item.pos = pos[i]
        item.draw()

# Set up window
delter, toe =  225/2, -1
screen_color = [0, 0, 0]
screen_color = [(x/delter) + toe for x in screen_color]  # convert to (-1,1)
win = visual. Window(fullscr = True, colorSpace = 'rgb', color = screen_color)

# Set up cue
linergb = [255,255,255]; linergb = [(x / delter) + toe for x in linergb]
cueline = visual.Line(win,units='pix', lineColor=linergb, lineWidth = 5, colorSpace='rgb')

# Shape or colors Text
feat_rec = visual.TextStim(
    win,
    text = ' SHAPE or COLORS ',
    colorSpace = 'rgb',
    color = (1,1,1),
    bold = True,
    units = 'pix',
    pos = (0,0),
    height = 20
    )

# Wrong feedback
wrong = visual.TextStim(
    win,
    text = ' INCORRECT RESPONSE',
    colorSpace = 'rgb',
    color = (1,0,0),
    bold = True,
    units = 'pix',
    pos = (0,0),
    height = 20
    )

# Keyboard + clocktime
key_resp = keyboard.Keyboard()
trial_clock = core.Clock()

#Hiding mouse
mouse = event.Mouse(visible=False, win=win)
mouse.setPos((10000, 10000))  # move far off screen

# Define number of blocks, trials per block
block_num = 5
trial_per_block = 80

# Loading randomized condition
conditions = [
   # second_set_state, change_feature, memory_type)
    ('change', 'shape', 'fVSTM'),
    ('change', 'color', 'fVSTM'),
    ('stay', None, 'fVSTM'),
    ('stay', None, 'fVSTM'),
    ('change', 'shape', 'WM'),
    ('change', 'color', 'WM'),
    ('stay', None, 'WM'),
    ('stay', None, 'WM')
]

# Trial for real recording
rows = conditions * 40
row_list = list(range(len(rows)))
random.shuffle(row_list)

# Trial for practice trial
practice_trial = conditions.copy() 
random.shuffle(practice_trial) # so only 8 trials, participant will practice each situation one time


# Intro to Block text function
def block_name(block_text):
    block_label = visual.TextStim(
        win, 
        text = block_text,
        units = 'pix',
        colorSpace = 'rgb',
        color = (1,1,1),
        bold = True,
        pos = (0,0)
        )
    block_label.draw()

#Dependent variables
accuracy_change = []
accuracy_feat = []
reaction_times = []

# ------- EXPERIMENT START FROM THIS LINE -------
# ---- Introduction + Instruction ----

word_size = 30
# Welcome title 
welcome = visual.TextStim(
    win, 
    text='Welcome to this Experiment', 
    height=50,
    units='pix',
    pos=(0, 320),
    colorSpace='rgb',
    color=(1, 1, 1), 
    wrapWidth=1400,
    bold=True
)
# Task description 
instruction_stim = visual.TextStim(
    win, 
    text='You will see a list of objects aranged on a circle around a center point.\n\n'
         'The objects will disappear briefly, then reappear.\n\n'
         'One object may change, or nothing may change.\n\n'
         'A cue line will show which object might have changed.',
    height=word_size, 
    units='pix',
    pos=(0, 120),  
    colorSpace='rgb',
    color=(0.9, 0.9, 0.9), 
    wrapWidth=1300
)

# Visual divider line
divider = visual.Line(
    win,
    start=(-500, 50),
    end=(500, 50),
    lineColor=(0.5, 0.5, 0.5),
    lineWidth=3
)
# Response keys section header
keys_header = visual.TextStim(
    win,
    text='RESPONSE KEYS',
    height=25,
    units='pix',
    pos=(0, -50),
    colorSpace='rgb',
    color=(1, 1, 0.2), 
    bold=True,
    opacity =.6
)
# Response instructions
instruction_sub = visual.TextStim(
    win, 
    text='Press  "Z"  for CHANGE     |     Press  "M"  for NO CHANGE\n\n'
         'If you correctly detect a change, then indicate which features has been changed\n\n'
         '    "Z"  =  SHAPE changed  (square <=> circle)     |     "M"  =  COLOR changed  (green <=> blue)',
    height=word_size, 
    units='pix',
    pos=(0, -180),  
    colorSpace='rgb',
    color=(0.95, 0.95, 0.95),
    wrapWidth=1300,
    opacity = 1
)
# Ready 
ready = visual.TextStim(
    win, 
    text='Press  SPACEBAR  when you understand and are ready to begin',
    height=25,  
    units='pix',
    pos=(0, -330), 
    colorSpace='rgb',
    color=(0.3, 1, 0.3),  # Bright green to stand out
    wrapWidth=1200,
    bold=True
)
# Draw all elements
welcome.draw()
instruction_stim.draw()
divider.draw()
keys_header.draw()
instruction_sub.draw()
ready.draw() 
win.flip()

# Wait for spacebar
event.waitKeys(keyList=['space'])
    
# ---- Executing experiment ---- 

for block in range(block_num):
    if block == 0:  
        num_trial = len(practice_trial) # 8 
        block_text =  'Practice block. Press z or m to get ready'
    else:
        num_trial = trial_per_block # 80
        block_text = f'Block {block}. Press z or m to get ready'

    block_name(block_text) # write out block introduction
    win.flip()
    event.waitKeys(keyList=['z', 'm'])
    
    # Blank
    win.flip()
    core.wait(2)

    for trial in range(num_trial):
        # Set up trial
        if block == 0: # Practice block
            trial_count = trial
            
            # Selecti condtions for practice blockl
            second_set_state = practice_trial[trial][0]
            change_feature = practice_trial[trial][1]
            memory_type = practice_trial[trial][2]
        
        else: # testing block
            trial_count = trial_per_block * (block-1) + trial
            
            # Select conditions for testing block
            sel_row = row_list[trial_count]
            second_set_state = rows[sel_row][0]
            change_feature = rows[sel_row][1]
            memory_type = rows[sel_row][2]
        
        
        # Set up angle/position
        angle = [45 * i for i in range(8)]
        pos = [(300* np.cos(np.deg2rad(a)), 300* np.sin(np.deg2rad(a))) for a in angle]
        
        # Choosing target / cue for target
        target = np.random.randint(0,8)
        
        x1 = 0.1 * pos[target][0]
        x2 = 0.8 * pos[target][0]
        y1 =  0.1 * pos[target][1]
        y2 =  0.8 * pos[target][1]
        
        cueline.start = (x1,y1)
        cueline.end = (x2, y2)
            
        # Random color and shape + set-up minimum number of each condition
        min_num = 3
        max_num = 5

        ## Color
        while True: 
            colr = np.random.randint(0, 2, 8)
            if min_num <= colr.sum() <= max_num:
                valid = True
                for i in range(8):
                    if colr[(i-1) % 8] == colr[i] and colr[(i+1) % 8] == colr[i]:
                        valid = False
                        break
                if valid:
                    break
        colors = [(0,0,1) if c == 0 else (0,1,0) for c in colr] # change to color code
        
        ## Shape
        while True:
            shape = np.random.randint(0, 2, 8)
            if shape.sum() >= min_num and shape.sum() <= max_num:
                valid = True
                for i in range(8):
                    if shape[(i-1) % 8] == shape[i] and shape[(i+1) % 8] == shape[i]:
                        valid = False
                        break
                if valid:
                    break
            
        #Run based on memory types
        if memory_type == 'fVSTM':
            # Fixated point
            fixate = visual.Circle(
                win, 
                colorSpace = 'rgb',
                fillColor = (1, 1, 1),
                units = 'pix',
                radius = 6)
            fixate.draw()
            
            # 1st screen
            draw_items(shape, colors, pos)
            win.flip()
            core.wait(0.25)
            
            #Blank1
            fixate.draw()
            win.flip()
            core.wait(1)
            
            #Cue
            cueline.draw()
            fixate.draw()
            win.flip()
            core.wait(0.5)
            
            #Blank 2
            fixate.draw()
            win.flip()
            core.wait(0.5)

            
            # Second screen
            if second_set_state == 'change':
                # choose changing object + its change feature
                new_shape = shape.copy()
                new_colors = colors.copy()

                if change_feature == 'shape': 
                    feature_change = 'shape'
                    new_shape[target] = 1 - new_shape[target]
                elif change_feature == 'color': 
                    feature_change = 'color'
                    new_colors[target] = (0,0,1) if colr[target] == 1 else (0,1,0)
                
                # draw 2nd screen
                draw_items(new_shape, new_colors, pos)
                
            elif second_set_state == 'stay':
                draw_items(shape, colors, pos)
            fixate.draw()
            win.flip()
            
            # Record response -  Change or stay
            key_resp.keys_change = []
            key_resp.keys_feat = []
            
            # Reaction Time
            timeold = trial_clock.getTime()
            keys_change = event.waitKeys(keyList=['z', 'm'])
            
            timenew = trial_clock.getTime()
            
            dur = 1000 * (timenew - timeold)
            rt = np.round(dur)
            
            # Accuracy
            acc_change = 0
            acc_feat = 0
            
            pressed_key_change = keys_change[0]
            if pressed_key_change == 'z' and second_set_state == 'change': # Correct change detection
                acc_change = 1
                # Draw feature choice prompt
                feat_rec.draw()
                win.flip()
                
                # Second response: feature
                keys_feat = event.waitKeys(keyList=['z', 'm'])
                pressed_key_feat = keys_feat[0]
            
                if (pressed_key_feat == 'z' and feature_change == 'shape') or (pressed_key_feat == 'm' and feature_change == 'color'): # Correct feature detection
                    acc_feat = 1
                    win.flip()
                    core.wait(1)
                    
                else: # Incorrect feature detection
                    wrong.draw()
                    win.flip()
                    core.wait(1) 
            
            elif pressed_key_change == 'm' and second_set_state == 'stay': # Correct stay detection
                acc_change = 1
                win.flip()
                core.wait(1)
            else: # Incorrect change/stay detection
                wrong.draw()
                win.flip()
                core.wait(1)  
        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif memory_type == 'WM':
            # Fixated point
            fixate = visual.Circle(
                win, 
                colorSpace = 'rgb',
                fillColor = (1, 1, 1),
                units = 'pix',
                radius = 6)
            fixate.draw()
            
            # Screen 1
            draw_items(shape, colors, pos)
            fixate.draw()
            win.flip()
            core.wait(0.25)
            
            # Blank
            fixate.draw()
            win.flip()
            core.wait(1)
            
            # Second Screen - WM
            cueline.start = (x1,y1)
            cueline.end = (x2, y2)

            if second_set_state == 'change':
                new_shape = shape.copy()
                new_colors = colors.copy()

                if change_feature == 'shape': 
                    feature_change = 'shape'
                    new_shape[target] = 1 - new_shape[target]
                elif change_feature == 'color': 
                    feature_change = 'color'
                    new_colors[target] = (0,0,1) if colr[target] == 1 else (0,1,0)
                    
                draw_items(new_shape, new_colors, pos)
                
            elif second_set_state == 'stay':
                draw_items(shape, colors, pos)
            
            # Cue appear concurrently
            cueline.draw()
            fixate.draw()
            win.flip()
            core.wait(0.5)
            
            # Cue disappear
            if second_set_state == 'change':
                draw_items(new_shape, new_colors, pos)
            elif second_set_state == 'stay':
                draw_items(shape, colors, pos)
            win.flip()
            
            # Record response -  Change or stay
            key_resp.keys_change = []
            key_resp.keys_feat = []
            
            # Reaction Time
            timeold = trial_clock.getTime()
            keys_change = event.waitKeys(keyList=['z', 'm'])
            timenew = trial_clock.getTime()
            
            dur = 1000 * (timenew - timeold)
            rt = np.round(dur)
            
            # Accuracy
            acc_change = 0
            acc_feat = 0
            
            pressed_key_change = keys_change[0]
            if pressed_key_change == 'z' and second_set_state == 'change':
                acc_change = 1
                
                # Draw feature choice prompt
                feat_rec.draw()
                win.flip()
                
                # Second response: feature
                keys_feat = event.waitKeys(keyList=['z', 'm'])
                pressed_key_feat = keys_feat[0]
                
                if (pressed_key_feat == 'z' and feature_change == 'shape') or (pressed_key_feat == 'm' and feature_change == 'color'):
                    acc_feat = 1
                    win.flip()
                    core.wait(1)
                else:
                    wrong.draw()
                    win.flip()
                    core.wait(1) 
                    
            elif pressed_key_change == 'm' and second_set_state == 'stay':
                acc_change = 1
                win.flip()
                core.wait(1)
                
            else:
                wrong.draw()
                win.flip()
                core.wait(1)
        
        # Record DI
        accuracy_change.append(acc_change)
        accuracy_feat.append(acc_feat)
        reaction_times.append(rt)
        
        # Write away information
        fp.write('%s %s %s %d %d %s %d %d %s %s %s %d %d %.3f\n' % (
            expName, datum, pp, anr, age, gender, 
            block, trial, second_set_state, change_feature, memory_type, 
            acc_change, acc_feat, rt))
    
        # Blank - 
        win.flip()
        core.wait(1)

# ---- Ending ----
msge = visual.TextStim(win, 'Thank you for participating!.')
msge.draw()
win.flip()
core.wait(2)

fp.close()
win.close()