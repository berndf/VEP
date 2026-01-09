#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :

import os
import math
import json
import pickle
import datetime
import subprocess

# Persistent memory of modules already executed.
# It contains a single dict with key ID and value dict with the executed
# modules
memory_file='memory.pickle'
# Number of horizontal start button boxes to hold the start buttons
n_StartBoxes=1
Randomization_file='Randomization.json'
# cd to the main directory
os.chdir(os.path.join(os.path.dirname(__file__)))

if os.path.exists(Randomization_file):
 with open(Randomization_file,'rb') as msgp:
  Randomization=json.load(msgp)
else:
 print("WARNING: No randomization loaded!")
 Randomization={}

if os.sys.platform=='linux':
 # Control audio settings
 # First control gnome/pulseaudio main volume
 os.system('pactl set-sink-mute 0 0')
 os.system('pactl set-sink-volume 0 100%')
 # Then set hardware card volume
 import alsaaudio
 ci=dict(zip(alsaaudio.cards(),alsaaudio.card_indexes()))
 #print(ci)
 #print(alsaaudio.mixers(cardindex=ci['SoundBar']))
 card=ci.get('SoundBar',0)
 mixer=alsaaudio.Mixer(cardindex=card,control='PCM')
 mixer.setvolume(50)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk

css_data=b'''
.css_normal {
    font-weight: bold;
    font-size: 30pt;
    padding: 0 10px 0 10px;
}
.css_green {
    background-color: green;
    background: green;
    color: white;
    border-color: white;
    font-weight: bold;
    font-size: 30pt;
    padding: 0 10px 0 10px;
}
.css_green:hover {
    background-color: green;
    background: green;
    color: red;
    border-color: white;
    font-weight: bold;
    font-size: 30pt;
    padding: 0 10px 0 10px;
}
.css_greyedout {
    background-color: grey;
    background: grey;
    color: grey;
    font-weight: bold;
    font-size: 30pt;
    padding: 0 10px 0 10px;
}
.css_orange {
    background-color: orange;
    background: orange;
    color: white;
    font-weight: bold;
    font-size: 30pt;
    padding: 0 10px 0 10px;
}
.css_red {
    background-color: red;
    background: red;
    color: white;
    border-color: white;
    font-weight: bold;
    font-size: 30pt;
    padding: 0 10px 0 10px;
}
'''

def good_subject_name(ID):
 is_good=False
 if ID.startswith('test'):
  is_good=True
 elif len(ID)==4:
  # [KP]\d\d\d
  is_good=ID[0]=='K' and \
  ID[1].isdigit() and ID[2].isdigit() and ID[3].isdigit()
 return is_good

def get_sex_age_permutation(ID):
 if ID=='test':
  Rand_Params=['W','1',['default', 'Kirk'],'vertical']
 elif ID.startswith('K2'):
  Rand_Params=Randomization.get(ID,['','',['', '', '']])
 else:
  Rand_Params=Randomization.get(ID,['','',['', ''],''])
 return Rand_Params

class SelectionWindow(Gtk.Window):
 def __init__(self, parent=None):
  self.memory={}
  if os.path.exists(memory_file):
   with open(memory_file,'rb') as mf:
    p=pickle.Unpickler(mf)
    self.memory=p.load()
  else:
   self.memory={}

  # Used to store the currently running program (in the background)
  self.command=None

  Gtk.Window.__init__(self)
  try:
      self.set_screen(parent.get_screen())
  except AttributeError:
      self.connect('destroy', self.my_quit)

  style_provider = Gtk.CssProvider()
  style_provider.load_from_data(css_data)
  Gtk.StyleContext.add_provider_for_screen(
   Gdk.Screen.get_default(),
   style_provider,
   Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
  )

  self.set_title("OptiVEP Study")
  self.set_default_size(600, 600)

  self.box=Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
  self.add(self.box)

  self.SubjectEntryBoxFrame=Gtk.Frame(label="VP Code")
  self.box.attach(self.SubjectEntryBoxFrame,0,0,2,1) # col row width height
  self.SubjectEntryBox=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
  self.SubjectEntryBoxFrame.add(self.SubjectEntryBox)

  self.SubjectEntry=Gtk.Entry()
  self.SubjectEntryBox.pack_start(self.SubjectEntry,True,True,0)
  self.SubjectEntry.get_style_context().add_class("css_red")
  self.SubjectEntry.connect("changed", self.entry_set_appearance)

  # Prepare n_StartBoxes horizontal boxes to hold the start buttons
  self.StartBoxes=[]
  for i in range(n_StartBoxes):
   startbox=Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
   startbox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
   startbox.set_homogeneous(True)
   startbox.set_spacing(1)
   self.box.add(startbox)
   self.StartBoxes.append(startbox)

  # Initialize empty dicts to hold the StartButtons and signals
  self.StartButtons={}
  self.SignalConnected={}

  randbox=Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
  self.box.add(randbox)
  self.Randomization_Label=Gtk.Label()
  self.Randomization_Label.get_style_context().add_class("css_normal")
  randbox.add(self.Randomization_Label)
  self.TestMode=Gtk.CheckButton(label="TestMode")
  self.TestMode.set_active(False)
  randbox.add(self.TestMode)

  testbox=Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
  self.box.add(testbox)

  teststartbox=Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
  teststartbox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
  teststartbox.set_homogeneous(False)
  testbox.attach(teststartbox,1,0,1,1)

  self.move(500,200)
  self.show_all()
 def add_startbutton(self,part):
  StartButton=Gtk.Button(label=part)
  StartButton.get_style_context().add_class("css_normal")
  buttons_per_box=math.ceil(self.n_buttons/n_StartBoxes)
  self.StartBoxes[int(len(self.StartButtons)/buttons_per_box)].add(StartButton)
  # Make the buttons accessible from a callback
  self.StartButtons[part]=StartButton
  self.SignalConnected[part]=StartButton.connect("button-press-event",self.start_Start)
 def add_startbuttons(self,ID):
  # In OptiVEP (K1*) we have 2 randomized conditions plus T2 with double modulation added
  # after the fact
  parts=['Demo']+[('T%d' % i) for i in range(3)]
  self.n_buttons=len(parts)
  for part in parts:
   self.add_startbutton(part)

  ClearButton=Gtk.Button(label='C')
  ClearButton.get_style_context().add_class("css_normal")
  self.box.attach(ClearButton,1,1,1,n_StartBoxes)
  # Make ClearButton accessible from a callback
  self.StartButtons['C']=ClearButton
  self.SignalConnected['C']=ClearButton.connect("button-press-event",self.ClearMemory)
  self.show_all()
 def remove_startbuttons(self,ID):
  for part in self.StartButtons.keys():
   if self.SignalConnected.get(part) is not None:
    self.StartButtons[part].disconnect(self.SignalConnected[part])
   self.StartButtons[part].destroy()
  self.StartButtons={}
  self.SignalConnected={}
 def update_startbuttons(self,ID):
  for part in self.StartButtons.keys():
   StartButton=self.StartButtons[part]
   c=StartButton.get_style_context()
   if part=='C':
    # Handle the 'Clear' button
    if ID in self.memory and len(self.memory[ID])>0:
     c.remove_class('css_normal')
     c.add_class('css_red')
    else:
     c.remove_class('css_red')
     c.add_class('css_normal')
   else:
    if ID in self.memory and part in self.memory[ID]:
     c.remove_class('css_green')
     c.add_class('css_normal')
    else:
     c.remove_class('css_normal')
     c.add_class('css_green')
 def entry_set_appearance(self,*w):
  c=w[0].get_style_context()
  ID=w[0].get_text()
  if good_subject_name(ID):
   c.remove_class('css_red')
   c.add_class('css_normal')
   condition=get_sex_age_permutation(ID)
   self.Randomization_Label.set_label(' '.join((str(x) for x in condition)))
   self.add_startbuttons(ID)
   self.update_startbuttons(ID)
  else:
   c.remove_class('css_normal')
   c.add_class('css_red')
   self.Randomization_Label.set_label('')
   self.remove_startbuttons(ID)
 def ReallyClearMemory(self, widget, response):
  widget.destroy()
  if response==Gtk.ResponseType.OK:
   subject=self.SubjectEntry.get_text()
   self.memory[subject]={}
   self.update_startbuttons(subject)
 def ClearMemory(self, widget, response):
  subject=self.SubjectEntry.get_text()
  if not good_subject_name(subject) or subject not in self.memory or len(self.memory[subject])==0: return
  dialog=Gtk.MessageDialog(parent=self,message_type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK_CANCEL)
  # https://developer.gnome.org/pango/stable/PangoMarkupFormat.html
  dialog.set_markup('''
<big>Wollen Sie den Speicher wirklich löschen?</big>

Auch graue Boxen können wieder angeklickt werden, die Farbe dient nur
zur Rückmeldung und wir speichern damit, wann welches Paradigma lief.
Diese Information soll in der Regel erhalten bleiben.

Also: Information für diese Person wirklich löschen?
''')
  dialog.connect("response",self.ReallyClearMemory)
  dialog.show()
 def my_quit(self,*w):
  with open(memory_file,'wb') as mf:
   p=pickle.Pickler(mf)
   p.dump(self.memory)
  Gtk.main_quit(w)

 def start_command(self, call):
  if self.command is not None and self.command.poll() is None:
   # Process is still alife
   print("Refusing start, process is running!")
   return
  self.command=subprocess.Popen(call, shell=False)
 def start_Start(self, widget, response):
  subject=self.SubjectEntry.get_text()
  if not good_subject_name(subject): return
  part=widget.get_label()
  if subject.startswith('K1'):
   sex,age,permutation,grating=get_sex_age_permutation(subject)
   variant='demo' if part=='Demo' else 'Mixed22' if part=='T2' else permutation[int(part[1])]
  elif subject=='test' or subject.startswith('K3'):
   sex,age,permutation,grating=get_sex_age_permutation(subject)
   variant='demo' if part=='Demo' else permutation[int(part[1])]
  else:
   grating=None
   sex,age,permutation=get_sex_age_permutation(subject)
   variant='demo' if part=='Demo' else permutation[int(part[1])]
  command=['python', 'checkerboard.py', subject, variant]
  if grating is not None and variant not in ['default', 'NormannOhne']:
   command.append('grating_'+grating) # vertical or horizontal
  self.start_command(command)
  self.memory.setdefault(subject,{}).setdefault(part,[]).append(datetime.datetime.now())
  self.update_startbuttons(subject)


if __name__ == '__main__':
 SelectionWindow()
 Gtk.main()
