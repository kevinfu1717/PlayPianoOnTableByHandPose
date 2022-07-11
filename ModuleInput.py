import threading
import cv2
import time
def packageData(det_results,pic):
    det_result = {
        'image': pic,
        'image_name': 'img',
        'bbox': [int(pic.shape[1] / 10), int(pic.shape[0] / 10), int(pic.shape[1] / 10 * 8),
                 int(pic.shape[0] / 10 * 8)],  # bbox format is 'xywh'
        'camera_param': None,
        'keypoints_3d_gt': None
    }
    #
    det_results.append([det_result])
    return  det_results
class FrameProducer(threading.Thread):
    """docstring for ClassName"""

    def __init__(self, frame_queue, width=800,height=600,link='',skipFrame=2 ):
        super(FrameProducer, self).__init__()
        self.frame_queue = frame_queue
        self.skipFrame=skipFrame
        self.link = link
        self.width=width
        self.height=height
        self.runFlag=True
        self.fps=0
        print('input producer fps',self.fps)
    def addQueue(self,pic):
        pic=cv2.resize(pic,(self.width,self.height))
        self.frameIndex+=1
        if self.frameIndex%self.skipFrame==0:
            det_results=[]
            det_results=packageData(det_results, pic)
            # print('det_results',det_results[0])
            self.frame_queue.append(det_results)
    def run(self):
        print('in producer')
        self.frameIndex=-1
        self.cap = cv2.VideoCapture(self.link)
        if isinstance(self.link, str):#video
            self.fps = int(round(self.cap.get(cv2.CAP_PROP_FPS)))
        #        cap = cv2.VideoCapture('rtsp://admin:passwd@10.130.10.111:554/MPEG-4/ch1/main/av_stream')
        print(self.link, ' == ', self.cap.isOpened())
        while self.runFlag:

            ret, image = self.cap.read()
            #            print('get frame = ',ret,image.shape)
            if (ret == True):
                if isinstance (self.link,str) and self.fps==0:#video
                    self.fps = int(round(self.cap.get(cv2.CAP_PROP_FPS)))
                self.addQueue(image)

            else:
                try:
                    self.cap = cv2.VideoCapture(self.link)
                    if (ret == True):
                        self.addQueue(image)
                    else:
                        print('frame process:sleep time to wait')
                        time.sleep(0.1)
                except Exception as e:
                    print('image 2nd read error-> end', e)
                    time.sleep(1)
                    self.cap = cv2.VideoCapture(self.link)
                    time.sleep(0.1)
                # continue
        print('frame producer end')
if __name__=='__main__':
    from collections import deque
    dataDeque = deque()
    link='./pianoSound/hand1.mp4'
    # link=0
    # link='rtsp://admin:admin@192.168.18.44:554/stream1'
    producer = FrameProducer(dataDeque, link)
    producer.start()

    producer.daemon = True