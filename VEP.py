#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :

import os
import subprocess

# cd to the main directory
os.chdir(os.path.join(os.path.dirname(__file__)))

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
from gi.repository import Gtk,Gdk,GLib

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
    font-weight: bold;
    font-size: 50pt;
    padding: 0 20px 0 20px;
}
.css_orange {
    background-color: orange;
    background: orange;
    color: white;
    font-weight: bold;
    font-size: 50pt;
    padding: 0 20px 0 20px;
}
.css_red {
    background-color: red;
    background: red;
    color: white;
    font-weight: bold;
    font-size: 50pt;
    padding: 0 20px 0 20px;
}
'''

parts=['demonstration','CB']

def good_subject_name(ID):
 is_good=False
 if ID.startswith('test'):
  is_good=True
 elif len(ID)==4:
  # [KP]\d\d\d
  is_good=ID[0] in ('K','P') and \
  ID[1].isdigit() and ID[2].isdigit() and ID[3].isdigit()
 return is_good

class SelectionWindow(Gtk.Window):
 def __init__(self, parent=None):
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

  self.set_title("VEP Study")
  self.set_default_size(600, 600)

  self.box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
  self.add(self.box)

  self.SubjectEntryBoxFrame=Gtk.Frame(label="VP Code")
  self.box.add(self.SubjectEntryBoxFrame)
  self.SubjectEntryBox=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
  self.SubjectEntryBoxFrame.add(self.SubjectEntryBox)

  self.SubjectEntry=Gtk.Entry()
  self.SubjectEntryBox.pack_start(self.SubjectEntry,True,True,0)
  self.SubjectEntry.get_style_context().add_class("css_red")
  self.SubjectEntry.connect("changed", self.entry_set_appearance)

  self.buttonbox=Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
  self.buttonbox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
  self.buttonbox.set_homogeneous(False)
  self.box.pack_start(self.buttonbox,True,True,0)


  # Startbox with 4 horizontal buttons Lab1, Training1, Training2, Lab2
  self.startbox=Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
  self.startbox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
  self.startbox.set_homogeneous(False)
  self.buttonbox.pack_start(self.startbox,True,True,0)

  self.StartButtons={}
  StartButton=Gtk.Button(label="Demonstration")
  StartButton.get_style_context().add_class("css_normal")
  StartButton.connect("button-press-event",self.start_demonstration)
  self.startbox.add(StartButton)
  # Make the buttons accessible from a callback
  self.StartButtons['demonstration']=StartButton

  StartButton=Gtk.Button(label="Checkerboard")
  StartButton.get_style_context().add_class("css_normal")
  StartButton.connect("button-press-event",self.start_VEP)
  self.startbox.add(StartButton)
  # Make the buttons accessible from a callback
  self.StartButtons['CB']=StartButton

  self.StartTestsAtFrame=Gtk.Frame(label="Start tests at")
  self.StartTestsAtFrame.get_style_context().add_class("css_normal")
  self.buttonbox.add(self.StartTestsAtFrame)
  self.StartTestsAt=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 6, 1)
  self.StartTestsAtFrame.add(self.StartTestsAt)
  self.StartTestsAt.set_value(0)

  self.ExitButton=Gtk.Button(label="Ende")
  self.ExitButton.get_style_context().add_class("css_orange")
  self.ExitButton.connect("button-press-event", self.my_quit)
  self.buttonbox.add(self.ExitButton)

  self.move(500,200)
  self.show_all()
 def update_startbuttons(self,ID):
  is_good=good_subject_name(ID)
  for part in parts:
   c=self.StartButtons[part].get_style_context()
   if not is_good:
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
  else:
   c.remove_class('css_normal')
   c.add_class('css_red')
  self.update_startbuttons(ID)
 def my_quit(self,*w):
  Gtk.main_quit(w)

 def start_command(self, call):
  if self.command is not None and self.command.poll() is None:
   # Process is still alife
   print("Refusing start, process is running!")
   return
  self.command=subprocess.Popen(call, shell=False)
 def start_demonstration(self, widget, response):
  subject=self.SubjectEntry.get_text()
  if not good_subject_name(subject): return
  self.start_command(['python','checkerboard.py', subject, 'demo'])
 def start_VEP(self, widget, response):
  subject=self.SubjectEntry.get_text()
  if not good_subject_name(subject): return
  self.start_command(['python','checkerboard.py', subject, self.StartTestsAt.get_value()])

if __name__ == '__main__':
 SelectionWindow()
 Gtk.main()
