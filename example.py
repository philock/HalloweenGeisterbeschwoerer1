
gitgit.videolan.org / vlc / bindings / python.git / blob
? search: re
summary | shortlog | log | commit | commitdiff | tree
history | raw | HEAD
python: strip prefixes from struct fieldnames
[vlc/bindings/python.git] / examples / tkvlc.py
   1 #! /usr/bin/python
   2 # -*- coding: utf-8 -*-
   3 
   4 # tkinter example for VLC Python bindings
   5 # Copyright (C) 2015 the VideoLAN team
   6 #
   7 # This program is free software; you can redistribute it and/or modify
   8 # it under the terms of the GNU General Public License as published by
   9 # the Free Software Foundation; either version 2 of the License, or
  10 # (at your option) any later version.
  11 #
  12 # This program is distributed in the hope that it will be useful,
  13 # but WITHOUT ANY WARRANTY; without even the implied warranty of
  14 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  15 # GNU General Public License for more details.
  16 #
  17 # You should have received a copy of the GNU General Public License
  18 # along with this program; if not, write to the Free Software
  19 # Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
  20 #
  21 """A simple example for VLC python bindings using tkinter.
  22 Requires Python 3.4 or later.
  23 Author: Patrick Fay
  24 Date: 23-09-2015
  25 """
  26 
  27 # Tested with Python 3.7.4, tkinter/Tk 8.6.9 on macOS 10.13.6 only.
  28 __version__ = '20.05.04'  # mrJean1 at Gmail
  29 
  30 # import external libraries
  31 import vlc
  32 # import standard libraries
  33 import sys
  34 if sys.version_info[0] < 3:
  35     import Tkinter as Tk
  36     from Tkinter import ttk
  37     from Tkinter.filedialog import askopenfilename
  38     from Tkinter.tkMessageBox import showerror
  39 else:
  40     import tkinter as Tk
  41     from tkinter import ttk
  42     from tkinter.filedialog import askopenfilename
  43     from tkinter.messagebox import showerror
  44 from os.path import basename, expanduser, isfile, join as joined
  45 from pathlib import Path
  46 import time
  47 
  48 _isMacOS   = sys.platform.startswith('darwin')
  49 _isWindows = sys.platform.startswith('win')
  50 _isLinux   = sys.platform.startswith('linux')
  51 
  52 if _isMacOS:
  53     from ctypes import c_void_p, cdll
  54     # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
  55     # returns the tk library /usr/lib/libtk.dylib from macOS,
  56     # but we need the tkX.Y library bundled with Python 3+,
  57     # to match the version number of tkinter, _tkinter, etc.
  58     try:
  59         libtk = 'libtk%s.dylib' % (Tk.TkVersion,)
  60         prefix = getattr(sys, 'base_prefix', sys.prefix)
  61         libtk = joined(prefix, 'lib', libtk)
  62         dylib = cdll.LoadLibrary(libtk)
  63         # getNSView = dylib.TkMacOSXDrawableView is the
  64         # proper function to call, but that is non-public
  65         # (in Tk source file macosx/TkMacOSXSubwindows.c)
  66         # and dylib.TkMacOSXGetRootControl happens to call
  67         # dylib.TkMacOSXDrawableView and return the NSView
  68         _GetNSView = dylib.TkMacOSXGetRootControl
  69         # C signature: void *_GetNSView(void *drawable) to get
  70         # the Cocoa/Obj-C NSWindow.contentView attribute, the
  71         # drawable NSView object of the (drawable) NSWindow
  72         _GetNSView.restype = c_void_p
  73         _GetNSView.argtypes = c_void_p,
  74         del dylib
  75 
  76     except (NameError, OSError):  # image or symbol not found
  77         def _GetNSView(unused):
  78             return None
  79         libtk = "N/A"
  80 
  81     C_Key = "Command-"  # shortcut key modifier
  82 
  83 else:  # *nix, Xwindows and Windows, UNTESTED
  84 
  85     libtk = "N/A"
  86     C_Key = "Control-"  # shortcut key modifier
  87 
  88 
  89 class _Tk_Menu(Tk.Menu):
  90     '''Tk.Menu extended with .add_shortcut method.
  91        Note, this is a kludge just to get Command-key shortcuts to
  92        work on macOS.  Other modifiers like Ctrl-, Shift- and Option-
  93        are not handled in this code.
  94     '''
  95     _shortcuts_entries = {}
  96     _shortcuts_widget  = None
  97 
  98     def add_shortcut(self, label='', key='', command=None, **kwds):
  99         '''Like Tk.menu.add_command extended with shortcut key.
 100            If needed use modifiers like Shift- and Alt_ or Option-
 101            as before the shortcut key character.  Do not include
 102            the Command- or Control- modifier nor the <...> brackets
 103            since those are handled here, depending on platform and
 104            as needed for the binding.
 105         '''
 106         # <https://TkDocs.com/tutorial/menus.html>
 107         if not key:
 108             self.add_command(label=label, command=command, **kwds)
 109 
 110         elif _isMacOS:
 111             # keys show as upper-case, always
 112             self.add_command(label=label, accelerator='Command-' + key,
 113                                           command=command, **kwds)
 114             self.bind_shortcut(key, command, label)
 115 
 116         else:  # XXX not tested, not tested, not tested
 117             self.add_command(label=label, underline=label.lower().index(key),
 118                                           command=command, **kwds)
 119             self.bind_shortcut(key, command, label)
 120 
 121     def bind_shortcut(self, key, command, label=None):
 122         """Bind shortcut key, default modifier Command/Control.
 123         """
 124         # The accelerator modifiers on macOS are Command-,
 125         # Ctrl-, Option- and Shift-, but for .bind[_all] use
 126         # <Command-..>, <Ctrl-..>, <Option_..> and <Shift-..>,
 127         # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M6>
 128         if self._shortcuts_widget:
 129             if C_Key.lower() not in key.lower():
 130                 key = "<%s%s>" % (C_Key, key.lstrip('<').rstrip('>'))
 131             self._shortcuts_widget.bind(key, command)
 132             # remember the shortcut key for this menu item
 133             if label is not None:
 134                 item = self.index(label)
 135                 self._shortcuts_entries[item] = key
 136         # The Tk modifier for macOS' Command key is called
 137         # Meta, but there is only Meta_L[eft], no Meta_R[ight]
 138         # and both keyboard command keys generate Meta_L events.
 139         # Similarly for macOS' Option key, the modifier name is
 140         # Alt and there's only Alt_L[eft], no Alt_R[ight] and
 141         # both keyboard option keys generate Alt_L events.  See:
 142         # <https://StackOverflow.com/questions/6378556/multiple-
 143         # key-event-bindings-in-tkinter-control-e-command-apple-e-etc>
 144 
 145     def bind_shortcuts_to(self, widget):
 146         '''Set the widget for the shortcut keys, usually root.
 147         '''
 148         self._shortcuts_widget = widget
 149 
 150     def entryconfig(self, item, **kwds):
 151         """Update shortcut key binding if menu entry changed.
 152         """
 153         Tk.Menu.entryconfig(self, item, **kwds)
 154         # adjust the shortcut key binding also
 155         if self._shortcuts_widget:
 156             key = self._shortcuts_entries.get(item, None)
 157             if key is not None and "command" in kwds:
 158                 self._shortcuts_widget.bind(key, kwds["command"])
 159 
 160 
 161 class Player(Tk.Frame):
 162     """The main window has to deal with events.
 163     """
 164     _geometry = ''
 165     _stopped  = None
 166 
 167     def __init__(self, parent, title=None, video=''):
 168         Tk.Frame.__init__(self, parent)
 169 
 170         self.parent = parent  # == root
 171         self.parent.title(title or "tkVLCplayer")
 172         self.video = expanduser(video)
 173 
 174         # Menu Bar
 175         #   File Menu
 176         menubar = Tk.Menu(self.parent)
 177         self.parent.config(menu=menubar)
 178 
 179         fileMenu = _Tk_Menu(menubar)
 180         fileMenu.bind_shortcuts_to(parent)  # XXX must be root?
 181 
 182         fileMenu.add_shortcut("Open...", 'o', self.OnOpen)
 183         fileMenu.add_separator()
 184         fileMenu.add_shortcut("Play", 'p', self.OnPlay)  # Play/Pause
 185         fileMenu.add_command(label="Stop", command=self.OnStop)
 186         fileMenu.add_separator()
 187         fileMenu.add_shortcut("Mute", 'm', self.OnMute)
 188         fileMenu.add_separator()
 189         fileMenu.add_shortcut("Close", 'w' if _isMacOS else 's', self.OnClose)
 190         if _isMacOS:  # intended for and tested on macOS
 191             fileMenu.add_separator()
 192             fileMenu.add_shortcut("Full Screen", 'f', self.OnFullScreen)
 193         menubar.add_cascade(label="File", menu=fileMenu)
 194         self.fileMenu = fileMenu
 195         self.playIndex = fileMenu.index("Play")
 196         self.muteIndex = fileMenu.index("Mute")
 197 
 198         # first, top panel shows video
 199 
 200         self.videopanel = ttk.Frame(self.parent)
 201         self.canvas = Tk.Canvas(self.videopanel)
 202         self.canvas.pack(fill=Tk.BOTH, expand=1)
 203         self.videopanel.pack(fill=Tk.BOTH, expand=1)
 204 
 205         # panel to hold buttons
 206         self.buttons_panel = Tk.Toplevel(self.parent)
 207         self.buttons_panel.title("")
 208         self.is_buttons_panel_anchor_active = False
 209 
 210         buttons = ttk.Frame(self.buttons_panel)
 211         self.playButton = ttk.Button(buttons, text="Play", command=self.OnPlay)
 212         stop            = ttk.Button(buttons, text="Stop", command=self.OnStop)
 213         self.muteButton = ttk.Button(buttons, text="Mute", command=self.OnMute)
 214         self.playButton.pack(side=Tk.LEFT)
 215         stop.pack(side=Tk.LEFT)
 216         self.muteButton.pack(side=Tk.LEFT)
 217 
 218         self.volMuted = False
 219         self.volVar = Tk.IntVar()
 220         self.volSlider = Tk.Scale(buttons, variable=self.volVar, command=self.OnVolume,
 221                                   from_=0, to=100, orient=Tk.HORIZONTAL, length=200,
 222                                   showvalue=0, label='Volume')
 223         self.volSlider.pack(side=Tk.RIGHT)
 224         buttons.pack(side=Tk.BOTTOM, fill=Tk.X)
 225 
 226 
 227         # panel to hold player time slider
 228         timers = ttk.Frame(self.buttons_panel)
 229         self.timeVar = Tk.DoubleVar()
 230         self.timeSliderLast = 0
 231         self.timeSlider = Tk.Scale(timers, variable=self.timeVar, command=self.OnTime,
 232                                    from_=0, to=1000, orient=Tk.HORIZONTAL, length=500,
 233                                    showvalue=0)  # label='Time',
 234         self.timeSlider.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
 235         self.timeSliderUpdate = time.time()
 236         timers.pack(side=Tk.BOTTOM, fill=Tk.X)
 237 
 238 
 239         # VLC player
 240         args = []
 241         if _isLinux:
 242             args.append('--no-xlib')
 243         self.Instance = vlc.Instance(args)
 244         self.player = self.Instance.media_player_new()
 245 
 246         self.parent.bind("<Configure>", self.OnConfigure)  # catch window resize, etc.
 247         self.parent.update()
 248 
 249         # After parent.update() otherwise panel is ignored.
 250         self.buttons_panel.overrideredirect(True)
 251 
 252         # Estetic, to keep our video panel at least as wide as our buttons panel.
 253         self.parent.minsize(width=502, height=0)
 254 
 255         if _isMacOS:
 256             # Only tested on MacOS so far. Enable for other OS after verified tests.
 257             self.is_buttons_panel_anchor_active = True
 258 
 259             # Detect dragging of the buttons panel.
 260             self.buttons_panel.bind("<Button-1>", lambda event: setattr(self, "has_clicked_on_buttons_panel", event.y < 0))
 261             self.buttons_panel.bind("<B1-Motion>", self._DetectButtonsPanelDragging)
 262             self.buttons_panel.bind("<ButtonRelease-1>", lambda _: setattr(self, "has_clicked_on_buttons_panel", False))
 263             self.has_clicked_on_buttons_panel = False
 264         else:
 265             self.is_buttons_panel_anchor_active = False
 266 
 267         self._AnchorButtonsPanel()
 268 
 269         self.OnTick()  # set the timer up
 270 
 271     def OnClose(self, *unused):
 272         """Closes the window and quit.
 273         """
 274         # print("_quit: bye")
 275         self.parent.quit()  # stops mainloop
 276         self.parent.destroy()  # this is necessary on Windows to avoid
 277         # ... Fatal Python Error: PyEval_RestoreThread: NULL tstate
 278 
 279     def _DetectButtonsPanelDragging(self, _):
 280         """If our last click was on the boarder
 281            we disable the anchor.
 282         """
 283         if self.has_clicked_on_buttons_panel:
 284             self.is_buttons_panel_anchor_active = False
 285             self.buttons_panel.unbind("<Button-1>")
 286             self.buttons_panel.unbind("<B1-Motion>")
 287             self.buttons_panel.unbind("<ButtonRelease-1>")
 288 
 289     def _AnchorButtonsPanel(self):
 290         video_height = self.parent.winfo_height()
 291         panel_x = self.parent.winfo_x()
 292         panel_y = self.parent.winfo_y() + video_height + 23 # 23 seems to put the panel just below our video.
 293         panel_height = self.buttons_panel.winfo_height()
 294         panel_width = self.parent.winfo_width()
 295         self.buttons_panel.geometry("%sx%s+%s+%s" % (panel_width, panel_height, panel_x, panel_y))
 296 
 297     def OnConfigure(self, *unused):
 298         """Some widget configuration changed.
 299         """
 300         # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M12>
 301         self._geometry = ''  # force .OnResize in .OnTick, recursive?
 302 
 303         if self.is_buttons_panel_anchor_active:
 304             self._AnchorButtonsPanel()
 305 
 306     def OnFullScreen(self, *unused):
 307         """Toggle full screen, macOS only.
 308         """
 309         # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/wm.htm#M10>
 310         f = not self.parent.attributes("-fullscreen")  # or .wm_attributes
 311         if f:
 312             self._previouscreen = self.parent.geometry()
 313             self.parent.attributes("-fullscreen", f)  # or .wm_attributes
 314             self.parent.bind("<Escape>", self.OnFullScreen)
 315         else:
 316             self.parent.attributes("-fullscreen", f)  # or .wm_attributes
 317             self.parent.geometry(self._previouscreen)
 318             self.parent.unbind("<Escape>")
 319 
 320     def OnMute(self, *unused):
 321         """Mute/Unmute audio.
 322         """
 323         # audio un/mute may be unreliable, see vlc.py docs.
 324         self.volMuted = m = not self.volMuted  # self.player.audio_get_mute()
 325         self.player.audio_set_mute(m)
 326         u = "Unmute" if m else "Mute"
 327         self.fileMenu.entryconfig(self.muteIndex, label=u)
 328         self.muteButton.config(text=u)
 329         # update the volume slider text
 330         self.OnVolume()
 331 
 332     def OnOpen(self, *unused):
 333         """Pop up a new dialow window to choose a file, then play the selected file.
 334         """
 335         # if a file is already running, then stop it.
 336         self.OnStop()
 337         # Create a file dialog opened in the current home directory, where
 338         # you can display all kind of files, having as title "Choose a video".
 339         video = askopenfilename(initialdir = Path(expanduser("~")),
 340                                 title = "Choose a video",
 341                                 filetypes = (("all files", "*.*"),
 342                                              ("mp4 files", "*.mp4"),
 343                                              ("mov files", "*.mov")))
 344         self._Play(video)
 345 
 346     def _Pause_Play(self, playing):
 347         # re-label menu item and button, adjust callbacks
 348         p = 'Pause' if playing else 'Play'
 349         c = self.OnPlay if playing is None else self.OnPause
 350         self.fileMenu.entryconfig(self.playIndex, label=p, command=c)
 351         # self.fileMenu.bind_shortcut('p', c)  # XXX handled
 352         self.playButton.config(text=p, command=c)
 353         self._stopped = False
 354 
 355     def _Play(self, video):
 356         # helper for OnOpen and OnPlay
 357         if isfile(video):  # Creation
 358             m = self.Instance.media_new(str(video))  # Path, unicode
 359             self.player.set_media(m)
 360             self.parent.title("tkVLCplayer - %s" % (basename(video),))
 361 
 362             # set the window id where to render VLC's video output
 363             h = self.videopanel.winfo_id()  # .winfo_visualid()?
 364             if _isWindows:
 365                 self.player.set_hwnd(h)
 366             elif _isMacOS:
 367                 # XXX 1) using the videopanel.winfo_id() handle
 368                 # causes the video to play in the entire panel on
 369                 # macOS, covering the buttons, sliders, etc.
 370                 # XXX 2) .winfo_id() to return NSView on macOS?
 371                 v = _GetNSView(h)
 372                 if v:
 373                     self.player.set_nsobject(v)
 374                 else:
 375                     self.player.set_xwindow(h)  # plays audio, no video
 376             else:
 377                 self.player.set_xwindow(h)  # fails on Windows
 378             # FIXME: this should be made cross-platform
 379             self.OnPlay()
 380 
 381     def OnPause(self, *unused):
 382         """Toggle between Pause and Play.
 383         """
 384         if self.player.get_media():
 385             self._Pause_Play(not self.player.is_playing())
 386             self.player.pause()  # toggles
 387 
 388     def OnPlay(self, *unused):
 389         """Play video, if none is loaded, open the dialog window.
 390         """
 391         # if there's no video to play or playing,
 392         # open a Tk.FileDialog to select a file
 393         if not self.player.get_media():
 394             if self.video:
 395                 self._Play(expanduser(self.video))
 396                 self.video = ''
 397             else:
 398                 self.OnOpen()
 399         # Try to play, if this fails display an error message
 400         elif self.player.play():  # == -1
 401             self.showError("Unable to play the video.")
 402         else:
 403             self._Pause_Play(True)
 404             # set volume slider to audio level
 405             vol = self.player.audio_get_volume()
 406             if vol > 0:
 407                 self.volVar.set(vol)
 408                 self.volSlider.set(vol)
 409 
 410     def OnResize(self, *unused):
 411         """Adjust the window/frame to the video aspect ratio.
 412         """
 413         g = self.parent.geometry()
 414         if g != self._geometry and self.player:
 415             u, v = self.player.video_get_size()  # often (0, 0)
 416             if v > 0 and u > 0:
 417                 # get window size and position
 418                 g, x, y = g.split('+')
 419                 w, h = g.split('x')
 420                 # alternatively, use .winfo_...
 421                 # w = self.parent.winfo_width()
 422                 # h = self.parent.winfo_height()
 423                 # x = self.parent.winfo_x()
 424                 # y = self.parent.winfo_y()
 425                 # use the video aspect ratio ...
 426                 if u > v:  # ... for landscape
 427                     # adjust the window height
 428                     h = round(float(w) * v / u)
 429                 else:  # ... for portrait
 430                     # adjust the window width
 431                     w = round(float(h) * u / v)
 432                 self.parent.geometry("%sx%s+%s+%s" % (w, h, x, y))
 433                 self._geometry = self.parent.geometry()  # actual
 434 
 435     def OnStop(self, *unused):
 436         """Stop the player, resets media.
 437         """
 438         if self.player:
 439             self.player.stop()
 440             self._Pause_Play(None)
 441             # reset the time slider
 442             self.timeSlider.set(0)
 443             self._stopped = True
 444         # XXX on macOS libVLC prints these error messages:
 445         # [h264 @ 0x7f84fb061200] get_buffer() failed
 446         # [h264 @ 0x7f84fb061200] thread_get_buffer() failed
 447         # [h264 @ 0x7f84fb061200] decode_slice_header error
 448         # [h264 @ 0x7f84fb061200] no frame!
 449 
 450     def OnTick(self):
 451         """Timer tick, update the time slider to the video time.
 452         """
 453         if self.player:
 454             # since the self.player.get_length may change while
 455             # playing, re-set the timeSlider to the correct range
 456             t = self.player.get_length() * 1e-3  # to seconds
 457             if t > 0:
 458                 self.timeSlider.config(to=t)
 459 
 460                 t = self.player.get_time() * 1e-3  # to seconds
 461                 # don't change slider while user is messing with it
 462                 if t > 0 and time.time() > (self.timeSliderUpdate + 2):
 463                     self.timeSlider.set(t)
 464                     self.timeSliderLast = int(self.timeVar.get())
 465         # start the 1 second timer again
 466         self.parent.after(1000, self.OnTick)
 467         # adjust window to video aspect ratio, done periodically
 468         # on purpose since the player.video_get_size() only
 469         # returns non-zero sizes after playing for a while
 470         if not self._geometry:
 471             self.OnResize()
 472 
 473     def OnTime(self, *unused):
 474         if self.player:
 475             t = self.timeVar.get()
 476             if self.timeSliderLast != int(t):
 477                 # this is a hack. The timer updates the time slider.
 478                 # This change causes this rtn (the 'slider has changed' rtn)
 479                 # to be invoked.  I can't tell the difference between when
 480                 # the user has manually moved the slider and when the timer
 481                 # changed the slider.  But when the user moves the slider
 482                 # tkinter only notifies this rtn about once per second and
 483                 # when the slider has quit moving.
 484                 # Also, the tkinter notification value has no fractional
 485                 # seconds.  The timer update rtn saves off the last update
 486                 # value (rounded to integer seconds) in timeSliderLast if
 487                 # the notification time (sval) is the same as the last saved
 488                 # time timeSliderLast then we know that this notification is
 489                 # due to the timer changing the slider.  Otherwise the
 490                 # notification is due to the user changing the slider.  If
 491                 # the user is changing the slider then I have the timer
 492                 # routine wait for at least 2 seconds before it starts
 493                 # updating the slider again (so the timer doesn't start
 494                 # fighting with the user).
 495                 self.player.set_time(int(t * 1e3))  # milliseconds
 496                 self.timeSliderUpdate = time.time()
 497 
 498     def OnVolume(self, *unused):
 499         """Volume slider changed, adjust the audio volume.
 500         """
 501         vol = min(self.volVar.get(), 100)
 502         v_M = "%d%s" % (vol, " (Muted)" if self.volMuted else '')
 503         self.volSlider.config(label="Volume " + v_M)
 504         if self.player and not self._stopped:
 505             # .audio_set_volume returns 0 if success, -1 otherwise,
 506             # e.g. if the player is stopped or doesn't have media
 507             if self.player.audio_set_volume(vol):  # and self.player.get_media():
 508                 self.showError("Failed to set the volume: %s." % (v_M,))
 509 
 510     def showError(self, message):
 511         """Display a simple error dialog.
 512         """
 513         self.OnStop()
 514         showerror(self.parent.title(), message)
 515 
 516 
 517 if __name__ == "__main__":
 518 
 519     _video = ''
 520 
 521     while len(sys.argv) > 1:
 522         arg = sys.argv.pop(1)
 523         if arg.lower() in ('-v', '--version'):
 524             # show all versions, sample output on macOS:
 525             # % python3 ./tkvlc.py -v
 526             # tkvlc.py: 2019.07.28 (tkinter 8.6 /Library/Frameworks/Python.framework/Versions/3.7/lib/libtk8.6.dylib)
 527             # vlc.py: 3.0.6109 (Sun Mar 31 20:14:16 2019 3.0.6)
 528             # LibVLC version: 3.0.6 Vetinari (0x3000600)
 529             # LibVLC compiler: clang: warning: argument unused during compilation: '-mmacosx-version-min=10.7' [-Wunused-command-line-argument]
 530             # Plugin path: /Applications/VLC3.0.6.app/Contents/MacOS/plugins
 531             # Python: 3.7.4 (64bit) macOS 10.13.6
 532 
 533             # Print version of this vlc.py and of the libvlc
 534             print('%s: %s (%s %s %s)' % (basename(__file__), __version__,
 535                                          Tk.__name__, Tk.TkVersion, libtk))
 536             try:
 537                 vlc.print_version()
 538                 vlc.print_python()
 539             except AttributeError:
 540                 pass
 541             sys.exit(0)
 542 
 543         elif arg.startswith('-'):
 544             print('usage: %s  [-v | --version]  [<video_file_name>]' % (sys.argv[0],))
 545             sys.exit(1)
 546 
 547         elif arg:  # video file
 548             _video = expanduser(arg)
 549             if not isfile(_video):
 550                 print('%s error: no such file: %r' % (sys.argv[0], arg))
 551                 sys.exit(1)
 552 
 553     # Create a Tk.App() to handle the windowing event loop
 554     root = Tk.Tk()
 555     player = Player(root, video=_video)
 556     root.protocol("WM_DELETE_WINDOW", player.OnClose)  # XXX unnecessary (on macOS)
 557     root.mainloop()
Python bindings for libvlc
RSS
Atom
