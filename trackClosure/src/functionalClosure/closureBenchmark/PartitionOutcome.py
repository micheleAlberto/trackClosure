from collections import Counter
from ..mergeBenchmark.partitionTransfer import dominant, soft_fetch
from collections import Counter, namedtuple
from tqdm import tqdm
import numpy as np
from itertools import combinations
import cv2
class ConnectedComponentTester():
    def __init__(self,cc,gEpG,oracle):
        self.cc=cc
        self.gEpG=gEpG
        self.oracle=oracle
    def testPartition(self,part):
        """
        evaluate correctness and completeness of the partition
        returns (corr,compl)
            corr is the average correctness of keypoint labeling
            compl is the number of keypoints that are correctly labeled
        """
        oracles_by_track={
            track.id:soft_fetch(oracle,track)
            for track in part.points.values() }
        dominant_oracle_by_track={
            t_id:dominant(oracles_by_track[t_id]) 
            for t_id,or_list in oracles_by_track}
        counter_oracles_by_track={
            t_id:Counter(oracles_by_track[t_id]) 
            for t_id,or_list in oracles_by_track}
        number_of_correct_oracles_by_track={            
            t_id:counter_oracles_by_track[t_id][dominant_oracle_by_track[t_id]]
            for t_id,or_list in oracles_by_track}
        fraction_of_correct_oracles_by_track={
            t_id:(
                float(number_of_correct_oracles_by_track[t_id])/
                sum(counter_oracles_by_track[t_id]) )
            for t_id,or_list in oracles_by_track}
        correct_keypoints=sum(number_of_correct_oracles_by_track.values())
        average_correctness=sum(fraction_of_correct_oracles_by_track.values())/float(len(fraction_of_correct_oracles_by_track))
        return average_correctness,correct_keypoints
        
ROC_Restult=namedtuple('ROC_result',['TP','FN','FP','TN','IMG'])
class ROC_Tester():
    def __init__(self,cc,gEpG,oracle):
        self.cc=cc
        self.gEpG=gEpG
        self.oracle=oracle
        ground_truth=[v 
            for v in self.cc.allViews() 
            if self.oracle.hasView(v.id_image,v.id_keypoint)]
        self.V=sorted(
            ground_truth, 
            key=lambda v: self.oracle.viewQuery(v.id_image,v.id_keypoint)*10000+v.id_image
            )
        n_kp=len(self.V)
        self.IMG=np.zeros((n_kp,n_kp,3),np.uint8)
        def mark(i, j, value):
            IMG[i,j]+=value
            IMG[j,i]+=value
    def O(self,v):
        return self.oracle.viewQuery(v.id_image,v.id_keypoint)
    def oracle_positive(self,v1,v2):
        return self.O(v1)==self.O(v2)
    def testPartition(self,part):
        """
        evaluate correctness and completeness of the partition
        returns (corr,compl)
            corr is the average correctness of keypoint labeling
            compl is the number of keypoints that are correctly labeled
        """
        P = lambda v: part.viewQuery(v.id_image,v.id_keypoint) if part.hasView(v.id_image,v.id_keypoint) else -1 
        BGR=np.array([[1,0,0],
                      [0,1,0],
                      [0,0,1]],np.uint8)*255
        BLUE,GREEN,RED=BGR
        def positive(v1,v2):
            t1,t2=P(v1),P(v2)
            if t1 != -1 :
                return t1==t2
            return False
        Positive = lambda v1,v2: self.O(v1)==self.O(v2) and self.O(v1) is not -1
        n_kp=len(self.V)
        IMG=np.zeros((n_kp,n_kp,3),np.uint8)
        def mark(i, j, value):
            IMG[i,j]=value
            IMG[j,i]=value
        TP,FP,TN,FN=0,0,0,0
        for iv1,iv2 in tqdm(combinations(enumerate(self.V),2),'ROC evaluation'): 
            i,v1=iv1
            j,v2=iv2   
            if self.oracle_positive(v1,v2):
                if positive(v1,v2):
                    TP+= 1
                    mark(i, j, GREEN)
                else:
                    FN+= 1
                    mark(i, j, BLUE)
            else:
                if positive(v1,v2):
                    FP+= 1
                    mark(i, j, RED)
                else:
                    TN+= 1
        return ROC_Restult(TP,FN,FP,TN,IMG)


    
        
