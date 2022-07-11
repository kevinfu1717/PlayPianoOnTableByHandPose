import json
import numpy as np
def saveJsonFile(infoDict,fileName):
    if len(infoDict)==0:return
    resultDict={}
    resultDict["maker"]= "kevin"
    resultDict["date"]= "2022-07-06"
    resultDict["info"]= [infoDict]
    print('resultDict',type(resultDict),resultDict)
    # with open(fileName+".json", "w") as f:
    #     f.write(json.dumps(resultDict, ensure_ascii=False, indent=4, separators=(',', ':')))
    with open(fileName+".json", 'w') as fp:
        json.dump(resultDict, fp)
    return True

def keypoint3dDatasetTo2dDataset(keypoints3D):
    #3d hand keypoint dataset： 20 is center of hand,tip id is 0,4,8,12,16,shape:[42,4]: [x,z,,y,confidence]
    #2d hand keypoint  dataset：0 is center of hand,tip id is 4,8,12,16,20,shape:[42,2]: [x,y]
    keypoints3D=np.array(keypoints3D)
    keypoints2D=np.zeros((keypoints3D.shape[0],2),dtype='int')
    confidence=np.zeros((keypoints3D.shape[0],1))
    for index in range(keypoints3D.shape[0]):
        if index==20:
            keypoints2D[0,:]=keypoints3D[index,[0,2]]
            confidence[0]=keypoints3D[index,3]
            continue
        elif index==41:
            keypoints2D[21,:]=keypoints3D[index,[0,2]]
            confidence[21]=keypoints3D[index,3]
            continue
        elif index<20:
            newIndex=(index//4)*8+4-index
        elif index<41:
            newIndex=((index-21)//4)*8+46-index
        # print('index',index,newIndex)
        keypoints2D[newIndex,:]=keypoints3D[index,[0,2]]
        confidence[newIndex] = keypoints3D[index,3]
    return keypoints2D,confidence
