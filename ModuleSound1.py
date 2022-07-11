



#######################
from playsound import playsound
import pygame
# pygame.mixer.init()
#
# pygameMusic1=pygame.mixer.music
#
# pygameMusic1.load('pianoSound/1.mp3')
#
# pygameSound=pygame.mixer.Sound('pianoSound/1.MP3')
#
# #
# pygameSound.play()
# # pygameMusic1.play()
#
# playsound('pianoSound/3.mp3')
import pyglet
import threading
from pyglet.window import key
# from ModuleHand import handKeypoints,deque

from multiprocessing import  Process,Queue
# maxLen = 10
# dataDeque = deque(maxlen=maxLen)
# mf = makeFrame(dataDeque)
# hkp = handKeypoints(dataDeque)
###
# window = pyglet.window.Window()
effect1 = pyglet.resource.media('pianoSound/1.MP3', streaming=False)
effect2 = pyglet.resource.media('pianoSound/2.MP3', streaming=False)
effect3 = pyglet.resource.media('pianoSound/3.MP3', streaming=False)
effect4 = pyglet.resource.media('pianoSound/4.MP3', streaming=False)
effect5 = pyglet.resource.media('pianoSound/5.MP3', streaming=False)
# effect5.play()
soundQueue=Queue()
def playSound(soundQueue):
    # while True:

    if soundQueue.qsize() > 0:
        sound=soundQueue.get()
        effect5.play()
        print('play')
            #eval(sound).play()


class soundPlayer(threading.Thread):
    def __init__(self,soundDeque):
        super(soundPlayer,self).__init__()
        self.soundDeque=soundDeque
        self.runFlag=True
        effect5.play()
    def run(self):
        while self.runFlag:
            if len(self.soundDeque)>0:
                sound=self.soundDeque.popleft()
                eval(sound).play()

# @window.event
# def on_key_press(symbol, modifiers):
#     # key "C" get press
#     if symbol == key.Q:
#
#         effect1.play()
#     elif symbol == key.W:
#
#         effect2.play()
#     elif symbol == key.E:
#
#         effect3.play()
#     elif symbol == key.R:
#
#         effect4.play()
#     elif symbol == key.T:
#
#         effect5.play()
#
#
# @window.event
# def on_draw():
#     effect1.play()
#     from pyglet import image
#     picture = image.load('picture.png')  # 读取图片
#     # 你可以截图这张图片，生成张新的图片。
#     picture.get_region(x, y, width, height)
#     window.clear()


if __name__ == "__main__":
    # soundQueue=Queue()
    # soundQueue.put('effect1')
    # p = Process(target=playSound, args=(soundQueue,))  # 实例化进程对象
    # p.start()
    ##
    from collections import deque
    #
    soundDeque=deque()
    soundDeque.append('effect1')
    # soundDeque.append('effect5')
    sp=soundPlayer(soundDeque)
    sp.start()
    sp.join()
    #

