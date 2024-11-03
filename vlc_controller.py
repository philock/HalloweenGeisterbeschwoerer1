import vlc
import time
import os
import serial
import serial.tools.list_ports

arduino:serial.Serial = serial.Serial(port='COM9', baudrate=9600, timeout=10)
arduino.reset_input_buffer()

# Path to your video file
video_path_demons = "test/HalloweenVideos/ConvertedNew/Demons.mp4"
video_path_fire = "test/HalloweenVideos/ConvertedNew/Fire.mp4"
video_path_demons_old = "test/Demons.mp4"

# Create an instance of VLC player
player = vlc.MediaPlayer(video_path_demons)
player.set_fullscreen(True)

def play_video():
    player.set_fullscreen(True)
    player.play()

    time.sleep(0.2)

    # Wait for the video to finish
    while player.is_playing():
        time.sleep(1)

    time.sleep(1)

    #player.stop()
    #player.set_media(vlc.Media(video_path_demons))

    #input("Press Enter to play again...")
    #while(arduino.read(1) != b'6'):
    #    time.sleep(1)

    while(arduino.in_waiting == 0):
        time.sleep(1)
    
    time.sleep(0.1)

    received = arduino.read(1)
    if(received == b'6'):
        player.set_media(vlc.Media(video_path_demons))
    elif(received == b'7'):
        player.set_media(vlc.Media(video_path_fire))

    time.sleep(0.2)
    


while True:
    play_video()