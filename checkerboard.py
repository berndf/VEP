#!/usr/bin/env python3

import sys

if len(sys.argv)>1:
 subject=sys.argv[1]
else:
 subject='test'

start_tests_at=0
# Default is Normann stimulation
variant='default'
if len(sys.argv)>2:
 if sys.argv[2] in [
  'default',
  'demo',
  'ceiling',
  'pulse',
  'theta',
  'Kirk',
  'Mixed11',
  'Mixed21',
  'Mixed12',
  'Mixed22',
  'NormannOhne',
  'KirkOhne',
  'Kirk10min2Hz',
 ]:
  variant=sys.argv[2]
 else:
  # Allow tests to be restarted at test x (counting from 1)
  start_tests_at=int(sys.argv[2])

stimtype='checkerboard'
if len(sys.argv)>3:
 stimtype=sys.argv[3]

import CB
import expyriment
from expyriment.misc import constants

# In Michael Bach's setup, the checker fields are 8mm on screen, fixation cross is diagonal
# in a constantly displayed 11mm wide circle, in which also the numbers appear on a white
# background every once in a while
# With a viewing distance of 114cm this corresponds to 0.4° visual angle for the checkers.
# On the large screen, the patchsize=30 resulted in 1.9cm checkers, with a viewing distance
# of 171cm and a targeted angle of 0.5° they should be 1.5cm -> patchsize 23
# The large screen is an LG OLED55CX9LA ie 55''=139cm diagonal, 122x73cm screen width x height
# Total visual angle from 171cm is atan(122/2/171)*2/pi*180=39.26 degrees
if stimtype=='checkerboard':
 testname='Checkerboard'
elif stimtype.startswith('grating_'):
 testname='Grating'
else:
 print("Error: Unknown stimulus tyle >%s<!" % stimtype)
 exit()
cb=CB.CB(subject,test=testname,experiment=testname,testmode=False)
allstimuli=[
 CB.Checkerboard(78,46,patchsize=24,background_colour=constants.C_BLACK,foreground_colour=constants.C_WHITE),
 CB.Checkerboard(78,46,patchsize=24,phase=1,background_colour=constants.C_BLACK,foreground_colour=constants.C_WHITE),
 # Stimulation following Sumner:2020, temporal parameters see below
 CB.SineGrating(cb.exp.screen.size[0],cb.exp.screen.size[1],40,direction='vertical',background_colour=expyriment.misc.constants.C_DARKGREY,foreground_colour=expyriment.misc.constants.C_WHITE),
 CB.SineGrating(cb.exp.screen.size[0],cb.exp.screen.size[1],40,direction='horizontal',background_colour=expyriment.misc.constants.C_DARKGREY,foreground_colour=expyriment.misc.constants.C_WHITE),
]
for stimulus in allstimuli:
 cb.fixcross.plot(stimulus)
 stimulus.preload()
targets=[
 expyriment.stimuli.TextLine(str(number),text_size=30,text_colour=expyriment.misc.constants.C_BLACK,background_colour=expyriment.misc.constants.C_WHITE)
 for number in range(10)
]
mask=cb.fixcross
for stimulus in targets:
 stimulus.preload()
mask.preload()

cb.init_queue()

def cb_block(duration_s=20,rps=2,usestim=allstimuli[:2]):
 qc=CB.queue_checkers(cb,stimuli=usestim,cycles=duration_s*rps/2,interval=1.0/rps)
 qc.start()
 cb.run()
 qc.stop()
 qc.join()

def default_modulation():
 # Note that after Normann:2007 19 rps was also used for the 10 min modulation
 # but not as effective as 2 rps
 cb_block(duration_s=60*10)

# Stimulation following Sumner:2020
# Probes: both stimuli were presented in a random order
# 120 times (ie, 60 times each) at 1 Hz for 34.8 ms. The interstimulus interval was
# varied using 5 intervals from 897 to 1036 ms that occurred
# randomly but equally often.
# Here: Shortened to 40s as in Checkerboard
def grating_probe(n_per_type=20):
 import random
 ISIs=[(897+x*(1036-897)/4) for x in range(5)]*int(n_per_type/5)
 stimno_and_ISIs=list(zip([0]*n_per_type+[1]*n_per_type,ISIs*2))
 random.shuffle(stimno_and_ISIs)
 qc=CB.queue_grating(cb,stimno_and_ISIs=stimno_and_ISIs,stimuli=allstimuli[2:4],mask=cb.fixcross)
 qc.start()
 cb.run()
 qc.stop()
 qc.join()

# Tetanus: 2-minute high-frequency stimulation comprising 1000
# presentations of either the horizontal or vertical stimulus to test
# input specificity (counterbalanced between participants) for 34.8 ms
# with a temporal frequency of approximately 9 Hz. The interstimulus interval was either
# 62.6 or 90.4 ms occurring at random but equally often.
# This is used unmodified (111.3s) in Kirk, Mixed1 and Mixed2
def grating_modulation_Sumner1(n_stim=1000,stimno=0):
 import random
 ISIs=[62.6,90.4]*int(n_stim/2)
 stimno_and_ISIs=list(zip([stimno]*n_stim,ISIs))
 random.shuffle(stimno_and_ISIs)
 qc=CB.queue_grating(
  cb,
  stimno_and_ISIs=stimno_and_ISIs,stimuli=allstimuli[2:4],
  mask=cb.fixcross)
 qc.start()
 cb.run()
 qc.stop()
 qc.join()
def grating_modulation_Sumner(n_stim=1000):
 stimno=0 if stimtype=='grating_vertical' else 1
 grating_modulation_Sumner1(n_stim,stimno)
def grating_modulation_Sumner_inverted(n_stim=1000):
 stimno=1 if stimtype=='grating_vertical' else 0
 grating_modulation_Sumner1(n_stim,stimno)

# This is just as for checkerboard: 10min 2Hz, but a bit jittered
def grating_modulation_Normann1(n_stim=1200,stimno=0):
 import random
 ISIs=[(465.2+x*(534.8-465.2)/2-34.8) for x in range(3)]*int(n_stim/3)
 stimno_and_ISIs=list(zip([stimno]*n_stim,ISIs))
 random.shuffle(stimno_and_ISIs)
 qc=CB.queue_grating(
  cb,
  stimno_and_ISIs=stimno_and_ISIs,stimuli=allstimuli[2:4],
  mask=cb.fixcross)
 qc.start()
 cb.run()
 qc.stop()
 qc.join()
def grating_modulation_Normann(n_stim=1200):
 stimno=0 if stimtype=='grating_vertical' else 1
 grating_modulation_Normann1(n_stim,stimno)
def grating_modulation_Normann_inverted(n_stim=1200):
 stimno=1 if stimtype=='grating_vertical' else 0
 grating_modulation_Normann1(n_stim,stimno)

def cb_wait(duration_s=10):
 qw=CB.queue_wait(cb, duration_s)
 qw.start()
 cb.run()
 qw.stop()
 qw.join()

def pulse_modulation():
 # Pulse protocol with 9 rps and four pulses of 135s each, with 20s cb_wait() in between
 for i in range(4):
  cb_block(duration_s=135, rps=9)
  if cb.quit_requested:
   break
  if i < 3:  # Only add cb_wait() after the first three blocks
   cb_wait(duration_s=20) # 20 seconds wait
   if cb.quit_requested:
    break

def theta_modulation():
 # Theta modulation protocol: 22 blocks each lasting 18 seconds with 10 seconds of cb_wait() in between
 for i in range(22):
  for j in range(5):  # 9 cycles of 2s stimulation and 2s wait to make up 18s
   cb_block(duration_s=2, rps=5)
   if cb.quit_requested:
    break
   cb_wait(duration_s=2)
  if cb.quit_requested:
   break
  cb_wait(duration_s=8)
  if cb.quit_requested:
   break


if variant=='demo':
 # Start the target thread
 qt=CB.queue_targets(cb,targets=targets,mask=mask,duration=0.3,min_s=3,max_s=8)
 qt.start()
 cb_wait()
 if cb.quit_requested:
  exit()
 if testname=='Checkerboard':
  cb_block(duration_s=10)
 else:
  grating_probe(n_per_type=10)
  grating_modulation_Sumner(n_stim=100)
 if cb.quit_requested:
  exit()
 cb_wait()
 exit()

if variant=='ceiling':
 modulation_at=[2,14,26]
else:
 modulation_at=[2]
if testname=='Checkerboard':
 probe=cb_block
 if variant=='pulse':
  modulation=pulse_modulation
 elif variant=='theta':
  modulation=theta_modulation
 elif variant=='NormannOhne':
  # No modulation, checkerboard probes, duration 10min as Normann modulation
  def modulation():
   cb_wait(duration_s=600)
 else:
  modulation=default_modulation
else:
 # Grating
 probe=cb_block if variant.startswith('Mixed1') else grating_probe
 if variant=='default' or variant=='Kirk10min2Hz':
  modulation=grating_modulation_Normann
 elif variant=='Kirk':
  modulation=grating_modulation_Sumner
 elif variant=='KirkOhne':
  # No modulation, Kirk probes, duration 2min as Sumner modulation
  def modulation():
   cb_wait(duration_s=120)

all_test_at_min_post_modulation=[2,8,12,18,22,28]
if start_tests_at==0:
 test_at_min_post_modulation=all_test_at_min_post_modulation
else:
 first_start=all_test_at_min_post_modulation[start_tests_at-1]
 test_at_min_post_modulation=[x-first_start for x in all_test_at_min_post_modulation[(start_tests_at-1):]]
 test_at_min_post_modulation[0]=0.1 # Allow 6 seconds at start

cb.common_start(testname)

# Start the target thread
qt=CB.queue_targets(cb,targets=targets,mask=mask,duration=0.3,min_s=3,max_s=8,code_offset=len(allstimuli))
qt.start()

def clean_exit():
 qt.stop()
 qt.join()
 exit()


# ------- Here the actual presentation starts! ---------
# Skip modulation if only tests need to be repeated
if start_tests_at==0:
 cb_wait()
 if cb.quit_requested:
  clean_exit()
 # Present first test and modulation
 cb.set_starttime()
 probe()
 if cb.quit_requested:
  clean_exit()
 if variant in ['Mixed11','Mixed21']:
  cb.do_at(2,cb_wait,grating_modulation_Sumner,clean_exit)
  cb.do_at(4,cb_wait,grating_modulation_Normann_inverted,clean_exit)
 elif variant in ['Mixed12','Mixed22']:
  cb.do_at(2,cb_wait,grating_modulation_Normann,clean_exit)
  cb.do_at(12.333333,cb_wait,grating_modulation_Sumner_inverted,clean_exit)
 else:
  for min_post_start in modulation_at:
   cb.do_at(min_post_start,cb_wait,modulation,clean_exit)

# New time zero for tests
cb.set_starttime()

for min_post_modulation in test_at_min_post_modulation:
 cb.do_at(min_post_modulation,cb_wait,probe,clean_exit)

clean_exit()
