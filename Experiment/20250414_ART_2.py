########################
  # Alphanumerical Rotaion Task
  # Author: Julia Borys & Jil Bahlig
  # Last edited: 09/04/2025

from psychopy import visual, core, event, gui, data
import tobii_research as tobii
import os, random, pandas as pd
from datetime import datetime
import itertools, time

#########################
# Pilot Testing Settings
    # pilot_n : 10, 10 trials in the experiment, for Full Exp, loop over "trials" instead of "pilot_trials"
    # practice_trials_n = 2 - 2 practice trials 
    # practice_fixation_duration = 2
    # practice_stimulus_duration = 2.5

# Necessary change between ART Time 1 and ART Time 2
    # change n_multiple
        # when n_multiple = 2, 120 trials (2 * unique trials(60)) - 10 minutes - Time 1
        # when n_multiple = 4, 240 trials (4 * unique trials(60)) - 20 minutes - Time 2

############
# INITIALISATION
############

my_directory = os.getcwd()
Instructions_directory = my_directory + "\\Instructions\\"

############
# Eyetracker

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

    tr.subscribe_to(tobii.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    time.sleep(3)



############
# DATAFILE
############

# Create data folder if it doesn't exist yet
if not os.path.isdir('ART_Data_2'):
    os.mkdir('ART_Data_2')

# GUI for participant information
expInfo = {'Participant number': '001', 'Gender': ['Female', 'Male', 'Other', 'Prefer not to say'], 'Age': '18', 'Handedness': ['Right', 'Left', 'Ambidextrous']}
dlg = gui.DlgFromDict(dictionary = expInfo, title = 'Participant Information')
if not dlg.OK:
    core.quit()  # User canceled the dialog

# Create datafile
expName = 'Alphanumerical_Rotation_Task'
expInfo['date'] = data.getDateStr()  # Add timestamp
filename = f"ART_Data_2/data_{expInfo['Participant number']}_{expName}_{expInfo['date']}"

filenameET = f"ART_Data_2/ETdata_{expInfo['Participant number']}_{expName}_{expInfo['date']}.csv"
ET_out = open(filenameET, 'w')
# Write away data
ThisExp = data.ExperimentHandler(dataFileName=filename, extraInfo=expInfo)

############
# PARAMETERS
############

n_trials = 120
pilot_n = 10 # for pilot testing
n_multiple = 4 # x: 60*x stimuli, in this case 60*2 = 120 stimuli (10 mins exp. time); for ART Time 2, change to 4 to double exp. time (20 mins)
stimulus_duration = 2.5  # in seconds
background_color = (-1, -1, -1)  # White in PsychoPy's color space
stimulus_color = (1, 1, 1)  # Black in PsychoPy's color space
stimulus_size = 50
fixation_duration_range = (1.5, 2.5)  # Fixation duration range in seconds

go_stimuli = ['2', '3', '4', '5', '7']
no_go_stimuli = ['F', 'P', 'R', 'G', 'Q']
rotations = [30, 90, 150]
mirrored = [False, True]

############
# INITIALISATION
############

# Define keyboard
SpaceKey = 'space'
EscapeKey = 'escape'
SKey = 'a'
KKey = 'l'

GetOut = 0  # Initialise exit
clock = core.Clock()  # Timer for reaction time
exp_clock = core.Clock()  # Global clock for experiment timestamp

############
# EXPERIMENTAL WINDOW
############

# Initialize PsychoPy window
win = visual.Window(size = (1000, 800), fullscr=True, color=background_color, units="pix", screen=0)

# Make mouse invisible
win.mouseVisible = False

############
#FIXATION and STIMULI
############

# fixation cross
fixation = visual.TextStim(win, text='+', color=stimulus_color, height= stimulus_size)

# text stimulus for numbers/letters
stimulus = visual.TextStim(win, text="", color=stimulus_color, height=stimulus_size)

# Generate balanced stimulus set with 2x each unique stimulus
    # 5 numbers + 5 letters = 10 stimuli; 2 mirrored conditions; 3 rotations
    # possible unique trials = 10 x 2 x 3 = 60
    
# Generate all unique stimuli (60)
all_combinations = list(itertools.product(go_stimuli + no_go_stimuli, mirrored, rotations))

def generate_stimuli():
    trials = all_combinations
    return [{'stimulus': stim, 'is_mirrored': mirr, 'rotation': rot, 'is_go_trial': stim in go_stimuli} for stim, mirr, rot in trials]

unique_trials = generate_stimuli()

#use for pilot testing (up to k=60)
pilot_trials = random.sample(unique_trials, k = pilot_n) # select random sample from trials without replacement

############
# INSTRUCTIONS
############

def  Instructions(win, JPGName):
    instructions = visual.ImageStim(win, image = JPGName, units='norm', size = None, interpolate = True)
    instructions.size *= 1.3 # upscale the size of the image
    instructions.draw()
    win.flip() # present text 
    event.waitKeys(keyList = [SpaceKey]) # press space to continue 


# instructions 
InstructionsImage = Instructions_directory + "\\ART_Instructions.jpg"
Instructions(win, InstructionsImage)

############
# PRACTICE TRIAL
############

# Initialisation
practice_trials_n = 6
practice_fixation_duration = 2
practice_stimulus_duration = 2.5
Trialnr = 0
Block = 0

# Feedback
feedback = visual.TextStim(win, text="", color=stimulus_color, height=stimulus_size)

# Create practice stimuli
random.seed(123) # ensures all participants receive same practice trials
practice_trials = random.sample(unique_trials, k=practice_trials_n)

# Practice trial loop
for trial in practice_trials:
    if GetOut == 1:   # Check for exit
        break

    # Set stimulus properties
    stimulus.text = trial['stimulus']
    stimulus.ori = trial['rotation']
    stimulus.flipHoriz = trial['is_mirrored']

    # Fixation
    fixation.draw()
    win.flip()
    core.wait(practice_fixation_duration)

    
    # Prepare stimulus and response variables
    stimulus.draw()
    event.clearEvents() # Clear previous responses
    
    #core.wait(practice_stimulus_duration)

    resp = []
    resp_given = 0
    Acc = 0
    RT = None
    
    # Show stimulus
    win.flip() 
    
    #Timestamp (time elapsed since start experiment) after stimulus presentation
    #timestamp = exp_clock.getTime()
    
    # Start response time
    start_rt = clock.getTime()
    temp_rt = clock.getTime()

    # Response collection getKeys
    while temp_rt - start_rt < practice_stimulus_duration:
        temp_rt = clock.getTime()
        if resp_given == 0:
            resp = event.getKeys(keyList = [SKey, KKey, EscapeKey])
            
            if len(resp) > 0:
                resp = [resp[0]]
                RT = temp_rt - start_rt
                resp_given = 1
                timestamp = exp_clock.getTime()  # timestamp at response

    if len(resp) > 0:
        if trial['stimulus'] in go_stimuli:
            if (resp[0] == SKey and not trial['is_mirrored']):
                Acc = 1
            elif (resp[0] == KKey and trial['is_mirrored']):
                Acc = 1
        else:
            Acc = 0

        if resp[0] == EscapeKey:
            GetOut = 1
            break

    else:
        if trial['stimulus'] in no_go_stimuli:
            Acc = 1

    # Set feedback text
    if Acc == 1:
        feedback.text = 'Correct'
    else:
        feedback.text = 'Incorrect'

    # Display feedback
    feedback.draw()
    win.flip()
    core.wait(2)  # Show feedback for 2 seconds

    #win.flip()

    # Exit if escape key was pressed
    if GetOut == 1:
        break

#################
# Practive Over

# Randomise trial presentation
random.seed(None) # ensures all participants receive different order of trials
trials = unique_trials * n_multiple # 60 unique trials * n_multiple  => number of trials 
random.shuffle(trials)  # randomize order of trials

# Tell participants that exercise is over and real experiment starts
InstructionsImage = Instructions_directory + "\\StartRealExperiment_ART.jpg"
Instructions(win, InstructionsImage)

##########################
# START MAIN EXPERIMENT
##########################


exp_clock.reset() # Reset clock for main experiment
tr.subscribe_to(tobii.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
time.sleep(3)

#StartTimeStamp = gaze_data['device_time_stamp']

for trial in trials: # Change "pilot_trials" to "trials" for Full Experiment!
    if GetOut == 1:   # Check for exit
        break

    # Set stimulus properties
    stimulus.text = trial['stimulus']
    stimulus.ori = trial['rotation']
    stimulus.flipHoriz = trial['is_mirrored']

    # Fixation
    fixation_duration = 2#random.uniform(*fixation_duration_range)  # random float between 1.5 and 2.5, fixation varies per trial
    exp_clock.reset()
    save_ET_data = True
    fixation.draw()
    win.flip()
    core.wait(fixation_duration)

    # Prepare stimulus and response variables
    stimulus.draw()

    resp = []
    resp_given = 0
    Acc = 0
    RT = None
    
    event.clearEvents() # Clear any previous responses
    
    # Show Stimulus
    win.flip() 
    
    # time elapsed from start experiment after stimulus presentation - for eyetracker data syncing
    StimOnset = exp_clock.getTime()
    
    # Start response time
    start_rt = clock.getTime()
    temp_rt = clock.getTime()

    # Response collection getKeys
    while temp_rt - start_rt < stimulus_duration:
        temp_rt = clock.getTime()
        if resp_given == 0:
            resp = event.getKeys(keyList = [SKey, KKey, EscapeKey])
            
            if len(resp) > 0:
                resp = [resp[0]]
                RT = temp_rt - start_rt
                resp_given = 1
                #timestamp = exp_clock.getTime()  # timestamp at response if response given - optional

    if len(resp) > 0:
        if trial['stimulus'] in go_stimuli:
            if (resp[0] == SKey and not trial['is_mirrored']): #SKey - normal
                Acc = 1
            elif (resp[0] == KKey and trial['is_mirrored']): #KKey - mirrored
                Acc = 1
        else: #if no response given to go stimulus
            Acc = 0

        if resp[0] == EscapeKey:
            GetOut = 1
            break

    else: #if no response is given
        if trial['stimulus'] in no_go_stimuli: #correct if NoGo trial
            Acc = 1

    Trialnr += 1
    if Trialnr < 120:
        Block = 1
    else:
        Block = 2    

    # Store trial info
    ThisExp.addData('Participant', expInfo['Participant number'])
    ThisExp.addData('Age', expInfo['Age'])
    ThisExp.addData('Handedness', expInfo['Handedness'])
    ThisExp.addData('Trial', Trialnr)
    ThisExp.addData('Block', Block)
    ThisExp.addData('Stimulus', trial['stimulus'])
    ThisExp.addData('Rotation', trial['rotation'])
    ThisExp.addData('Mirrored', trial['is_mirrored'])
    ThisExp.addData('Response', resp if resp else None)
    ThisExp.addData('RT', RT)
    ThisExp.addData('Accuracy', Acc)
    ThisExp.addData('Timestamp', StimOnset)
    ThisExp.nextEntry()

    save_ET_data = False

    time_offset = trial_GazeData[0]['device_time_stamp'] / 1000

    for j in range(len(trial_GazeData)):
        ET_out.write(str(Trialnr) + "\t{timestamp}\t{gaze_right_eye}\t{pupil_right_eye}\n".format(
            timestamp = (trial_GazeData[j]['device_time_stamp'] /1000 - time_offset),
            gaze_right_eye = trial_GazeData[j]['right_gaze_point_on_display_area'],
            pupil_right_eye = trial_GazeData[j]['right_pupil_diameter']))

    trial_GazeData.clear()

    # Exit if escape key was pressed
    if GetOut == 1:
        break
        
    if (Trialnr == 119):
        InstructionsImage = Instructions_directory + "\\Break.jpg"
        Instructions(win, InstructionsImage)

# ThisExp.saveAsWideText(filename, delim =',')

tr.unsubscribe_from(tobii.EYETRACKER_GAZE_DATA, gaze_data_callback)

ET_out.close()
####################
# Outro
InstructionsImage = Instructions_directory + "\\EndExperiment.jpg"
Instructions(win, InstructionsImage)

# End of experiment
win.close()
core.quit()