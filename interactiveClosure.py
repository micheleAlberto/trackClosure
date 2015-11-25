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

def epipolarFilter(gEpG,tollerance):
    def foo(va,vb):
        IJ=(va.id_image,vb.id_image)
        if( IJ in gEpG):
            Ferr=np.dot(vb.hpt() ,np.dot( gEpG[IJ] , va.hpt().T ))
            return np.absolute(Ferr)<tollerance
        else:
            return False
    return foo
from random import random
from itertools import combinations, permutations
def edge_sampling(cc,gEpG,p):
    return (pair_of_views
    for pair_of_views in all_edges(cc,gEpG)
    if random()<p)

def all_edges(cc,gEpG):
    geometric_filter=epipolarFilter(gEpG,4.)
    return ( 
        (va,vb)
        for va,vb in combinations(cc.allViews,2)
        if geometric_filter(va,vb)
        )
from closure.transclosure import transitiveclosure as Partition
from closure.transclosure import save_tracks
from closure.point import point as Track
from closure.point import view as View

def partitions_from_edges(list_of_pairs):
    pv=[]
    for (va,vb) in list_of_pairs:
        part=Partition()
        part.add_point(Track(-1,[v0,v1]))
        pv.append(part)
    return pv
        

from copy import deepcopy
from random import shuffle

from PartitionOutcome import ConnectedComponentTester
#commands to be used inside BenchmarkApp.py
def live_be_cmd(
        benchmark_file,
        epipolar_geometry_file,
        image_dir,
        omvg_dir):
    """
live benchmark_file epipolar_geometry_file image_directory omvg_dir
    
*   run an oracle based tracking benchmark
*   For every connected components of the benchmark many edge permutations are 
    simulated.
*   An edge permutation is a permutation of the list of edges that are 
    observable for the connected components.
*   An edge is a match between 2 keypoints of a single connected component, 
    validated by the provided epipolar geometries.
*   For each sampled edge permutations the merging process is performed and
    validated against the oracle
*   For each connected component a performance profile is returned as a
    dictionary value mapped by the connected component identifier
*   a performance profile is a pair of floats : correctness and completeness
*   correctness is the probability that tracks produced by the merge process are
    correct 
*   a track is correct if all the keypoint of the track belong to the same oracle
*   completeness is the average number of keypoints correctly labeled in the cc.
*   a keypoint is correctly labeled if its oracle is the same as the (relative)
    majority of the keypoints of the track  
    """
    omvg=OpenMVG()
    omvg.set_image_dir(image_dir)
    omvg.set_feature_dir(omvg_dir)
    image_id2name,name2image_id = omvg.loadImageMap()
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    print "[live] benchmark file: ",benchmark_file
    bm=load_benchmark(benchmark_file)
    print "[live] ",bm.label , ' with {} connected components '.format(len(bm.cc.points))
    partitionTester=ConnectedComponentTester(bm.cc,gEpG,bm.oracle)
    cc_performance={}
    for cc_id in bm.cc.points:
        print 'connected component #',cc_id
        cc=bm.cc.points[cc_id]
        cc_edges=all_edges(cc,gEpG)
        base_partitions=partitions_from_edges(cc_edges)
        sampled_outcomes=[]
        #   ALL PERMUTATIONS
        for shuffled_partition in permutations(base_partitions):
        #   1 RANDOM PERMUTATION PER KEYPOINT
        #for shuffled_partition in (shuffle(base_partitions) for _i in cc.allViews() ):
        #   10 RANDOM PERMUTATIONS
        #for shuffled_partition in (shuffle(base_partitions) for _i in range(10) ):
        #   1 RANDOM PERMUTATION
        #for shuffled_partition in (shuffle(base_partitions), ):
            partitions=deepcopy(shuffled_partition)
            while len(partitions)>1:
                partitions=[
                    (closure(partitions[i],partitions[i+1])
                        if i+1<len(partitions)
                        else partitions[i]
                    )
                    for i in range(len(partitions))
                    if  i % 2 ==0]
            sampled_outcomes.append(partitions[0])
        #now it' s time to judge the sampled outcomes
        test_of_sample_outcomes=[partitionTester.test(sample_partition) for sample_partition in sampled_outcomes]
        average_number_of_correct_keypoints=sum( (ts[1] for ts in test_of_sample_outcomes),0.)/len(test_of_sample_outcomes)
        average_track_correctness=sum((ts[0] for ts in test_of_sample_outcomes),0.)/len(test_of_sample_outcomes)
        cc_performance[cc_id]=(average_track_correctness,average_number_of_correct_keypoints)
        print "{}:\t{}\t{}\t".format(cc_id,cc_performance[cc_id][0],cc_performance[cc_id][1])
    print "\tCC\tcorrectness\tcompleteness"
    for cc_id in cc_performance:
        print "{}:\t{}\t{}\t".format(cc_id,cc_performance[cc_id][0],cc_performance[cc_id][1])
    return cc_performance
                

#TODO:
"""
costruire closure
    closure(partitions[i],partitions[i+1])->part
costruire la valutazione finale delle operazioni sul cc
    final(partitions[0]) -> bho
definire se e come permutare i lati dei componenti connessi
"""

