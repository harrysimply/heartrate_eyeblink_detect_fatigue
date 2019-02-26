
import os
import pygame
import time
import pygame
import time

pygame.mixer.init()

def tired_detect():
    print("检测疲劳中>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    return True



def tired_warning():
    print("开始播放警报声音>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    warning='./warning_voice/give_a_warning.mp3'

    os.system("play " + warning)





def tired_playmusic():
    print("播放歌单>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    song = './warning_voice/give_a_song.mp3'
    os.system("play " + song)
    path ='./songs'
    files=os.listdir(path)
    print(files)

    for file in files:
        print(file)
        os.system("play ./songs/"+file)

def tired_finalcall():
    print("让语音助手打电话求助>>>>>>>>>>>>>>>")
    call = './warning_voice/give_a_call.mp3'
    os.system("play "+call)

def new_warning():

    print("开始播放声音")
    track = pygame.mixer.music.load('./warning_voice/rest_properly.wav')
    pygame.mixer.music.play()
    time.sleep(5)
    pygame.mixer.music.stop()
    print("声音播放结束")

if __name__=='__main__':
    if tired_detect():
        print("！！！检测到已经出现疲劳状态")
    # tired_warning()
    # tired_finalcall()
    # tired_playmusic()
    tired_finalcall()
    #new_warning()

