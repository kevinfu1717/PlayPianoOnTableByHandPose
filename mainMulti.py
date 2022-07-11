import pygame
from pygame.locals import *
from sys import exit
import cv2
import time
from collections import deque
import traceback
from ModuleSound import effect1,effect2,effect3,effect4,effect5
from ModuleHand import handKeypoints
# from ModuleHandPaddle import handKeypoints
from ModuleInput import  FrameProducer
pygame.init()

def yBiasCal(fringerTip,pressLineDict1):#higher than line is + else -
    biasDict={}
    for index,ft in fringerTip.items():
        print('ft[1]-(fringerTipDown[index][1]+upRange',ft[1],pressLineDict1[index])
        ## ft[1]<0  fringerTipDown<0
        biasDict[index]=ft[1]-(pressLineDict1[index])

    return  biasDict

def pressDetect(biasDictBefore,biasDictNow):
    biasMinerList=[]
    indexList=[]
    fringerTipIndex=-1
    print('biasDictBefore,biasDictNow',biasDictBefore,biasDictNow)
    for index in range(5):
        try:
            if biasDictBefore[index]>0 and biasDictNow[index]<0:
                biasMinerList.append(biasDictBefore[index]-biasDictNow[index])
                indexList.append(index)
        except Exception as e:
            print(e)


    if len(biasMinerList)>0:
        mi=biasMinerList.index(max(biasMinerList))
        fringerTipIndex=indexList[mi]
        print('press----------',fringerTipIndex)
    return fringerTipIndex


def uiProcess(image,ftDown1,ftDown2,pressLineDict1,pressLineDict2):
    if len(ftDown1)==5 and len(pressLineDict1)==0:
        image = drawPressArea(image, ftDown1, [])
    if len(ftDown2)==5 and len(pressLineDict2)==0:

        image = drawPressArea(image, ftDown2, [])

    if len(pressLineDict1)==5:
        image=drawPressArea(image, ftDown1,pressLineDict1)
    if len(pressLineDict2)==5:
        image=drawPressArea(image, ftDown2,pressLineDict2)
    return image

def pressLineCal(ftDown1,ftUp1,rangeIndexList):#for position y: ftDown1<0,ftUp1<0,ftDown1<ftUp1
    pressLineDict={}
    for index,ftd in ftDown1.items():
        print('pressLineCal',index,ftUp1[index][1],ftd[1])
        print(rangeIndexList[index])
        y_min=int(ftd[1]+(ftUp1[index][1]-ftd[1])*rangeIndexList[index])
        pressLineDict[index]=y_min
    ftUp1={}

    ## only reset ftUp ,keep ftDown
    return pressLineDict,ftUp1


def drawPressArea(image,ftDown1,pressLineDict1):#for position y: ftDown1<0,pressLineDict1<0,ftDown1<pressLineDict1
    # print('ftDown1--',ftDown1)
    # print('pressLineDict1',pressLineDict1,ftDown1)
    for index,ft in ftDown1.items():
        try:
            bias=pressLineDict1[index]
        except:
            bias=ft[1]-2
        x_max=ft[0]+15
        x_min=ft[0]-15
        y_max=int(-1*ft[1])
        y_min=int(-1*ft[1]+(ft[1]-bias))
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 0, 0), 4)

    return image
def frameShow(frame,screen):

    #
    # timeStamp = cap.get(cv2.CAP_PROP_POS_MSEC)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    print('frame',frame.shape)
    frame = cv2.transpose(frame)
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0, 0))
    pygame.display.update()
    # return timeStamp
def keyboardResponse(prodecer,handKeypointer,
                    ft1, ft2,ftDown1,ftDown2,ftUp1,ftUp2):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            prodecer.runFlag = False
            handKeypointer.runFlag = False
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN :
                print('down',ft1,ft2)
                return ft1,ft2,ftUp1,ftUp2
            if event.key == pygame.K_UP :
                print('up',ft1,ft2)
                return ftDown1,ftDown2,ft1,ft2

            if event.key == pygame.K_1:
                print('key1')
                effect5.play()
    return ftDown1,ftDown2,ftUp1,ftUp2
def loopRun(dataDeque,wSize,hSize,prodecer,handKeypointer,rangeIndexList,skipFrame):
    # tip position of hand down
    ftDown1={}
    ftDown2={}
    # tip position for now
    ft1={}
    ft2={}
    # tip position of hand up
    ftUp1={}
    ftUp2={}
    #
    pressLineDict1={}
    pressLineDict2={}
    #
    biasDict1={}
    biasDict2={}
    screen = pygame.display.set_mode((wSize,hSize))
    # cap = cv2.VideoCapture(path)

    num=-1
    result={}
    while True:
        ##

        FPS=prodecer.fps/skipFrame
        if FPS > 0:
            videoFlag = True
        else:
            videoFlag = False
            ##

            ##

        ftDown1,ftDown2,ftUp1,ftUp2=keyboardResponse(prodecer, handKeypointer,
                                         ft1, ft2,ftDown1,ftDown2,ftUp1,ftUp2)
        ##
        if len(ftDown1)==5 and len(ftUp1)==5:
            pressLineDict1, ftUp1=pressLineCal(ftDown1, ftUp1, rangeIndexList)
        if len(ftDown2)==5 and len(ftUp2)==5:
            pressLineDict2, ftUp2=pressLineCal(ftDown2, ftUp2, rangeIndexList)
        # print('ppp', len(dataDeque), len(result))
        if len(dataDeque)==0 and len(result)==0:
            time.sleep(0.1)
            continue
        # print('FPS',FPS)


        if len(result)==0:
        ##
            result=dataDeque.popleft()

        image=result['image']
        ft1=result['fringerTip1']
        ft2=result['fringerTip2']


        if videoFlag:

            num += 1
            if num == 0:
                T0 = time.time()
                print('T0',T0,num*(1./FPS))
        try:

            image = uiProcess(image,ftDown1,ftDown2,pressLineDict1,pressLineDict2)

            # print('ft1,2',ft1,ft2)
            if len(ft1) ==5 and len(pressLineDict1) == 5 :#to do: do not need all fringer tip to be detected at that time
                bl1 = yBiasCal(ft1, pressLineDict1)
                if len(biasDict1) > 0 and len(bl1) > 0:
                    # print('biasDict1', biasDict1, bl1)
                    fringerTipIndex1 = pressDetect(biasDict1, bl1)

                    if fringerTipIndex1 >= 0:
                        eval('effect' + str(fringerTipIndex1+1)).play()

                        cv2.putText(image,  str(fringerTipIndex1+1),(int( ftDown1[fringerTipIndex1][0]),int(-1*ftDown1[fringerTipIndex1][1])),  cv2.FONT_HERSHEY_COMPLEX,
                                    2, (0, 255, 0), thickness=2, lineType=4)


                        print('play effect:', str(fringerTipIndex1))
                biasDict1 = bl1
            if len(ft2) == 5 and len(pressLineDict2) == 5 :
                bl2 = yBiasCal(ft2, pressLineDict2)
                ##################

                if len(biasDict2) > 0 and len(bl2) > 0:
                    # print('biasDict2', biasDict2, bl2)
                    fringerTipIndex2 = pressDetect(biasDict2, bl2)
                    if fringerTipIndex2 >= 0:
                        eval('effect' + str(5 - fringerTipIndex2)).play()
                        cv2.putText(image,  str(fringerTipIndex2+1),
                                    ( int(ftDown2[fringerTipIndex2][0]),int(-1*ftDown2[fringerTipIndex2][1])),  cv2.FONT_HERSHEY_COMPLEX,
                                    2, (0, 255, 0), thickness=2, lineType=4)
                biasDict2 = bl2



        except Exception as e:
            traceback.print_exc()
        frameShow(image, screen)
        #clear result
        result={}


if __name__=='__main__':
    from initParam import link,wSize,hSize,rangeIndexList,maxLen,skipFrmae
    ft1=ft2=ftDown1=ftDown2=[]
    biasDict1=biasDict2= {}
    dataDeque = deque(maxlen=maxLen)
    resultDeque=deque()
    producer = FrameProducer(dataDeque, wSize, hSize, link,skipFrmae)

    handKeypointer = handKeypoints(dataDeque, resultDeque,savePath='')
    producer.start()
    handKeypointer.start()
    loopRun(resultDeque, wSize, hSize, producer,handKeypointer,rangeIndexList,skipFrmae)