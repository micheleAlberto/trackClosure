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
from PartitionOutcome import ROC_Tester
from ..mergeF import hard_merge
from ..synthF import make_synthPoints # (merge_points_functor)    
from ..addPointF import make_add_point # (SynthPoints_functor)
import cv2
from ...trackAnalysis.greedyDecomposition.decomposition import make_track_greedy_decomposition, decomposition_tuner
from collections import namedtuple
from random import choice
OP_fields=['method','cc','MAX_COS','R','TP','FN','FP','TN']
OP = namedtuple('operating_point',OP_fields)
def make_receiver_operating_point_csv(name):
    f=open(name+'.csv','w')
    f.write( ','.join(OP_fields) +'\n')
    return f

def write_OP(method,cc_id,MAX_COS,R,roc,f):
    op = OP(method,cc_id,MAX_COS,R,roc.TP,roc.FN,roc.FP,roc.TN)
    f.write( ', '.join(map(str,op)) +'\n')

def omvg_refinement(cc):
    t=Track(0,[choice(V) for V in cc.views.values()])
    return t

methods={0:'first',1:'best',2:'short'}
"""
def roc_of_a_benchmark(
            benchmark_file,
            epipolar_geometry_file,
            image_dir,
            omvg_dir):
        omvg=OpenMVG()
        omvg.set_image_dir(image_dir)
        omvg.set_feature_dir(omvg_dir)
        image_id2name,name2image_id = omvg.loadImageMap()
        gEpG=EpipolarGeometry.load(epipolar_geometry_file)
        print "[live] benchmark file: ",benchmark_file
        bm=load_benchmark(benchmark_file)
        print "[ROC] ",bm.label , ' with {} connected components '.format(len(bm.CC.points))
        synth = make_synthPoints(hard_merge)
        add_point = make_add_point(synth)
        f=make_receiver_operating_point_csv('roc')
        for cc_id in bm.CC.points:
            cc=bm.CC.points[cc_id]
            roc=ROC_Tester(cc,gEpG,bm.oracle)
            refiner_tuner=decomposition_tuner(gEpG,cc)
            for R in np.logspace(1.5,3.,500):
                for method in methods:
                    print "Testing CC#",cc_id," with R ",R, ' and method ',method
                    refined_tracks = refiner_tuner.solve_for(R,1.,method)
                    part=Partition()
                    for track in refined_tracks:
                        add_point(part,track)
                    print "Evaluation"
                    roc_result=roc.testPartition(part)
                    write_OP(methods[method],cc_id,1.,R,roc_result,f)
                    f.flush()
                    cv2.imwrite('cc1/{}R{:05.0f}m{}.bmp'.format(cc_id,R,method),roc_result.IMG)
                    total=roc_result.TP+roc_result.FP+roc_result.TN+roc_result.FN+0.0
                    print 'TP:',roc_result.TP
                    print 'FP:',roc_result.FP
                    print 'TN:',roc_result.TN
                    print 'FN:',roc_result.FN
                    print 'accuracy:',(roc_result.TP+roc_result.TN)/(total) 
                    print 'sensitivity:',roc_result.TP/(roc_result.TP+roc_result.FN+0.0) 
                    print 'false positive rate:',(roc_result.FP)/(roc_result.FP+roc_result.TN+0.0) 
                    print 'precision:',roc_result.TP/(roc_result.TP+roc_result.FP+0.0)
            for trial in range(50):
                part=Partition()
                add_point(part,omvg_refinement(cc))
                roc_result=roc.testPartition(part)
                write_OP('omvg',cc_id,trial,roc_result,f)
        f.close() 
"""
def roc_of_a_benchmark(
            benchmark_file,
            epipolar_geometry_file,
            image_dir,
            omvg_dir):
        omvg=OpenMVG()
        omvg.set_image_dir(image_dir)
        omvg.set_feature_dir(omvg_dir)
        image_id2name,name2image_id = omvg.loadImageMap()
        gEpG=EpipolarGeometry.load(epipolar_geometry_file)
        print "[live] benchmark file: ",benchmark_file
        bm=load_benchmark(benchmark_file)
        print "[ROC] ",bm.label , ' with {} connected components '.format(len(bm.CC.points))
        synth = make_synthPoints(hard_merge)
        add_point = make_add_point(synth)
        f=make_receiver_operating_point_csv('roc')
        for cc_id in bm.CC.points:
            cc=bm.CC.points[cc_id]
            roc=ROC_Tester(cc,gEpG,bm.oracle)
            refiner_tuner=decomposition_tuner(gEpG,cc)
            for MAX_COS in 1-np.logspace(-8,-1,8):
              for R in np.logspace(1,4,80):
                for method in methods:
                    print "Testing CC#",cc_id," with R ",R, ' and method ',method
                    refined_tracks = refiner_tuner.solve_for(R,MAX_COS,method)
                    part=Partition()
                    for track in refined_tracks:
                        add_point(part,track)
                    print "Evaluation"
                    roc_result=roc.testPartition(part)
                    write_OP(methods[method],cc_id,MAX_COS,R,roc_result,f)
                    f.flush()
                    image_name='cc1/{}m{}COS{:05.0f}R{:05.0f}.bmp'.format(
                        cc_id,
                        method,
                        float(np.degrees(np.arccos(MAX_COS))),
                        R)
                    cv2.imwrite(image_name,roc_result.IMG)
                    total=roc_result.TP+roc_result.FP+roc_result.TN+roc_result.FN+0.0
                    print 'TP:',roc_result.TP
                    print 'FP:',roc_result.FP
                    print 'TN:',roc_result.TN
                    print 'FN:',roc_result.FN
                    print 'accuracy:',(roc_result.TP+roc_result.TN)/(total) 
                    print 'sensitivity:',roc_result.TP/(roc_result.TP+roc_result.FN+0.0) 
                    print 'false positive rate:',(roc_result.FP)/(roc_result.FP+roc_result.TN+0.0) 
                    print 'precision:',roc_result.TP/(roc_result.TP+roc_result.FP+0.0)
            for trial in range(50):
                part=Partition()
                add_point(part,omvg_refinement(cc))
                roc_result=roc.testPartition(part)
                write_OP('omvg',cc_id,1.,trial,roc_result,f)
        f.close() 
