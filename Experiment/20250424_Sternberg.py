#####################################
  # Sternberg Task
  # Author: Julia Borys & Jil Bahlig
  # Last edited: 09/04/2025
#####################################

#######################
# Current pilot settings:
# n_trials_block - no. trials per block set to 5
# block rest_period - set to 10 seconds
# practice_trials_n - set to 2 practice trials
#######################


########################
#   DEPENDENCIES
########################

from psychopy import visual, core, event, gui, data
import os, random, string, itertools
import tobii_research as tobii
import pandas as pd
from datetime import datetime

########################
#   INITIALISATION
########################

#############
# Eyetracker
#############

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

############
# DATAFILE
############

my_directory = os.getcwd()
Instructions_directory = my_directory + "\\Instructions\\"

# Create data folder if it doesn't exist yet
if not os.path.isdir('Sternberg_Data'):
    os.mkdir('Sternberg_Data')

# GUI for participant information
expInfo = {'Participant number': '001', 'Gender': ['Female', 'Male', 'Other', 'Prefer not to say'], 'Age': '18', 'Handedness': ['Right', 'Left', 'Ambidextrous']}
dlg = gui.DlgFromDict(dictionary=expInfo, title='Participant Information')
if not dlg.OK:
    core.quit()  # User canceled the dialog

# Create datafile
expName = 'Sternberg_Task'
expInfo['date'] = data.getDateStr()  # Add timestamp
filename = f"Sternberg_Data/data_{expInfo['Participant number']}_{expName}_{expInfo['date']}.csv"

# Write away data
ThisExp = data.ExperimentHandler(dataFileName=filename, extraInfo=expInfo)

n_trials = 160 # number of trials - 216 for Full Experiment
# n_trials_block = 5 # number of trials per block 54 for Full Experiment
# n_blocks = 4 # number of blocks
stimulus_duration = 0.5  # in seconds, 500ms
retention_duration = 3 # in seconds, 3000ms
probe_duration = 3 # in seconds, 3000ms
rest_period = 10 # in seconds, rest between blocks - 60 seconds for Full Experiment
background_color = (-1, -1, -1)  # Black 
stimulus_color = (1, 1, 1)  # White
stimulus_size = 40 #0.1
rest_text_size = 40 #0.05
fixation_size = 40
fixation_duration =  1 # Inter-stimulus interval, 1000ms

########################
# EXPERIMENTAL WINDOW
########################

# Initialize PsychoPy window
win = visual.Window(size = (1000, 800), fullscr=True, color=background_color, units="pix", screen=0) 

def  Instructions(win, JPGName):
    instructions = visual.ImageStim(win, image = JPGName, units='norm', size = None, interpolate = True)
    instructions.size *= 1.3 # upscale the size of the image
    instructions.draw()
    win.flip() # present text 
    event.waitKeys(keyList = [SpaceKey]) # press space to continue 

############
# PARAMETERS
############ 

#Initialise
Block = 0 # out of 4
Trialnr = 0
GetOut = 0  # Initialise exit
clock = core.Clock()  # Timer for reaction time
exp_clock = core.Clock()  # Global clock for experiment timestamp

# Define keyboard
SpaceKey = 'space'
EscapeKey = 'escape'
InKey = 'l'
OutKey = 'a'


# Make mouse invisible
win.mouseVisible = False

########################
# FIXATION and STIMULI
########################

# Create fixation cross
fixation = visual.TextStim(win, text='+', color=stimulus_color, height=fixation_size) 

# Create text stimulus
stimulus = visual.TextStim(win, text="", color=stimulus_color, height=stimulus_size)
probe = visual.TextStim(win, text="", color=stimulus_color, height=stimulus_size)
feedback = visual.TextStim(win, text="", color=stimulus_color, height=stimulus_size)
rest_text= visual.TextStim(win, text="", color=stimulus_color, height=rest_text_size)

# Set function to generate stimulus - returns letter-hash sequence and number of hashes in the stimulus
def generate_stimulus():
    consonants = ''.join([c for c in string.ascii_uppercase if c not in 'AEIOU']) # all uppercase consonants
    num_hashes = random.randint(0, 3) # number of hashes from 0-3 per stimulus
    num_consonants = 6 - num_hashes # number of consonants needed

    chars = random.sample(consonants, k=num_consonants) + ['#'] * num_hashes # Randomly select consonants WITHOUT replacement to avoid duplicate letters
    random.shuffle(chars) # randomise order of charachters
    
    stimulus_string = ''.join(chars)
    
    return stimulus_string, num_hashes

# Function to generate the probe, lowercase consonant letter 50% chance IN stimulus
def generate_probe(stimulus_string):
    stimulus_letters_upper = [c for c in stimulus_string if c.isalpha()] # uppercase letters in stimulus_string (from above function), ignoring # sign
    letters_in_stimulus = [c.lower() for c in stimulus_letters_upper] # lowercase letters in stimulus_string
    all_consonants = [c for c in string.ascii_lowercase if c not in 'aeiou'] # all consonants, lowercase
    letters_not_in_stimulus = [c for c in all_consonants if c not in letters_in_stimulus] # all consonants that are not in stimulus_string
    
    if random.random() < 0.5 and letters_in_stimulus:  # generate random float, 50-50 coin flip for choosing probe that is in letter string or out
        probe_string = random.choice(letters_in_stimulus) # probe is IN stimulus
        is_in = True
    else:
        probe_string = random.choice(letters_not_in_stimulus) # probe is NOT IN stimulus
        is_in = False
        
    return probe_string, is_in

############
# INSTRUCTIONS
############

# intro Weclome
#IntroImage = my_directory + "\\Intro.jpg"
#intro = visual.ImageStim(win, image = 'Intro.jpg', units='height', size=(1.0, 0.7), interpolate=True)
#intro.draw()
#win.flip() # present text 
#event.waitKeys(keyList=[SpaceKey]) # press space to continue 

# instructions 
InstructionsImage = Instructions_directory + "\\Sternberg_Instructions.jpg"
Instructions(win, InstructionsImage)

########################
#   PRACTICE TRIAL
########################

practice_trials_n = 6 # number of practice trials
feedback_duration = 2 # seconds shown feedback
# set random seed so each participant receives same practice trials
random.seed(123) 

for n in range(practice_trials_n):
    if GetOut == 1:     # Check for exit
        break
    
    # Set stimulus_string and probe
    stimulus_string, num_hashes = generate_stimulus()
    probe_string, is_in = generate_probe(stimulus_string)
    
    # Set stimulus and probe text
    stimulus.text = stimulus_string
    probe.text = probe_string
    
    # Fixation
    fixation.draw()
    win.flip()
    core.wait(fixation_duration)
    
    # Show Stimulus
    stimulus.draw()
    win.flip()
    core.wait(stimulus_duration)
    
    #retention period blank screen
    win.flip()
    core.wait(retention_duration)
    
    #draw probe
    probe.draw()
    
    # Initialise response variables
    resp = []
    resp_given = 0
    Acc = 0
    RT = None
    
    event.clearEvents() # Clear any previous responses
    
    #show probe
    win.flip()
    
    timestamp = exp_clock.getTime() # timestamp since start of experiment for eye tracker data syncing
    
    #Start response time
    start_rt = clock.getTime()
    temp_rt = clock.getTime()
    
    # Response collection 
    while temp_rt - start_rt < probe_duration:
        temp_rt = clock.getTime()
        if resp_given == 0:
            resp = event.getKeys(keyList = [InKey, OutKey, EscapeKey])
            
            if len(resp) > 0:
                resp = [resp[0]]    #only register first button press
                RT = temp_rt - start_rt
                resp_given = 1
                #timestamp = exp_clock.getTime()  # Get timestamp at response for responded trials - optional
                
    if len(resp)>0:
        if is_in: #if probe is in stimulus string
        # Correct response is "In" (InKey)
            if resp [0] == InKey:
                Acc = 1
            else:
                Acc = 0
        else: #if probe is NOT in stimulus string
        # Correct response is "Out" (OutKey)
            if resp[0] == OutKey:
                Acc = 1
            else:
                Acc = 0
        if resp [0] == EscapeKey:
            GetOut = 1
            break
            
    else: #No response = Incorrect!
            Acc = 0

    # Set feedback text
    if Acc == 1:
        feedback.text = 'Correct'
    else:
        feedback.text = 'Incorrect'

    # Display feedback
    feedback.draw()
    win.flip()
    core.wait(feedback_duration)  # Show feedback for 2 seconds

    # Exit if escape key was pressed
    if GetOut:
        break

######################## 
# PRACTICE OVER 

# reset random seed to ensure randomisation between participants from now on
random.seed(None)

# Tell participants that exercise is over and real experiment starts
InstructionsImage = Instructions_directory + "\\StartRealExperiment_Sternberg.jpg"
Instructions(win, InstructionsImage)

##########################
# START MAIN EXPERIMENT
##########################

# Reset experimental clock
exp_clock.reset()

# # Loop over blocks
# for block_index in range(n_blocks):  #4 blocks
#     if GetOut == 1:
#         break
    
#     Block += 1 # numbering blocks; Block initialised above at 0
    
    #Loop over trials per block
for n in range(n_trials):
    if GetOut == 1:     # Check for exit
        break
    
    # Set stimulus_string and probe
    stimulus_string, num_hashes = generate_stimulus()
    probe_string, is_in = generate_probe(stimulus_string)
    
    # Set stimulus and probe text
    stimulus.text = stimulus_string
    probe.text = probe_string
    
    # Fixation
    fixation.draw()
    win.flip()
    core.wait(fixation_duration)
    
    # Show Stimulus
    stimulus.draw()
    win.flip()
    core.wait(stimulus_duration)
    
    #retention period blank screen
    win.flip()
    core.wait(retention_duration)
    
    # draw probe
    probe.draw()
    
    # Initialise response variables
    resp = []
    resp_given = 0
    Acc = 0
    RT = None
    
    event.clearEvents() # Clear any previous responses
    
    # show probe
    win.flip()
    
    timestamp = exp_clock.getTime() # Get timestamp of time elapsed from beginning experiment at stimulus presentation
    
    #Start response time 
    start_rt = clock.getTime()
    temp_rt = clock.getTime()
    
    # Response collection 
    while temp_rt - start_rt < probe_duration:
        temp_rt = clock.getTime()
        if resp_given == 0:
            resp = event.getKeys(keyList = [InKey, OutKey, EscapeKey])
            
            if len(resp) > 0:
                resp = [resp[0]]
                RT = temp_rt - start_rt
                resp_given = 1
                
    if len(resp)>0:
        if is_in:
        # Correct response is "In" (InKey)
            if resp [0] == InKey:
                Acc = 1
            else:
                Acc = 0
        else:
        # Correct response is "Out" (OutKey)
            if resp[0] == OutKey:
                Acc = 1
            else:
                Acc = 0
                
        if resp [0] == EscapeKey:
            GetOut = 1
            break
            
    else: #No response = Incorrect!
            Acc = 0
            
    Trialnr += 1 # increment trial count
    
    if n < 40:
        Block = 1
    elif (n > 39) and (n < 80):
        Block = 2
    elif (n > 79) and (n < 120):
        Block = 3
    elif (n > 119):
        Block = 4
        
# Store trial info
    ThisExp.addData('Trial', Trialnr)
    ThisExp.addData('Block', Block)
    ThisExp.addData('Stimulus', stimulus_string)
    ThisExp.addData('Probe', probe_string)
    ThisExp.addData('Is_In', is_in)
    ThisExp.addData('Response', resp if resp else None)
    ThisExp.addData('RT', RT)
    ThisExp.addData('Accuracy', Acc)
    ThisExp.addData('Timestamp', timestamp)
    ThisExp.addData('Hash_Num', num_hashes )
    ThisExp.nextEntry()
    
# Exit if escape key was pressed
    if GetOut == 1:
        break
    
    if (n == 39) or (n == 79) or (n == 119):
        InstructionsImage = Instructions_directory + "\\Break.jpg"
        Instructions(win, InstructionsImage)
    
    # Display rest screen after each block (except the last one)
    # if Block < 3:  # Only show rest screen after the first 3 blocks
        
    #     rest_clock = core.Clock()
        
        # while rest_clock.getTime() < rest_period:
        #     # Check for escape key press during the rest period
        #     if EscapeKey in event.getKeys():
        #         GetOut = 1
        #         break
        #     # Continue waiting and display count down
        #     remaining_time = rest_period - rest_clock.getTime()
        #     if remaining_time > 0:
        #         # Count down
        #         rest_text.text = f'Break.\nThe experiment will resume in {int(remaining_time)} seconds.'
        #         rest_text.draw()
        #         win.flip()
        #         core.wait(0.1)  # Update count down 100 ms
                
        # if GetOut == 1:
        #     break

# SAVE and END
ThisExp.saveAsWideText(filename, delim =',')

# outro
InstructionsImage = Instructions_directory + "\\EndExperiment.jpg"
Instructions(win, InstructionsImage)

# End of experiment
win.close()
core.quit()