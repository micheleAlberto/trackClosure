#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import sys

from ..src.closure.transclosure import load_tracks, save_tracks
from ..src.closure.point import point
from ..src.geometry.epipolarGeometry import EpipolarGeometry
from ..src.closure.transclosure import transitiveclosure as Partition

from ..src.functionalClosure.mergeF import hard_merge
from ..src.functionalClosure.synthF import make_synthPoints
from ..src.functionalClosure.addPointF import make_add_point, make_quick_add_point

from ..src.trackAnalysis.greedyDecomposition.decomposition import make_track_greedy_decomposition # (gEpG,radius):

from tqdm import tqdm
def REFINE(cc_file,epipolar_geometry_file,radius,mode,outfile):
    """
    REFINE connected components from a file using multi view epipolar geometry constraints
    ----Arguments:
    (str) cc_file : connected components file
    (str) epipolar_geometry_file: epipolar geometry file
    (flo) radius : threshold for the 3-keypoint prediction error
    (int) mode : keypoint selection method
    (str) refined_file : output connected components file

    modes: 
    0 : First available keypoint
    1 : Best available keypoint (L0)
    2 : Best L2 keypoint
    """
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    CC=load_tracks(cc_file)
    P=Partition()   
    assert(mode in [0,1,2])
    refiner=make_track_greedy_decomposition(gEpG,radius,mode)
    synth = make_synthPoints(hard_merge)
    add_point = make_add_point(synth)
    rejected = 0
    to_refine = 0
    refined= 0
    passed = 0
    for cc in tqdm(CC.points.values()):
        ni=len(cc.views)
        nk=sum((len(cc.views[i]) for i in cc.views))
        if ni==nk and ni==3:
            add_point(P,cc)
            passed+=1
        elif ni>2:
            to_refine+=1
            refined_tracks=refiner(cc)
            for r_cc in refined_tracks:
                refined+=1
                add_point(P,r_cc)
        else :
            rejected+=1
    save_tracks(P,outfile)
    print 'rejected :',rejected
    print 'passed :',passed
    print 'to refine :',to_refine
    print 'refined:', refined
    return
    
if __name__ == "__main__":
    cc_file = sys.argv[1]
    epipolar_geometry_file = sys.argv[2]
    radius = float(sys.argv[3])
    mode = int(sys.argv[4])
    assert(mode in [0,1,2])
    outfile = sys.argv[5]
    REFINE(cc_file,epipolar_geometry_file,radius,mode,outfile)

