# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 10:31:27 2025
@author: fvopsta1
Mental rotation dot-task
"""

# import relevant libraries 
from psychopy import core, visual, data, event, clock, gui 
from psychopy.hardware import keyboard
from psychopy.visual.circle import Circle
import tobii_research as tobii
import os
import random 
import math

# determine path
my_directory = os.getcwd()

# Initialize eyetracker (replace with your actual eyetracker setup)
try:
    tr = tobii.find_all_eyetrackers()[0]
    print("Address: " + tr.address)
    print("Model: " + tr.model)
    print("Name (It's OK if this is empty): " + tr.device_name)
    print("Serial number: " + tr.serial_number)
except IndexError:
    print("No eyetracker found. Continuing without eyetracker.")
    tr = None

trial_GazeData = []
save_ET_data = False

def gaze_data_callback(gaze_data):
    # Print gaze points of left and right eye
    if save_ET_data:
        trial_GazeData.append(gaze_data)

if tr:
    tr.subscribe_to(tobii.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

Instructions_directory = my_directory + "\\Instructions\\"

# Create data folder if it doesn't exist yet
if not os.path.isdir('Dot_Data'):
    os.mkdir('Dot_Data')

# gui for participant information
expInfo = {'Participant number': '001', 'Gender': ['Female', 'Male', 'Other', 'Prefer not to say'], 'Age': '18', 'Handedness': ['Right', 'Left', 'Ambidextrous']} 
dlg = gui.DlgFromDict(dictionary = expInfo, title = 'Participant Information')
if not dlg.OK:
    core.quit() # cancel

# create datafile 
expName = 'DotRotationTask' 
expInfo['date'] = data.getDateStr() # add timestamp
file_name = 'Dot_Data/data_%s_%s_%s' % (expInfo['Participant number'], expName, expInfo['date']) + ".csv"

# write away data 
ThisExp = data.ExperimentHandler(dataFileName = file_name, extraInfo = expInfo)


# Timing
my_clock = core.Clock()

# Prepare graphical elements
#colorstim   = ('white') 
backcolor   = (-1, -1, -1)  # White in PsychoPy's color space
colorstim   = (1, 1, 1)  # Black in PsychoPy's color space

# Window 
win = visual.Window(size = (400, 200), fullscr = True, colorSpace = 'rgb', color = backcolor, units = 'pix') #black screen, no fullscr debugging 
#win = visual.Window(fullscr = True, colorSpace = 'rgb', color = (-1,-1,-1), units = 'pix') #black screen, no fullscr debugging 
stimSize    = 40
Fix         = visual.TextStim(win, text = "+", color = colorstim, height = stimSize)
circle      = visual.Circle(win, units = 'pix', radius = 10, lineColor = colorstim)
Txt_tmp     = visual.TextStim(win, text = "", color = colorstim, height = stimSize)
feedback    = visual.TextStim(win, text = "", color = colorstim, height = stimSize  )

min_size = 50
max_size = 150

# define keyboard 
key_resp        = keyboard.Keyboard()
key_resp.keys   = []
space           = 'space' 
LeftResponse    = 'a'
RightResponse   = 'l'
EscapeKey       = 'escape'

# some variables
NrTrials        = 160 # 160 x 7.5s/trial = 1200s = 20min
NrExTrials      = 6
StimPresent     = 0.5
MemDelay        = 3
RespWindow      = 3
ITI             = 1
FB_duration     = 2

GetOut          = 0

# Make mouse invisible
win.mouseVisible = False

def  Instructions(win, JPGName):
    instructions = visual.ImageStim(win, image = JPGName, units='norm', size = None, interpolate = True)
    instructions.size *= 1.3 # upscale the size of the image
    instructions.draw()
    win.flip() # present text 
    event.waitKeys(keyList = [space]) # press space to continue 

InstructionsImage = Instructions_directory + "\\Depletion_Instructions.jpg"
Instructions(win, InstructionsImage)

Fix.draw()
win.flip()
core.wait(ITI)

my_clock.reset()

for i in range(0, NrExTrials):
    
    if GetOut == 1:
        break
    
    ##############################
    # Prepare all for this trial #
    ##############################
    
    # Define a position in every quadrant. Then select 3 quadrants to form a triangle
    # Quad1 = upper left, Quad2 = upper right, Quad3 = lower right, Quad4 = lower left
    
    Quad1 = [random.randint(-max_size, -min_size), random.randint(min_size, max_size)]
    Quad2 = [random.randint(min_size, max_size), random.randint(min_size, max_size)]
    Quad3 = [random.randint(min_size, max_size), random.randint(-max_size, -min_size)]
    Quad4 = [random.randint(-max_size, -min_size), random.randint(-max_size, -min_size)]
    
    # Randomly select 3 of the 4 points
    Qlist = [Quad1, Quad2, Quad3, Quad4]
    Qs = random.sample(Qlist, 3)
    
    # Calculate new positions, rotated 30 degrees clockwise
    Qs_new = Qlist[0:3]
    Qs_displ = Qlist[0:3]
    Angle = [0, 0, 0]
    Angle_tmp = [0, 0, 0]
    
    Diff = random.randint(1, 3) # random select difficulty
    Dir = random.randint(0, 359) # random angle for displacement
    NoDispl = random.randint(0,2) # select random dot that will NOT be displaced
    
    for j in range(0, 3):
        Hypo = math.hypot(Qs[j][0], Qs[j][1])
        
        if Qs[j][0] < 0 and Qs[j][1] > 0: # if in quadrant 1, correct angle
            Angle[j] =  90 + (90 - (math.degrees(math.asin(Qs[j][1]/Hypo))))
        elif Qs[j][0] < 0 and Qs[j][1] < 0: # if in quadrant 4, correct angle
            Angle[j] =  180 + -1*(math.degrees(math.asin(Qs[j][1]/Hypo)))
        else:
            Angle[j] =  math.degrees(math.asin(Qs[j][1]/Hypo))
            
        Angle_tmp[j] = math.radians(Angle[j]-30)
        Qs_new[j] = [math.cos(Angle_tmp[j])*Hypo, math.sin(Angle_tmp[j])*Hypo]    
    
        # In case of mismatch, two dots are misplaced
        # easy trials: displacement of ~ 1.9 cm (72 pixels)
        # medium trials: ~ 1.5 cm (57 pixels)
        # hard trials: ~ 1.1 cm (41 pixels)
        # randomly chose 2 dots, and chose direction of displacement
         
        if Diff == 1:
            Length = 72 # Easy - largest displacement
        elif Diff == 2:
            Length =  57 # Medium - medium displacement
        else:
            Length = 41 # Difficult - smallest displacement
            
        x_displ = math.cos(math.radians(Dir))*Length
        y_displ = math.sin(math.radians(Dir))*Length
        
        if j != NoDispl: # one of the dots will not be displaced
            Qs_displ[j] = [Qs_new[j][0] + x_displ, Qs_new[j][1] + y_displ]
        else:
            Qs_displ[j] = Qs_new[j]
    
    # 50% should be match trials. ONLY IN EXERCISE TRIALS. Match  = 1
    Match = random.choices((0, 1), weights = [0.5, 0.5], k = 1)
       
    #############################################
    # Start presenting things - start real trial
    #############################################
       
    # Display 3 full circles in geometric pattern
    circle.lineColor    = colorstim
    circle.fillColor    = colorstim
    circle.pos          = Qs[0]
    circle.draw()
    circle.pos          = Qs[1]
    circle.draw()
    circle.pos          = Qs[2]
    circle.draw()
    Fix.draw()
    win.flip()
    
    timestamp = my_clock.getTime()
    StimStartTime = my_clock.getTime() # TrialStart
    core.wait(StimPresent)
      
    StimEndTime = my_clock.getTime()
    
    Fix.draw()
    win.flip()
    core.wait(MemDelay)
    
    MemoryEndTime = my_clock.getTime()
    
    circle.fillColor = backcolor
    circle.lineColor = colorstim
    print(Match[0])
    if Match[0] == 1:
        # circle.lineColor = [1, 1, 1]
        for k in range(0,3):
            circle.pos = Qs_new[k]
            circle.draw()
    else:     
        for k in range(0,3):
            circle.pos = Qs_displ[k]
            circle.draw() 
    
    Fix.draw()
    win.flip()
    ProbeStartTime = my_clock.getTime()
    tmp_rt = my_clock.getTime()
    RespGiven = 0
    resp = []
    Acc = 0
    event.clearEvents() 
    RT = 0
    
    while (tmp_rt - ProbeStartTime < RespWindow):
        tmp_rt = my_clock.getTime()
        if RespGiven == 0:
            resp  = event.getKeys(keyList = [LeftResponse, RightResponse, EscapeKey])
                
            if len(resp) > 0:
                resp        = [resp[0]]
                RT          = tmp_rt - ProbeStartTime
                RespGiven   = 1
                if ((resp[0] == LeftResponse) and Match[0] == 1) or ((resp[0] == RightResponse) and Match[0] == 0):
                    Acc = 1    # match = Left response, non-match = Right response
                elif resp[0] == EscapeKey:
                    GetOut = 1
                    break 
                
    # while (tmp_rt - ProbeStartTime < RespWindow) and (RespGiven == 0):
    #     tmp_rt = my_clock.getTime()
    #     if RespGiven == 0:
    #         resp  = event.getKeys(keyList = [LeftResponse, RightResponse, EscapeKey])
                
    #         if len(resp) > 0:
    #             resp        = [resp[0]]
    #             RT          = tmp_rt - ProbeStartTime
    #             RespGiven   = 1
    #             if ((resp[0] == LeftResponse) and Match[0] == 1) or ((resp[0] == RightResponse) and Match[0] == 0):
    #                 Acc = 1    # match = Left response, non-match = Right response
    #             elif resp[0] == EscapeKey:
    #                 GetOut = 1
    #                 break 

    # Set feedback text
    if Acc == 1:
        feedback.text = 'Correct'
    else:
        feedback.text = 'Incorrect'

    # Display feedback
    feedback.draw()
    win.flip()
    core.wait(FB_duration)  # Show feedback for 2 seconds
    
    Fix.draw()
    win.flip()
    core.wait(ITI)
    
##########################
# End of exercise trials #
##########################

InstructionsImage = Instructions_directory + "\\StartRealExperiment.jpg"
Instructions(win, InstructionsImage)

Fix.draw()
win.flip()
core.wait(ITI)

my_clock.reset()

for i in range(0, NrTrials):
    
    if GetOut == 1:
        break
    
    ##############################
    # Prepare all for this trial #
    ##############################
    
    # Define a position in every quadrant. Then select 3 quadrants to form a triangle
    # Quad1 = upper left, Quad2 = upper right, Quad3 = lower right, Quad4 = lower left
    
    Quad1 = [random.randint(-max_size, -min_size), random.randint(min_size, max_size)]
    Quad2 = [random.randint(min_size, max_size), random.randint(min_size, max_size)]
    Quad3 = [random.randint(min_size, max_size), random.randint(-max_size, -min_size)]
    Quad4 = [random.randint(-max_size, -min_size), random.randint(-max_size, -min_size)]
    
    # Randomly select 3 of the 4 points
    Qlist = [Quad1, Quad2, Quad3, Quad4]
    Qs = random.sample(Qlist, 3)
    
    # Calculate new positions, rotated 30 degrees clockwise
    Qs_new = Qlist[0:3]
    Qs_displ = Qlist[0:3]
    Angle = [0, 0, 0]
    Angle_tmp = [0, 0, 0]
    
    Diff = random.randint(1, 3) # random select difficulty
    Dir = random.randint(0, 359) # random angle for displacement
    NoDispl = random.randint(0,2) # select random dot that will NOT be displaced
    
    for j in range(0, 3):
        Hypo = math.hypot(Qs[j][0], Qs[j][1])
        
        if Qs[j][0] < 0 and Qs[j][1] > 0: # if in quadrant 1, correct angle
            Angle[j] =  90 + (90 - (math.degrees(math.asin(Qs[j][1]/Hypo))))
        elif Qs[j][0] < 0 and Qs[j][1] < 0: # if in quadrant 4, correct angle
            Angle[j] =  180 + -1*(math.degrees(math.asin(Qs[j][1]/Hypo)))
        else:
            Angle[j] =  math.degrees(math.asin(Qs[j][1]/Hypo))
            
        Angle_tmp[j] = math.radians(Angle[j]-30)
        Qs_new[j] = [math.cos(Angle_tmp[j])*Hypo, math.sin(Angle_tmp[j])*Hypo]    
    
        # In case of mismatch, two dots are misplaced
        # easy trials: displacement of ~ 1.9 cm (72 pixels)
        # medium trials: ~ 1.5 cm (57 pixels)
        # hard trials: ~ 1.1 cm (41 pixels)
        # randomly chose 2 dots, and chose direction of displacement
         
        if Diff == 1:
            Length = 72 # Easy - largest displacement
        elif Diff == 2:
            Length =  57 # Medium - medium displacement
        else:
            Length = 41 # Difficult - smallest displacement
            
        x_displ = math.cos(math.radians(Dir))*Length
        y_displ = math.sin(math.radians(Dir))*Length
        
        if j != NoDispl: # one of the dots will not be displaced
            Qs_displ[j] = [Qs_new[j][0] + x_displ, Qs_new[j][1] + y_displ]
        else:
            Qs_displ[j] = Qs_new[j]
    
    # 70% should be match trials. Match  = 1
    Match = random.choices((0, 1), weights = [0.3, 0.7], k = 1)
       
    #############################################
    # Start presenting things - start real trial
    #############################################
       
    # Display 3 full circles in geometric pattern
    circle.lineColor    = colorstim
    circle.fillColor    = colorstim
    circle.pos          = Qs[0]
    circle.draw()
    circle.pos          = Qs[1]
    circle.draw()
    circle.pos          = Qs[2]
    circle.draw()
    Fix.draw()
    win.flip()
    
    timestamp = my_clock.getTime()
    StimStartTime = my_clock.getTime() # TrialStart
    core.wait(StimPresent)
      
    StimEndTime = my_clock.getTime()
    
    Fix.draw()
    win.flip()
    core.wait(MemDelay)
    
    MemoryEndTime = my_clock.getTime()
    
    circle.fillColor = backcolor
    circle.lineColor = colorstim
    if Match[0] == 1:
        # circle.lineColor = [1, 1, 1]
        for k in range(0,3):
            circle.pos = Qs_new[k]
            circle.draw()
    else:     
        for k in range(0,3):
            circle.pos = Qs_displ[k]
            circle.draw() 
    
    Fix.draw()
    win.flip()
    ProbeStartTime = my_clock.getTime()
    tmp_rt = my_clock.getTime()
    RespGiven = 0
    resp = []
    Acc = 0
    event.clearEvents() 
    RT = 0
    
    while (tmp_rt - ProbeStartTime < RespWindow):
        tmp_rt = my_clock.getTime()
        if RespGiven == 0:
            resp  = event.getKeys(keyList = [LeftResponse, RightResponse, EscapeKey])
                
            if len(resp) > 0:
                resp        = [resp[0]]
                RT          = tmp_rt - ProbeStartTime
                RespGiven   = 1
                if ((resp[0] == LeftResponse) and Match[0] == 1) or ((resp[0] == RightResponse) and Match[0] == 0):
                    Acc = 1    # match = Left response, non-match = Right response
                elif resp[0] == EscapeKey:
                    GetOut = 1
                    break 
                
    # while (tmp_rt - ProbeStartTime < RespWindow) and (RespGiven == 0):
    #     tmp_rt = my_clock.getTime()
    #     if RespGiven == 0:
    #         resp  = event.getKeys(keyList = [LeftResponse, RightResponse, EscapeKey])
                
    #         if len(resp) > 0:
    #             resp        = [resp[0]]
    #             RT          = tmp_rt - ProbeStartTime
    #             RespGiven   = 1
    #             if ((resp[0] == LeftResponse) and Match[0] == 1) or ((resp[0] == RightResponse) and Match[0] == 0):
    #                 Acc = 1    # match = Left response, non-match = Right response
    #             elif resp[0] == EscapeKey:
    #                 GetOut = 1
    #                 break 

    if resp == []:
        resp = [99]
    
    ThisExp.addData('Participant', expInfo['Participant number'])
    ThisExp.addData('Age', expInfo['Age'])
    ThisExp.addData('Handedness', expInfo['Handedness'])
    ThisExp.addData('Trial', i)
    ThisExp.addData('Diff', Diff)
    ThisExp.addData('Match', Match[0])
    ThisExp.addData('Response', resp[0])
    ThisExp.addData('RT', RT)
    ThisExp.addData('Accuracy', Acc)
    ThisExp.addData('Timestamp', timestamp)
    ThisExp.nextEntry()
    
    if (i == 39) or (i == 79) or (i == 119):
        InstructionsImage = Instructions_directory + "\\Break.jpg"
        Instructions(win, InstructionsImage)
        
    Fix.draw()
    win.flip()
    core.wait(ITI)

ThisExp.saveAsWideText(file_name, delim ='auto')
InstructionsImage = Instructions_directory + "\\EndExperiment.jpg"
Instructions(win, InstructionsImage)
win.close()
core.quit()