import cv2
import time
import  threading
class makeFrame(threading.Thread):
    def __init__(self,dataDeque,link=''):
        super(makeFrame,self).__init__()
        self.dataDeque=dataDeque
        imagePathList=['../tests/data/interhand2.6m/fringer\\30.jpg',
                       '../tests/data/interhand2.6m/fringer\\31.jpg',
                       '../tests/data/interhand2.6m/fringer\\32.jpg',
                       '../tests/data/interhand2.6m/fringer\\33.jpg',
                       '../tests/data/interhand2.6m/fringer\\34.jpg',
                       '../tests/data/interhand2.6m/fringer\\35.jpg']

        self.picList=[]
        for imagePath in imagePathList:
            self.picList.append(cv2.imread(imagePath))
        self.runFlag=True
        self.link=link
        if len(link)>0:
            self.cap=cv2.VideoCapture(self.link)
            print('asdf')
        else:
            self.cap=None
    def run(self):
        while self.runFlag:
            self.videoPic()
            #self.testPic()
    def videoPic(self):
        det_results=[]
        ret,pic=self.cap.read()
        print('ret',ret)
        if ret==True:
            #init param
            det_result = {
                'image':pic,
                'image_name': self.link,
                'bbox': [int(pic.shape[1]/10),int(pic.shape[0]/10),int(pic.shape[1]/10*8),int(pic.shape[0]/10*8)],  # bbox format is 'xywh'
                'camera_param': None,
                'keypoints_3d_gt': None
            }
            #
            det_results.append([det_result])
        return det_results

    def testPic(self):
        time.sleep(0.05)

        det_results_list = self.addFrame()
        self.dataDeque.append(det_results_list)
    def addFrame(self):


        det_results=[]

        for pic in self.picList:

            #init param
            det_result = {
                'image':pic,
                'image_name': 'imagePath',
                'bbox': [int(pic.shape[1]/10),int(pic.shape[0]/10),int(pic.shape[1]/10*8),int(pic.shape[0]/10*8)],  # bbox format is 'xywh'
                'camera_param': None,
                'keypoints_3d_gt': None
            }
            #
            det_results.append([det_result])
        return det_results
if __name__=='__main__':
    from collections import deque
    dataDeque=deque()
    mf = makeFrame(dataDeque, link='0')
    mf.start()

