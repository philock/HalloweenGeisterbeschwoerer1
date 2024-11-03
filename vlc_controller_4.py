from msilib.schema import Media
import time
import vlc
import serial
import serial.tools.list_ports

def search_ports():
    print('Search...')
    ports = serial.tools.list_ports.comports(include_links=False)
    for port in ports :
        print('Find port '+ port.device)

    ser = serial.Serial(port.device)
    if ser.isOpen():
        ser.close()

    ser = serial.Serial(port.device, 9600, timeout=1)
    ser.flushInput()
    ser.flushOutput()
    print('Connect ' + ser.name)

arduino:serial.Serial = serial.Serial(port='COM9', baudrate=9600, timeout=10)
arduino.reset_input_buffer()

Inst:   vlc.Instance    = vlc.Instance()
player: vlc.MediaPlayer = Inst.media_player_new()
media:  vlc.Media       = Inst.media_new("test/Demons.mp4")

player.audio_set_mute(False)
player.set_fullscreen(True)

while(True):
    #prepare video
    player.set_media(media)
    player.play()
    while(not player.is_playing()):
        pass
    player.pause()

    #wait for start signal
    while(arduino.read(1) != b'6'):
        pass

    #Go
    player.play()
    time.sleep(0.2)
    while(player.is_playing()):
        pass