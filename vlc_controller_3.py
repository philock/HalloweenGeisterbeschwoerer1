from msilib.schema import Media
import time
import vlc

Inst: vlc.Instance = vlc.Instance()
player: vlc.MediaPlayer = Inst.media_player_new("test/Cat.mp4")
media: vlc.Media = Inst.media_new("test/Cat.mp4")

player.set_fullscreen(True)
player.set_media(media)
player.play()
time.sleep(1)
while(player.is_playing()):
    pass
print("next")
player.set_media(media)
player.play()


time.sleep(30)