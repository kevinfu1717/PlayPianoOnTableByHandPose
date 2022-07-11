# Play piano by a table with keypoint hand pose 基于实时手部关键点识别实现在平面上弹钢琴

## Introduction

配置好环境，在平面上放上一个摄像头，运行程序，让我们弹奏一首欢乐颂吧~
<br>
> 直接上视频

[![Watch the video](https://raw.github.com/GabLeRoux/WebMole/master/ressources/WebMole_Youtube_Video.png)](https://www.bilibili.com/video/BV1wT411g7MU/)

B站地址：https://www.bilibili.com/video/BV1wT411g7MU/


## Environment

1. 从github或gitee上clone MMpose项目到本地，把本项目内容全部复制到mmpose/demo文件夹下。

2. cd到 mmpose 文件夹下，运行 python setup.py install 安装需要的库

3. 在mmpose/demo文件夹中运行 mainMulti.py文件（python mainMulti.py)

4. 若要修改使用摄像头画面或视频文件,修改预览画面大小，跳帧数,可修改initParam.py, 

5. 本项目中，暂时设定了右手的 拇指到尾指分别对应 do ,re ,mi ,fa ,sol 这5个音。

6. 因要实现弹钢琴的效果，摄像头放置于图示位置是最好的。而摄像头不能太高，否则摄像头拍摄角度太大，导致手指尖上下移动的变化就不明显。但可以适当向下倾，有利于模型识别。

<img src="https://ai-studio-static-online.cdn.bcebos.com/04b870027d3e4953843b6149173f9f574ec11abb47224fc39730ae08955af6b1" width="800px" />

7.摄像头可选用普通usb网络摄像头。最好清晰度能高一点，不要有畸变的。我这里选用手机前置摄像头录了一段视频

## Param setting

1.设置link来设置输入图片的来源，如视频则为视频地址：link='./pianoSound/hand6.mp4'，若拿摄像头画面则设为摄像头对应id，如：link=0

2.设置wSize=800，hSize=450 来设置获取图片的宽高

3 rangeIndexList=[0.45,0.59,0.55,0.5,0.5]分别代表拇指，食指，中指，无名指，尾指的按键响应区域在纵坐标方向的大小。使用时需先进行校准，这与校准参数有关【详见下一节校准】。

4.skipFrmae=1即不跳帧处理，skipFrame=3则代表每3帧处理一帧

## Run

### 1. 确认安装好对应的库

### 2. 运行mainMultiThread.py

启动后，pygame会启动一个新窗口，并显示视频或摄像头画面。这时需要进行校准。

### 3. 校准：

3.1 五指放于桌面上，对应5只手指都按下琴键，如下图，这时识别正常后按键盘方向键下，获取指尖在桌面位置。

成功后会标示下限位置，对应代码中的ftDown1（右手）或ftDown2（左手），暂时只支持同一时间只有一只手。

![](https://ai-studio-static-online.cdn.bcebos.com/271a452970b54a979bc20f49e9435b381ff7092dc6a64598a76052d3539aa588)

 3.2 同时抬起5只手指，对应5只手指都没有按下琴键，并按键盘的上方向键
 
![](https://ai-studio-static-online.cdn.bcebos.com/adb563616b98488e8d265033a953d1b0f974839c365f4a14bcf1122d549f1500)


3.3 这时若出现如上图的矩形即校准成功。矩形为指尖响应区，即指尖到这里就会响起对应的声音。

> 只需关注纵向位置，横向位置可忽略，即指尖只需落在响应区矩形的上横线与下横向之间即可，不用落在左右竖线之间）

3.4 设置rangeIndexList，list中的5个值分别对应拇指，食指，中指，无名指，尾指的响应区大小，为1则从校准时最低到校准时手指的最高处，所以正常在0.4~0.5附近这里给出一定参考，如：[0.45,0.59,0.55,0.5,0.5]