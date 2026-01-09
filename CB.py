#!/usr/bin/env python3

# vim: set fileencoding=utf-8 :
# Checkerboard stimulus

marker_duration_ms=20

import expyriment
import time

class CB(object):
 def __init__(self,subject='Test',test='CB',experiment="Checkerboard",testmode=False):
  self.testmode=testmode
  self.quit_requested=False
  # This is for concurrent presentations through threads
  self.queue=None

  import os
  if os.sys.platform.startswith('win'):
   import sys
   sys.path.append(os.path.dirname(__file__))
   parport=0xE010
  else:
   parport="/dev/parport0"

  #expyriment.control.set_develop_mode(True)
  #expyriment.control.defaults.event_logging=0
  # Create and initialize an Experiment
  expyriment.control.defaults.window_mode = False
  expyriment.control.defaults.initialise_delay=0
  expyriment.control.defaults.opengl=0
  expyriment.design.defaults.experiment_background_colour=expyriment.misc.constants.C_DARKGREY
  expyriment.design.defaults.experiment_foreground_colour=expyriment.misc.constants.C_WHITE
  expyriment.io.defaults.textinput_user_text_colour=expyriment.misc.constants.C_BLACK
  self.exp = expyriment.design.Experiment(experiment+' - '+test)
  expyriment.control.initialize(self.exp)
  self.fixcross=expyriment.stimuli.Circle(20,colour=expyriment.misc.constants.C_GREY)
  x=expyriment.stimuli.FixCross(size=(26,26),line_width=4,colour=expyriment.misc.constants.C_WHITE)
  x.rotate(45)
  x.plot(self.fixcross)
  if self.testmode:
   self.abstime_s=0
   self.set_starttime()
   return

  expyriment.control.start(subject_id=1,skip_ready_screen=True)
  self.set_eventfile(subject,test)

  try:
   pport=expyriment.io.ParallelPort(parport)
  except (RuntimeError,ImportError): # RuntimeError on Linux, ImportError on Windows
   pport=None
  if pport:
   self.marker=expyriment.io.MarkerOutput(pport, default_duration=marker_duration_ms)
  else:
   self.marker=None
   print("WARNING: Device %s not present, no marker will be sent!" % parport)

  self.set_starttime()
 def set_starttime(self):
  if self.testmode:
   self.starttime_s=self.abstime_s
   print("Starttime set at %g" % self.abstime_s)
  else:
   self.starttime=time.time()
 def sleep(self,interval):
  if not self.testmode:
   # Avoid crash with negative intervals
   if interval>0:
    time.sleep(interval)
 def do_at(self, minutes, waitfun, which, clean_exit):
  # Wait until x minutes after starttime (waitfun takes wait time in seconds)
  if self.testmode:
   difftime=minutes*60-(self.abstime_s-self.starttime_s)
   print("do_at %gmin at %gs (relative %gs, %gmin) waiting for %gs" % (minutes,self.abstime_s,self.abstime_s-self.starttime_s,(self.abstime_s-self.starttime_s)/60,difftime))
   self.abstime_s+=difftime
   which()
   return
  waitfun(minutes*60-(time.time()-self.starttime))
  if self.quit_requested:
   clean_exit()
  which()
  if self.quit_requested:
   clean_exit()
 def common_start(self, name):
  '''Convenience to show message and fixcross and wait for mouse press'''
  if self.testmode:
   return
  self.exp.screen.clear()
  self.exp.keyboard.clear()
  self.exp.mouse.clear()
  text=expyriment.stimuli.TextBox("Nächster Teil: %s\n\nZum Start Maustaste drücken" % name,size=(self.exp.screen.size[0]*0.75,self.exp.screen.size[1]*0.2),position=(0,self.exp.screen.size[1]*0.05),text_size=40,text_colour=expyriment.misc.constants.C_WHITE)
  text.present()
  self.exp.mouse.wait_press(process_control_events=False)
  self.exp.screen.clear()
  self.exp.screen.update()
  self.fixcross.present()
 def clear_events(self):
  self.quit_requested=False
  self.exp.mouse.clear()
  self.exp.keyboard.clear()
 def set_eventfile(self,subject,test):
  import os
  tmstamp=self.exp.events.filename.split('.')[0].split('_')[-1]
  # tmstamp is only exact to the minute, so it is possible that a collision
  # occurs, which causes an abort. So we first check:
  i=0
  evtname=''
  while True:
   evtname='%s_%s_%s_%02d' % (subject,test,tmstamp,i)
   if not os.path.exists(os.path.join(self.exp.events.directory,evtname+'.xpe')):
    break
   i+=1
  self.exp.events.rename(evtname+'.xpe')
  self.exp.data.rename(evtname+'.xpd')

 def marker_send(self,code):
  '''Convenience so that we don't have to check for marker in all applications'''
  if self.marker:
   self.marker.send(code)
 def __del__(self):
  expyriment.control.end(fast_quit=True)
 def init_queue(self):
  # The queue class is thread safe
  import queue
  self.queue=queue.Queue()
 def waitfn(self):
  # check_for_control_keys calls sys.exit() which we cannot use at all!
  # This should be registered and unregistered by the paradigm like so:
  #expyriment.control.register_wait_callback_function(lambda: self.expy.waitfn(),self.expy.exp)
  #expyriment.control.unregister_wait_callback_function(self.expy.exp)
  key=self.exp.keyboard.check(check_for_control_keys=False)
  if key is not None and key==self.exp.keyboard.get_quit_key():
   self.quit_requested=True
 def run(self):
  if self.queue is None:
   print("self.queue must be initialized to receive stimuli!")
   return
  # This is run until stimulus is None or quit was requested
  if self.testmode:
   while True:
    stimulus,code,clear,duration=self.queue.get(block=True)
    if stimulus is None:
     break
    print("Stimulus at %gs (relative %gs, %gmin) code %d" % (self.abstime_s,self.abstime_s-self.starttime_s,(self.abstime_s-self.starttime_s)/60,code))
    self.abstime_s+=duration
   return
  while True:
   stimulus,code,clear,duration=self.queue.get(block=True)
   self.waitfn()
   #print(stimulus,code,clear)
   if stimulus is None or self.quit_requested:
    break
   if not type(stimulus) is expyriment.stimuli._audio.Audio:
    stimulus.present(clear=clear,update=True)
    if not clear:
     # Second and third time because of triple buffering
     stimulus.present(clear=clear,update=True)
     stimulus.present(clear=clear,update=True)
   else:
    # expyriment.stimuli._audio.Audio
    stimulus.present()
   if code:
    self.marker_send(code)
  # Clear the screen at the end
  self.exp.screen.clear()
  self.exp.screen.update()
  self.exp.screen.clear()
  self.exp.screen.update()


import numpy
from expyriment.stimuli._canvas import Canvas

class Checkerboard(Canvas):
 def __init__(self, nx, ny, phase=0, patchsize=100, position=None,
              background_colour=(0, 0, 0),
              foreground_colour=(255, 255, 255)):
  # Assumes even n
  o0=(numpy.ones(patchsize)*numpy.array(background_colour,ndmin=2).T).T
  o1=(numpy.ones(patchsize)*numpy.array(foreground_colour,ndmin=2).T).T
  final = []
  for i in range(nx):
   oneline=numpy.tile(numpy.append(o0,o1,axis=0) if (i+phase)%2==0 else numpy.append(o1,o0,axis=0),(int(ny/2),1))
   final.extend([oneline]*patchsize)
  self._pixel_array = numpy.array(final)
  Canvas.__init__(self, size=self._pixel_array.shape[:2], position=position, colour=background_colour)
  self._background_colour = background_colour
  self._foreground_colour = foreground_colour

 @property
 def background_colour(self):
  """Getter for background_colour"""
  return self._background_colour

 @property
 def pixel_array(self):
  """Getter for pixel_array"""
  return self._pixel_array

 def _create_surface(self):
  """Get the surface of the stimulus.
  This method has to be overwritten for all subclasses individually!
  """
  self.set_surface(self._pixel_array)
  return self._surface

class SineGrating(Canvas):
 '''
 Patterned after https://github.com/RachaelSumner/VisualLTP
 degrees: visual angle stimuli will span
 '''
 def __init__(self, pixels_width, pixels_height, screen_width_degrees,
              direction='vertical', degrees=8, num_cycles=8,
              position=None,
              background_colour=expyriment.misc.constants.C_DARKGREY,
              foreground_colour=expyriment.misc.constants.C_WHITE):
  pixels_per_degree = pixels_width/screen_width_degrees
  dia = numpy.floor(pixels_per_degree*degrees) - 1
  radius = dia / 2

  x = numpy.arange(dia)
  gratingImage=(numpy.sin(((x*2*numpy.pi*num_cycles)/dia)+numpy.pi/2)+1)*0.5
  gratingImage=gratingImage.reshape(gratingImage.shape[0],1).repeat(dia,1)
  gratingImage=numpy.expand_dims(gratingImage,2).dot(numpy.array(foreground_colour.rgb,ndmin=2))

  #Cut grating into a circle
  for y in numpy.arange(dia):
   ycentred = y - radius
   x = numpy.sqrt(radius * radius - ycentred * ycentred)
   gratingImage[int(y), 0:int(numpy.floor(radius-x))]=background_colour.rgb
   gratingImage[int(y), int(numpy.floor(radius+x+1)):int(dia)]=background_colour.rgb

  if direction!='vertical':
   gratingImage=gratingImage.transpose(1,0,2)

  self._pixel_array = gratingImage
  Canvas.__init__(self, size=self._pixel_array.shape[:2], position=position, colour=background_colour)
  self._background_colour = background_colour
  self._foreground_colour = foreground_colour

 @property
 def background_colour(self):
  """Getter for background_colour"""
  return self._background_colour

 @property
 def pixel_array(self):
  """Getter for pixel_array"""
  return self._pixel_array

 def _create_surface(self):
  """Get the surface of the stimulus.
  This method has to be overwritten for all subclasses individually!
  """
  self.set_surface(self._pixel_array)
  return self._surface


import threading
class queue_checkers(threading.Thread):
 def __init__(self, cb, stimuli, cycles, interval=1.0, code_offset=0):
  super().__init__()
  self.cb=cb
  self.stimuli=stimuli
  self.cycles=round(cycles)
  self.interval=interval
  self.code_offset=code_offset
  self.daemon=True
  self.done=False
 def run(self):
  for rep in range(self.cycles):
   for code,stimulus in enumerate(self.stimuli):
    if self.done:
     return
    self.cb.queue.put((stimulus,code+1+self.code_offset,True,self.interval))
    #print("queue_checkers: Putting %d" % (code+1))
    self.cb.sleep(self.interval)
  self.cb.queue.put((None,0,False,0))
 def stop(self):
  self.done=True

class queue_grating(threading.Thread):
 def __init__(self, cb, stimno_and_ISIs, stimuli, mask, code_offset=2):
  super().__init__()
  self.cb=cb
  self.stimuli=stimuli
  self.stimno_and_ISIs=stimno_and_ISIs
  self.mask=mask
  self.code_offset=code_offset
  self.daemon=True
  self.done=False
 def run(self):
  for code,ISI in self.stimno_and_ISIs:
   self.cb.queue.put((self.stimuli[code],code+1+self.code_offset,True,34.8/1000))
   self.cb.sleep(34.8/1000)
   self.cb.queue.put((self.mask,0,True,ISI/1000))
   if self.done:
    return
   self.cb.sleep(ISI/1000)
  self.cb.queue.put((None,0,False,0))
 def stop(self):
  self.done=True

class queue_targets(threading.Thread):
 def __init__(self, cb, targets, mask, duration, min_s, max_s, code_offset=2):
  super().__init__()
  self.cb=cb
  self.targets=targets
  self.mask=mask
  self.duration=duration
  self.min_s=min_s
  self.max_s=max_s
  self.code_offset=code_offset
  self.daemon=True
  self.done=False
 def run(self):
  if self.cb.testmode:
   # Do not debug times of this thread as only a single thread can be counted in testmode!
   while not self.done:
    time.sleep(1)
   return

  import random
  # Don't start off with a target but wait
  self.cb.sleep(self.min_s+random.random()*(self.max_s-self.min_s)-self.duration)
  while not self.done:
   code=random.randint(0,len(self.targets)-1)
   self.cb.queue.put((self.targets[code],code+1+self.code_offset,False,self.duration))
   #print("queue_targets: Putting %d" % code)
   self.cb.sleep(self.duration)
   sleepdur=self.min_s+random.random()*(self.max_s-self.min_s)-self.duration
   self.cb.queue.put((self.mask,0,False,sleepdur))
   #print("queue_targets: Putting mask")
   self.cb.sleep(sleepdur)
 def stop(self):
  self.done=True

class queue_wait(threading.Thread):
 def __init__(self, cb, wait_s):
  super().__init__()
  self.cb=cb
  self.wait_s=wait_s
  self.daemon=True
  self.done=False
 def run(self):
  self.cb.queue.put((self.cb.fixcross,0,True,self.wait_s))
  self.cb.sleep(self.wait_s)
  self.cb.queue.put((None,0,False,0))
 def stop(self):
  self.done=True


if __name__ == "__main__":
 import CB

 subject='test'
 cb=CB.CB(subject,test='Checkerboard',experiment='Checkerboard')
 # This list contains all stimuli
 # The second element in each tuple determines whether the screen is cleared when displaying.
 stimuli=[
  CB.SineGrating(cb.exp.screen.size[0],cb.exp.screen.size[1],20,background_colour=expyriment.misc.constants.C_DARKGREY,foreground_colour=expyriment.misc.constants.C_WHITE),
  CB.SineGrating(cb.exp.screen.size[0],cb.exp.screen.size[1],20,direction='horizontal',background_colour=expyriment.misc.constants.C_DARKGREY,foreground_colour=expyriment.misc.constants.C_WHITE),
  #CB.Checkerboard(32,16,patchsize=50,background_colour=expyriment.misc.constants.C_BLACK,foreground_colour=expyriment.misc.constants.C_WHITE),
  #CB.Checkerboard(32,16,patchsize=50,phase=1,background_colour=expyriment.misc.constants.C_BLACK,foreground_colour=expyriment.misc.constants.C_WHITE),
 ]
 for stimulus in stimuli:
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
 #cb.common_start('Checkerboard')

 cb.init_queue()
 qc=CB.queue_checkers(cb,stimuli=stimuli,cycles=20,interval=0.5)
 qc.start()

 qt=CB.queue_targets(cb,targets=targets,mask=mask,duration=0.3,min_s=3,max_s=8,code_offset=len(stimuli))
 qt.start()

 cb.run()
 qc.stop()
 qc.join()
 if cb.quit_requested:
  qt.stop()
  qt.join()
  exit()

 qw=CB.queue_wait(cb, 10)
 qw.start()
 cb.run()

 qw.stop()
 qw.join()
 qt.stop()
 qt.join()
