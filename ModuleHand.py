skeleton = [[0, 1], [1, 2], [2, 3], [3, 20], [4, 5], [5, 6],
            [6, 7], [7, 20], [8, 9], [9, 10], [10, 11], [11, 20],
            [12, 13], [13, 14], [14, 15], [15, 20], [16, 17],
            [17, 18], [18, 19], [19, 20], [21, 22], [22, 23],
            [23, 24], [24, 41], [25, 26], [26, 27], [27, 28],
            [28, 41], [29, 30], [30, 31], [31, 32], [32, 41],
            [33, 34], [34, 35], [35, 36], [36, 41], [37, 38],
            [38, 39], [39, 40], [40, 41]]

pose_kpt_color = [[14, 128, 250], [14, 128, 250], [14, 128, 250],
                  [14, 128, 250], [80, 127, 255], [80, 127, 255],
                  [80, 127, 255], [80, 127, 255], [71, 99, 255],
                  [71, 99, 255], [71, 99, 255], [71, 99, 255],
                  [0, 36, 255], [0, 36, 255], [0, 36, 255],
                  [0, 36, 255], [0, 0, 230], [0, 0, 230],
                  [0, 0, 230], [0, 0, 230], [0, 0, 139],
                  [237, 149, 100], [237, 149, 100],
                  [237, 149, 100], [237, 149, 100], [230, 128, 77],
                  [230, 128, 77], [230, 128, 77], [230, 128, 77],
                  [255, 144, 30], [255, 144, 30], [255, 144, 30],
                  [255, 144, 30], [153, 151, 0], [153, 151, 0],
                  [153, 151, 0], [153, 151, 0], [255, 151, 13],
                  [255, 151, 13], [255, 151, 13], [255, 151, 13],
                  [103, 37, 8]]

pose_link_color = [[14, 128, 250], [14, 128, 250], [14, 128, 250],
                   [14, 128, 250], [80, 127, 255], [80, 127, 255],
                   [80, 127, 255], [80, 127, 255], [71, 99, 255],
                   [71, 99, 255], [71, 99, 255], [71, 99, 255],
                   [0, 36, 255], [0, 36, 255], [0, 36, 255],
                   [0, 36, 255], [0, 0, 230], [0, 0, 230],
                   [0, 0, 230], [0, 0, 230], [237, 149, 100],
                   [237, 149, 100], [237, 149, 100],
                   [237, 149, 100], [230, 128, 77], [230, 128, 77],
                   [230, 128, 77], [230, 128, 77], [255, 144, 30],
                   [255, 144, 30], [255, 144, 30], [255, 144, 30],
                   [153, 151, 0], [153, 151, 0], [153, 151, 0],
                   [153, 151, 0], [255, 151, 13], [255, 151, 13],
                   [255, 151, 13], [255, 151, 13]]
import os
import os.path as osp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import pickle
# import mmcv
import numpy as np
from collections import deque
import cv2
import json
from mmpose.apis import inference_interhand_3d_model, vis_3d_pose_result
from mmpose.apis.inference import init_pose_model
from mmpose.core import SimpleCamera
# from initParam import pose_link_color,pose_kpt_color,skeleton
import threading
from calTools import saveJsonFile,keypoint3dDatasetTo2dDataset

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
    def __init__(self,dataDeque,resultDeque,savePath='tmp'):
        super(handKeypoints,self).__init__()
        self.dataDeque=dataDeque
        self.args = argsClass()
        # build the pose model from a config file and a checkpoint file
        self.pose_model = init_pose_model(
            self.args.pose_config, self.args.pose_checkpoint, device=self.args.device.lower())
        self.dataset = self.pose_model.cfg.data['test']['type']
        self.runFlag=True
        self.kpt_score_thr=0.2
        self.resultDeque=resultDeque
        self.passFrame=1
        if len(savePath)>0:
            self.savePath=savePath

            self.outpuFlag = True
        else:

            self.outpuFlag = False
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

                    keypoints3D, valid,image=  self.process(det_results_list)
                    if self.outpuFlag:
                        self.write2DPoint(image,keypoints3D,valid)
                    fringerTip1, fringerTip2=self.processPoint(keypoints3D,valid)
                    # print('fp1', fringerTip1,'fp2',fringerTip2)
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

    def processPoint(self,keypoints3D,valid):
        fringerTip1={}
        fringerTip2={}

        x_3d,  z_3d,y_3d = np.split(keypoints3D[:, :3], [1, 2], axis=1)
        # print(y_3d)
        for index,data in enumerate(zip(x_3d,y_3d,z_3d)):

            point=np.array([data[0][0],data[1][0],data[2][0]],dtype='int16')
            if index<21:
                if index%4==0 and index!=20:
                    # print('valid1',valid[index],index)
                    if valid[index] == True:
                        fringerTip1[len(fringerTip1)]=point

            else:
                if ( index-21)%4==0 and index!=41:
                    # print('valid2',valid[index],index)
                    if valid[index] == True:
                        fringerTip1[len(fringerTip1)]=point

        return  fringerTip1,fringerTip2
    def write3DPoint(self,image,keypoints3D,valid):

        x_3d,  z_3d,y_3d = np.split(keypoints3D[:, :3], [1, 2], axis=1)
        print(len(y_3d))
        if len(x_3d)==42:

            pointDict1=pointDict2={}
            Mimage=image.copy()
            for index,data in enumerate(zip(x_3d,y_3d)):
                if valid[index]==False:continue

                point=np.array([int(data[0][0]),int(-1*data[1][0])],dtype='int16')

                if index > 20:
                    pointDict1[index-21]= {'x':int(point[0]),'y':int(point[1])}
                    color=(10*index-210,100,420-10*index)
                else:
                    pointDict2[index]={'x':int(point[0]),'y':int(point[1])}
                    color=(110,255-10*index,10+10*index)
                # 图片 添加的文字 位置 字体 字体大小 字体颜色 字体粗细
                cv2.putText(Mimage, str(index),point, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 3)
            if len(pointDict1)==21:
                timeStamp=str(time.time())
                #source pic
                fileName=self.savePath+'/imageR'+timeStamp
                cv2.imwrite(fileName+'.jpg',image)
                # pic with memo
                fileName2=self.savePath+'/imageR'+timeStamp
                cv2.imwrite(fileName2+'.png',Mimage)
                infoDict={}
                infoDict["bbox"]=[0,0,0,0]
                infoDict["pts"]=pointDict1

                saveJsonFile(infoDict, fileName)
            if  1==0:#len(pointDict2) == 21:
                timeStamp=str(time.time())
                #source pic
                fileName=self.savePath+'/imageL'+timeStamp
                cv2.imwrite(fileName+'.jpg',image)
                # pic with memo
                fileName2=self.savePath+'/imageL'+timeStamp
                cv2.imwrite(fileName2+'.png',Mimage)
                infoDict={}
                infoDict["bbox"]=[0,0,0,0]
                infoDict["pts"]=pointDict2
                saveJsonFile(infoDict, fileName)

    def write2DPoint(self,image,keypoints3D,valid,writeNumBias=21):
        keypoints2D,_=keypoint3dDatasetTo2dDataset(keypoints3D)

        x_3d=keypoints2D[:,0]
        y_3d = keypoints2D[:,1]
        # print(len(y_3d))
        if len(x_3d)==42:

            pointDict1=pointDict2={}
            Mimage=image.copy()
            for index,data in enumerate(zip(x_3d,y_3d)):
                if valid[index]==False:continue

                point=np.array([int(data[0]),int(-1*data[1])],dtype='int16')

                if index > 20:
                    pointDict1[index-21]= {'x':int(point[0]),'y':int(point[1])}
                    color=(10*index-210,100,420-10*index)
                else:
                    pointDict2[index]={'x':int(point[0]),'y':int(point[1])}
                    color=(110,255-10*index,10+10*index)
                # 图片 添加的文字 位置 字体 字体大小 字体颜色 字体粗细
                cv2.putText(Mimage, str(index-writeNumBias),point, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 3)
            if len(pointDict1)==21:
                timeStamp=str(time.time())
                #source pic
                fileName=self.savePath+'/imageR'+timeStamp
                cv2.imwrite(fileName+'.jpg',image)
                # pic with memo
                fileName2=self.savePath+'/imageR'+timeStamp
                cv2.imwrite(fileName2+'.png',Mimage)
                infoDict={}
                infoDict["bbox"]=[0,0,0,0]
                infoDict["pts"]=pointDict1

                saveJsonFile(infoDict, fileName)
            if  1==0:#len(pointDict2) == 21:
                timeStamp=str(time.time())
                #source pic
                fileName=self.savePath+'/imageL'+timeStamp
                cv2.imwrite(fileName+'.jpg',image)
                # pic with memo
                fileName2=self.savePath+'/imageL'+timeStamp
                cv2.imwrite(fileName2+'.png',Mimage)
                infoDict={}
                infoDict["bbox"]=[0,0,0,0]
                infoDict["pts"]=pointDict2
                saveJsonFile(infoDict, fileName)
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
    def show3D(self,keypoints3D,valid):

        fig = plt.figure()
        # ax = fig.add_subplot(1, num_axis, ax_idx, projection='3d')
       # ax = fig.add_subplot(1, projection='3d')

        ax = plt.subplot(111, projection='3d')

        x_3d, y_3d, z_3d = np.split(keypoints3D[:, :3], [1, 2], axis=1)
        # matplotlib uses RGB color in [0, 1] value range
#        _color =  pose_kpt_color[..., ::-1] / 255.
        ax.scatter(
            x_3d[valid],
            y_3d[valid],
            z_3d[valid],
            marker='o',
            color='g',
            # color=_color[valid],
        )
        # print(x_3d[valid],y_3d[valid])
        #
        self.drawLine=True
        if self.drawLine:
            # pose_link_color = np.array(pose_link_color)
            assert len(pose_link_color) == len(skeleton)
            for link, link_color in zip(skeleton, pose_link_color):
                link_indices = [_i for _i in link]
                xs_3d = keypoints3D[link_indices, 0]
                ys_3d = keypoints3D[link_indices, 1]
                zs_3d = keypoints3D[link_indices, 2]
                kpt_score = keypoints3D[link_indices, 3]
                if kpt_score.min() > self.kpt_score_thr:
                    # matplotlib uses RGB color in [0, 1] value range
#                    _color = link_color[::-1] / 255.
                    ax.plot(xs_3d, ys_3d, zs_3d, color='b', zdir='z')
        #


        plt.show()
        img_vis = None
        # convert figure to numpy array
        # fig.tight_layout()
        # fig.canvas.draw()
        # img_w, img_h = fig.canvas.get_width_height()
        # img_vis = np.frombuffer(
        #     fig.canvas.tostring_rgb(), dtype=np.uint8).reshape(img_h, img_w, -1)
        # img_vis = mmcv.rgb2bgr(img_vis)

        plt.close(fig)

    def process(self,det_results_list):
        for i, det_results in enumerate(det_results_list):
            image = det_results[0]['image']
            t1=time.time()
            pose_results = inference_interhand_3d_model(
                self.pose_model, image, det_results, dataset=self.dataset)
            print('predict time',time.time()-t1)
            # Post processing
            pose_results_vis = []


            for idx, res in enumerate(pose_results):

                keypoints_3d = res['keypoints_3d']
                # normalize kpt score
                if keypoints_3d[:, 3].max() > 1:
                    keypoints_3d[:, 3] /= 255

                valid = keypoints_3d[:, 3] >= self.kpt_score_thr
                # get 2D keypoints in pixel space
                res['keypoints'] = keypoints_3d[:, [0, 1, 3]]

                # For model-predicted keypoints, channel 0 and 1 are coordinates
                # in pixel space, and channel 2 is the depth (in mm) relative
                # to root joints.
                # If both camera parameter and absolute depth of root joints are
                # provided, we can transform keypoint to camera space for better
                # visualization.
                camera_param = res['camera_param']
                keypoints_3d_gt = res['keypoints_3d_gt']
                if camera_param is not None and keypoints_3d_gt is not None:
                    # build camera model
                    camera = SimpleCamera(camera_param)
                    # transform gt joints from world space to camera space
                    keypoints_3d_gt[:, :3] = camera.world_to_camera(
                        keypoints_3d_gt[:, :3])

                    # transform relative depth to absolute depth
                    keypoints_3d[:21, 2] += keypoints_3d_gt[20, 2]
                    keypoints_3d[21:, 2] += keypoints_3d_gt[41, 2]

                    # transform keypoints from pixel space to camera space
                    keypoints_3d[:, :3] = camera.pixel_to_camera(
                        keypoints_3d[:, :3])

                # rotate the keypoint to make z-axis correspondent to height
                # for better visualization
                vis_R = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
                keypoints_3d[:, :3] = keypoints_3d[:, :3] @ vis_R
                if keypoints_3d_gt is not None:
                    keypoints_3d_gt[:, :3] = keypoints_3d_gt[:, :3] @ vis_R

                # rebase height (z-axis)
                # if self.args.rebase_keypoint_height:
                #     valid = keypoints_3d[..., 3] > 0
                #     keypoints_3d[..., 2] -= np.min(
                #         keypoints_3d[valid, 2], axis=-1, keepdims=True)
                res['keypoints_3d'] = keypoints_3d
                res['keypoints_3d_gt'] = keypoints_3d_gt

                # Add title
                instance_id = res.get('track_id', idx)
                res['title'] = f'Prediction ({instance_id})'
                pose_results_vis.append(res)


            # print('pose_results_vis______________',pose_results_vis)
            keypoints3D=pose_results_vis[0]['keypoints_3d'][...,[0,1,2,3]]#['keypoints_3d_gt']
           # print('keypoints3D',len(keypoints3D))
        return keypoints3D,valid,image


if __name__=='__main__':
    maxLen=50
    dataDeque=deque(maxlen=maxLen)
    resultDeque=deque()
    from ModuleInput import FrameProducer
    mf=FrameProducer(dataDeque,link='pianoSound/hand6.mp4',skipFrame=1)
    hkp=handKeypoints(dataDeque,resultDeque,savePath='hand6')
    hkp.start()

    mf.start()
    # mf.daemon=True