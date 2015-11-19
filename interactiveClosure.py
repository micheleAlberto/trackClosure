from IPython import embed
import closure.trackclosure.transitiveclosure as Partition
from partitionTransfer import fetch, soft_fetch, partition_transfer, track_is_wrong
    
"""
Correctness:
means not to introduce errors in the computation.
We are introducing errors when 
    there are no errors in the operands and 
    there are errors in the results

Recovering:
means errors in the input are prevented from spreading in the output
we are recovering errors when:
    there are errors in the operands and
    there are no errors in the results

(variant) Partial recover:
    there are less errors in the results than in the full closure results
that is:
    there are errors in the full closure results that are not in the robust 
    results  
    
Completeness:
means not to discard usefull data in the computation
we are discarding usefull data when there are keypoints :
    that are in the operands
    that are not in the results
    that are in same the oracle of a result 
    (that is: keypoints that should be in the results but are not)


Absolute Correctness Evaluation 
goal : understand when we are introducing errors

Relative Correctness Evaluation
goal 1: understand when we are not introducing errors that a full closure would introduce
goal 2: understand when we are introducing errors that a full closure would not introduce
The condition of goal 2 is unsatisfiable

Recover Evaluation
goal : understand when we are correcting errors

correctness Scenario:
add_point_functor RC is Absolutely Correct <=> there are no errors in the operands and 
                                              there are no errors in the filtered results
add_point_functor RC is Relatively Correct <=> there are no errors in the operands and
                                              there are no errors in the filtered results
                                              there are errors in the full closure results
add_point_functor RC is Relatively Correct => Absolutely Correct

errors in the operands:
Completeness Evaluation
goal 1(strong): understand when we are discarding usefull data
goal 2(light): understand when we are discarding usefull data but we still have a correct substitute for the lost information
"""


def per_track_reduction(part_x,track_y,oracle,add_point_functor):
    def per_track_reduction(
        part_x,     #partition
        track_y,    #track to insert
        oracle      #oracle partition
        ):
        assert(len(part_x.points)>0)
        part_z=add_point_functor(part_x,track_y)
        yO=fetch(oracle,track_y)
        """
        Errors in the track operand
        #if len(yO)==0 we don' t kow much about the track because supervised 
            information is not available
        #if len(yO)==1 track_y is a correct track as far as we know !!!
        #if len(yO)>1  track_y is already wrong before the computation !!!
        """
        yX=fetch(part_x,track_y)
        """
        Number of interactions between track and partition
        #if len(yX)==0 track_y is not in the partition, so there is no 
            interaction between the track and the partition
        #if len(yX)==1  track_y match one track in X (one merge)
        #if len(yX)>1  track_y match many track in X (many merges)
        """
        yZ=fetch(part_z,track_y)
        """
        MERGE/SPLIT 
        #if len(yZ)==0 track_y has been lost in the operation
        #if len(yZ)==1 track_y has passed undivided the operation (only MERGE)
        #if len(yZ)>1  track_y has been split in the operation (at least one split SPLIT)
        """
        yXO=partition_transfer(oracle,part_x,yX)
        """
        yXO are oracles (ids) of the keypoints of X that are going to be 
        related to track_y by full closure
        #if len(yXO)==0 track_y mutuals in part_x are not described by oracles
        #if len(yXO)==1 track_y mutuals are consistent in oracles => correct results
        #if len(yXO)>1  track_y mutuals are NOT consistent in oracles => error in results
        """
        yZO=partition_transfer(oracle,part_z,yZ)
        """
        yZO are oracles (ids) of the keypoints of Z that are related to track_y 
            that is yZO are the oracles of the results
        #if len(yZO)==0 track_y mutuals in part_x are not described by oracles
        #if len(yZO)==1 track_y mutuals are consistent in oracles
        #if len(yZO)>1  track_y mutuals are NOT consistent in oracles
        """
        """
        correct operands:
            len(yXO)<=1 and len(yO)<=1
        correct operands and mutually consistent
            len(set(yO+yXO))<=1
        correct result
        
        in a perfect world:
            oracle of results == oracle of operands
                yZO     ==  yXO == yO
        yZO are oracles of results
        yXO are oracles of operands from partition part_X
        yO  are oracles of operand track_y
            
        """
    return foo

    
