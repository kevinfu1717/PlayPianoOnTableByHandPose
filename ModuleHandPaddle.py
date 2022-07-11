
import os
import os.path as osp
import matplotlib.pyplot as plt

import time

import numpy as np
from collections import deque
import cv2
import paddlehub as hub
import threading
import os
os.environ['CUDA_VISIBLE_DEVICES']='0'
from playsound import playsound
class argsClass:
    def __init__(self):
        self.pose_config="../configs/hand/3d_kpt_sview_rgb_img/internet/interhand3d/res50_interhand3d_all_256x256.py"
        self.pose_checkpoint="https://download.openmmlab.com/mmpose/hand3d/internet/res50_intehand3d_all_256x256-b9c1cf4c_20210506.pth"
        self.img_root="../tests/data/interhand2.6m/fringer"
        self.json_file="../tests/data/interhand2.6m/my.json"
        self.camera_param_file=None
        self.gt_joints_file=None
        self.rebase_keypoint_height=False
        self.show_ground_truth=False
        self.show=True
        self.out_img_root="vis_results"
        # self.device='cpu'#'cuda:0'
        self.device='cuda:0'
        self.kpt_thr=0.3
        self.radius=8
        self.thickness=3



class handKeypoints(threading.Thread):
    def __init__(self,dataDeque,resultDeque,savePath=''):
        super(handKeypoints,self).__init__()
        self.dataDeque=dataDeque
        self.args = argsClass()
        # build the pose model from a config file and a checkpoint file
        self.pose_model = hub.Module(name='hand_pose_localization', use_gpu=True)

        self.runFlag=True
        self.kpt_score_thr=0.2
        self.resultDeque=resultDeque
        self.passFrame=1
    def run(self):
        frameNum=-1
        while self.runFlag:
            # print('dd',len(self.dataDeque))
            if len(self.dataDeque)>0:
                result={}
                fringerTip1= {}
                fringerTip2= {}
                det_results_list=self.dataDeque.popleft()
                frameNum+=1
                if frameNum%self.passFrame==0:
                    # print(' len(self.dataDeque)', len(self.dataDeque))
                    # print(' len(self.dataDeque)', len(self.dataDeque))

                    keypoints,image=  self.process(det_results_list)
                    print('keypoints,keypoints',keypoints)
                    fringerTip1, fringerTip2=self.processTipPoint2Dict(keypoints)
                    print('fp1', fringerTip1,'fp2',fringerTip2)
                else:
                    det_results=det_results_list[0]
                    image = det_results[0]['image']

                image=self.showWrite2D(image, fringerTip1, fringerTip2)
                #add result
                result['fringerTip1']=fringerTip1
                result['fringerTip2']=fringerTip2
                result['image']=image

                self.resultDeque.append(result)
                # print('add result',result)

                #self.show3D(keypoints3D,valid)

    def processTipPoint2Dict(self,result):
        points = []
        fringerTip1 = {}
        fringerTip2 = {}
        points = result[0]
        for index, pp in enumerate(points):
            if index % 4 == 0 and index != 0:
                if pp is not None:
                    fringerTip1[index // 4] = [pp[0],-1*pp[1]]
        if len(result) == 2:
            points = result[1]
            for index, pp in enumerate(points):
                if index % 4 == 0:
                    if pp is not None:
                        fringerTip2[index // 4] =[pp[0],-1*pp[1]]
        return fringerTip1, fringerTip2

    def showWrite2D(self,image, fringerTip1, fringerTip2,writeFlag=False):


        for index,fp in fringerTip1.items():
            if len(fp)>0:
                point=np.array([fp[0],-1*fp[1]],dtype='int16')

                size=8
                color=(0,255-30*index,50+30*index)

                cv2.circle(image,(point),size,color,size)

        for index,fp in fringerTip2.items():
            if len(fp) > 0:
                point=np.array([fp[0],-1*fp[1]],dtype='int16')
                size=8
                color=(255-30*index,0,50+40*index)
                cv2.circle(image,(point),size,color,size)
        # for index,point in enumerate(keypoint2D):
        #     if valid[index]==False:continue
        #     point=np.array(point,dtype='int16')
        #     point[1]*=-1
        #
        #     if index%4==0 and index!=0:
        #         size=8
        #         color=(0,0,255)
        #     else:
        #         size=2
        #         color=(0,255,0)
        #     cv2.circle(image,(point),size,color,size)
        #print('point',point)
        if writeFlag:
            print('write',cv2.imwrite('image.jpg',image))
        return image

    def process(self,det_results_list):
        for i, det_results in enumerate(det_results_list):
            image = det_results[0]['image']
            t1=time.time()
            pose_results = self.pose_model.keypoint_detection(images=[image], visualization=False)
            '''eg:[[None, None, [846, 765], [763, 876], [707, 987], [1373, 598], [1401, 570],
             [1429, 653], [1429, 765], [1152, 542], [1263, 487], [1290, 654], [1262, 792], 
             [1041, 514], [1151, 459], [1123, 625], [1096, 792], [929, 487], [902, 514], [874, 598], None]]'''
            print('predict time',time.time()-t1)

        return pose_results,image


if __name__=='__main__':
    maxLen=10
    dataDeque=deque(maxlen=maxLen)
    resultDeque=deque()
    from ModuleInput import FrameProducer
    mf=FrameProducer(dataDeque,link='pianoSound/hand3.mp4',skipFrame=1)
    hkp=handKeypoints(dataDeque,resultDeque)
    hkp.start()

    mf.start()
    # mf.daemon=True