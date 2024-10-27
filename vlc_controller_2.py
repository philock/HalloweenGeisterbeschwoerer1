import os
import time
from vlc import Instance


Player: Instance = Instance('--loop')
mediaList = Player.media_list_new()

path = r"C:\Users\phili\Programmierung\ESP32\Keyboard_test\test"
songs = os.listdir(path)
for s in songs:
    mediaList.add_media(Player.media_new(os.path.join(path,s)))
listPlayer = Player.media_list_player_new()
listPlayer.set_media_list(mediaList)

listPlayer.play()

time.sleep(30)