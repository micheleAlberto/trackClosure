from collections import Counter
from partitionTransfer import dominant
from printOperation import print_merge_operation
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
            track.id:soft_fetch(oracle,track))
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
        
