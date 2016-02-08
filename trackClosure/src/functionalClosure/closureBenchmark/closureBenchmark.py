from IPython import embed
from random import random
from random import shuffle
from copy import deepcopy
from itertools import combinations, permutations
import numpy as np
from ...closure.transclosure import transitiveclosure as Partition
from ...closure.transclosure import save_tracks
from ...closure.point import point as Track
from ...closure.view import view as View
from ...fromOpenMVG.wrapper import OpenMVG
from ...geometry.epipolarGeometry import EpipolarGeometry
from ...benchmark.benchmark import Benchmark
from ...benchmark.benchmark import save_benchmark
from ...benchmark.benchmark import load_benchmark
from PartitionOutcome import ConnectedComponentTester


def epipolarFilter(gEpG,tollerance):
    def foo(va,vb):
        IJ=(va.id_image,vb.id_image)
        if( IJ in gEpG):
            Ferr=np.dot(vb.hpt() ,np.dot( gEpG[IJ] , va.hpt().T ))
            return np.absolute(Ferr)<tollerance
        else:
            return False
    return foo

def edge_sampling(cc,gEpG,p):
    """
    an edge that respect epipolar constraints is generated between two nodes of
    the connected component with probability p. This is similar to the Erdos
    Graph model.
    """
    return (pair_of_views
    for pair_of_views in all_edges(cc,gEpG)
    if random()<p)

def all_edges(cc,gEpG,r=4.):
    geometric_filter=epipolarFilter(gEpG,r)
    return (
        (va,vb)
        for va,vb in combinations(cc.allViews(),2)
        if geometric_filter(va,vb)
        )




def partitions_from_edges(list_of_pairs):
    pv=[]
    for (va,vb) in list_of_pairs:
        part=Partition()
        part.add_point(Track(-1,[va,vb]))
        pv.append(part)
    return pv


"""
THE FUNCTIONAL SCHEMA OF CLOSURE
closure (part1,part2) -> part1
add_point(part1,track2) (-> part1?)
SynthPoints(track2,tracks1[]) -> tracks[]
merge(track1,track2) -> tracks[]

make_closure(gEpG,radius)
merge_f=make_merge_with_validation(gEpG,radius)
merge_i_f=make_merge_interactive(
        merge_f,
        labda merge_outcome: not merge_outcome.is_correct(),
synth_f=make_synthPoints(merge_i_f)
add_point_f=make_add_point(synth_f)
closure_f=make_closure(add_point_f)
return closure_f
"""

def makeEvalCC(
        closure_functor,
        gEpG,
        benchmark_connected_component,
        oracle,
        permutation_sampling_functor):
    partitionTester=ConnectedComponentTester(
        benchmark_connected_component,
        gEpG,
        oracle)
    def evalCC_functor(cc):
        print 'evaluation'
        cc_id=cc.id
        cc_edges=all_edges(cc,gEpG)
        print 'got edges'
        base_partitions=partitions_from_edges(cc_edges)
        print 'base_partitions'
        sampled_outcomes=[]
        #   ALL PERMUTATIONS
        for shuffled_partition in permutation_sampling_functor(base_partitions,cc):
            print 's',
            partitions=deepcopy(shuffled_partition)
            while len(partitions)>1:
                partitions=[
                    (closure_functor(partitions[i],partitions[i+1])
                        if i+1<len(partitions)
                        else partitions[i]
                    )
                    for i in range(len(partitions))
                    if  i % 2 ==0]
            sampled_outcomes.append(partitions[0])
        print '\n'
        #now it' s time to judge the sampled outcomes
        test_of_sample_outcomes=[partitionTester.test(sample_partition) for sample_partition in sampled_outcomes]
        average_number_of_correct_keypoints=sum( (ts[1] for ts in test_of_sample_outcomes),0.)/len(test_of_sample_outcomes)
        average_track_correctness=sum((ts[0] for ts in test_of_sample_outcomes),0.)/len(test_of_sample_outcomes)
        return (average_track_correctness,average_number_of_correct_keypoints)
    return evalCC_functor

def copy_suffle(arr):
    print 'i am shuffling at len ',len(arr)
    support=range(len(arr))
    shuffle(support)
    print 'shufles'
    arr2=[arr[s] for s in support]
    
    return arr2

permutation_sampling_functors={
    'all'           : lambda base_partitions,cc: permutations(base_partitions),
    'oneEachView'   : lambda base_partitions,cc: (copy_suffle(base_partitions) for _i in cc.allViews() ),
    'oneEachImage'  : lambda base_partitions,cc: (copy_suffle(base_partitions) for _i in cc.views ),
    'ten'           : lambda base_partitions,cc: (copy_suffle(base_partitions) for _i in range(10) ),
    'one'           : lambda base_partitions,cc: (copy_suffle(base_partitions) , )
}

def make_closure_benchmark(closure_functor):
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
        print "[live] ",bm.label , ' with {} connected components '.format(len(bm.CC.points))
        evalCC=makeEvalCC(
            closure_functor,
            gEpG,
            bm.CC, # benchmark_connected_component,
            bm.oracle, # oracle,
            permutation_sampling_functors['ten']) #permutation_sampling_functor)
        cc_performance={}
        for cc_id in bm.CC.points:
            print 'connected component #',cc_id
            cc=bm.CC.points[cc_id]
            cc_performance[cc_id]=evalCC(cc)
            print "{}:\t{}\t{}\t".format(cc_id,cc_performance[cc_id][0],cc_performance[cc_id][1])
        print "\tCC\tcorrectness\tcompleteness"
        for cc_id in cc_performance:
            print "{}:\t{}\t{}\t".format(cc_id,cc_performance[cc_id][0],cc_performance[cc_id][1])
        return cc_performance
    return live_be_cmd





