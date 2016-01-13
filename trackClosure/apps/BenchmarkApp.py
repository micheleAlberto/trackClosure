#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import sys

from ..src.closure.transclosure import load_tracks
from ..src.closure.point import point
from ..src.benchmark.benchmark import Benchmark
from ..src.benchmark.benchmark import save_benchmark
from ..src.benchmark.benchmark import load_benchmark
from ..src.benchmark.OracleGui import oracle_gui
from ..src.geometry.epipolarGeometry import EpipolarGeometry
from ..src.fromOpenMVG.wrapper import OpenMVG

def ADD_CC(
        benchmark_file,
        epipolar_geometry_file,
        image_dir,
        omvg_dir,
        cc_track_file,
        cc_ids):
    """
    Add a connected component to a benchmark file, use a GUI to allow user to 
    separate tracks in the same connected components to define an oracle.
    ----Arguments:
    (str) benchmark_file 
    (str) epipolar_geometry_file
    (str) image_dir : directory that hosts the images
    (str) omvg_dir : directory that hosts openmvg data
    (str) cc_track_file : connected components file to open
    (int[]) cc_ids : list of connected components id to add
    ----GUI commands
    Each different oracle track is colored differently (up to 8 colors!)
    Keypoints of an oracle tracks are colored accordingly;
    Unassigned keypoints are drawn in black;
    Epipolar lines, if drawn, use the color of the track-oracle of the
    keypoint that project them.

    left-right : change image
    up-down : change active oracle
    n : new oracle
    d : delete active oracle
    double-click : assign keypoint to active oracle track
    right-click : detach keypoint from oracle
    e : toggle epilines
    q: quit
    
    """
    omvg=OpenMVG()
    omvg.set_image_dir(image_dir)
    omvg.set_feature_dir(omvg_dir)
    image_id2name,name2image_id = omvg.loadImageMap()
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    CC=load_tracks(cc_track_file)
    print "connected components file: ",cc_track_file, " id:",cc_ids
    bm=load_benchmark(benchmark_file)
    print bm
    print "benchmark file: ",benchmark_file
    for cc_id in cc_ids:
        cc=CC.points[cc_id]
        print cc
        gui=oracle_gui(lambda i:image_dir+image_id2name[i],gEpG,cc)
        gui.play()
        oracle_list=gui.get_oracles()
        bm.addConnectedComponent(cc)
        for o in oracle_list:
            bm.addOracle(o)
        print "saving ",benchmark_file," :",
        save_benchmark(bm, benchmark_file)
        print "DONE"

def EDIT_CC(
        benchmark_file,
        epipolar_geometry_file,
        image_dir,
        omvg_dir,
        cc_id):
    """
    Edit a connected component in a benchmark file, use a GUI to allow user to 
    separate tracks in the same connected components to re-define oracles.
    ----Arguments:
    (str) benchmark_file 
    (str) epipolar_geometry_file
    (str) image_dir : directory that hosts the images
    (str) omvg_dir : directory that hosts openmvg data
    (int) cc_id : connected component id to edit
    ----GUI commands
    Each different oracle track is colored differently (up to 8 colors!)
    Keypoints of an oracle tracks are colored accordingly;
    Unassigned keypoints are drawn in black;
    Epipolar lines, if drawn, use the color of the track-oracle of the
    keypoint that project them.

    left-right : change image
    up-down : change active oracle
    n : new oracle
    d : delete active oracle
    double-click : assign keypoint to active oracle track
    right-click : detach keypoint from oracle
    e : toggle epilines
    q: quit
    """
    omvg=OpenMVG()
    omvg.set_image_dir(image_dir)
    omvg.set_feature_dir(omvg_dir)
    image_id2name,name2image_id = omvg.loadImageMap()
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    bm=load_benchmark(benchmark_file)
    print "benchmark file: ",benchmark_file
    cc=bm.CC.points[cc_id]
    o_ids=bm.cc2oracles(cc_id)
    print cc
    gui=oracle_gui(lambda i:image_dir+image_id2name[i],gEpG,cc)
    for o_id in o_ids:
        o=bm.oracle.points[o_id]
        gui.add_oracle(o)
    gui.play()
    oracle_list=gui.get_oracles()
    for o_id in o_ids:
        bm.oracle.removePoint(o_id)
    for o in oracle_list:
        bm.addOracle(o)
    print "saving ",benchmark_file," :",
    save_benchmark(bm, benchmark_file)
    print "DONE"

def TEST_CC(
        benchmark_file,
        epipolar_geometry_file,
        image_dir,
        omvg_dir,
        R):
    from ..src.functionalClosure.benchmarkClosureF import benchmark_test   
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    bt=benchmark_test(gEpG,R)
    bt(     benchmark_file,
            epipolar_geometry_file,
            image_dir,
            omvg_dir)
    bm=load_benchmark(benchmark_file)
    
def __ADD_CC_T(
        benchmark_file,
        epipolar_geometry_file,
        image_dir,
        omvg_dir,
        cc_track_file,
        track_file,
        t_ids):
    omvg=OpenMVG()
    omvg.set_image_dir(image_dir)
    omvg.set_feature_dir(omvg_dir)
    image_id2name,name2image_id = omvg.loadImageMap()
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    CC=load_tracks(cc_track_file)
    print "connected components file: ",cc_track_file
    T=load_tracks(track_file)
    print "track file: ",track_file, " id:",t_ids
    bm=load_benchmark(benchmark_file)
    print "benchmark file: ",benchmark_file
    for t_id in t_ids:
        t=T.points[t_id]
        cc_ids=CC.viewGroupQuery(t.views)
        assert(len(cc_ids)==1)
        cc=CC.points[cc_ids[0]]
        print cc
        gui=oracle_gui(lambda i:image_dir+image_id2name[i],gEpG,cc)
        gui.play()
        oracle_list=gui.get_oracles()
        bm.addConnectedComponent(cc)
        for o in oracle_list:
            bm.addOracle(o)
        print "saving ",benchmark_file," :",
        save_benchmark(bm, benchmark_file)
        print " DONE"

def NEW(benchmark_file,benchmark_label):
    """
    Create a new benchmark file
    ----Arguments
    (str) benchmark_file
    (str) label
    """
    bm=Benchmark(benchmark_label)
    save_benchmark(bm, benchmark_file)

def PRINT(benchmark_file):
    """
    Print a benchmark file as text
    Will show connected components and relative oracles
    ----Arguments
    (str) benchmark_file
    """
    bm=load_benchmark(benchmark_file)
    print "benchmark file: ",benchmark_file
    print bm





def main(argv):
    if '--addcc' in argv[1]:
        benchmark_file=argv[2]
        epipolar_file=argv[3]
        cc_track_file=argv[4]
        image_dir=argv[5]
        omvg_dir=argv[6]
        cc_ids=[]
        for cc_id_str in argv[7:]:
            try :
                cc_ids.append(int(cc_id_str))
            except:
                print "can't understand track id ",cc_id_str
                pass
        ADD_CC(
             benchmark_file,    #benchmark_file,
             epipolar_file,     #epipolar_geometry_file,
             image_dir,         #image_dir,
             omvg_dir,          #omvg_dir,
             cc_track_file,     #cc_track_file,
             cc_ids)            #cc_ids)

    if '--addt'  in argv[1]:
        benchmark_file=argv[2]
        epipolar_file=argv[3]
        cc_track_file=argv[4]
        image_dir=argv[5]
        omvg_dir=argv[6]
        track_file=argv[7]
        t_ids=[]
        for t_id_str in argv[8:]:
            try :
                t_ids.append(int(t_id_str))
            except:
                print "can't understand track id ",t_id_str
                pass
        ADD_CC_T(
            benchmark_file,
            epipolar_geometry_file,
            image_dir,
            omvg_dir,
            cc_track_file,
            track_file,
            t_ids)
    if "--new" in argv[1]:
        benchmark_file=argv[2]
        label=argv[3]
        NEW(benchmark_file,label)
    if "--print" in argv[1]:
        benchmark_file=argv[2]
        PRINT( benchmark_file)
    if "--help" in argv[1]:
        HELP(argv[0])
    if "--edit" in argv[1]:
        benchmark_file=argv[2]
        epipolar_file=argv[3]
        image_dir=argv[4]
        omvg_dir=argv[5]
        cc_id=int(argv[6])
        EDIT(benchmark_file,
            epipolar_file,
            image_dir,
            omvg_dir,
            cc_id)


addt_help="""--addt benchmark_file epipolar_file connected_component_file image_directory openMVG_directory track_file list_of_track_ids

add the connected components of the tracks of track_file identified by list_of_track_ids to benchmark_file
for each connected component oracles are to be defined with a point and click GUI

Exaple:
--addt benchmark.be vg.epg cc_tracks.pk images/ matches/ robust_tracks.pk 8983 10393 29977 30134 34933 17783"""

addcc_help="""--addcc benchmark_file epipolar_file connected_component_file image_directory openMVG_directory list_of_cc_ids

add the connected components from connected_component_file identified by list_of_cc_ids to benchmark_file
for each connected component oracles are to be defined with a point and click GUI

Exaple:
--addcc benchmark.be vg.epg cc_tracks.pk images/ matches/  8983 10393 29977 30134 34933 17783"""

new_help="""--new benchmark_file label

Create a new, empty, benchmark file with label as label

Exaple:
--new benchmark.be soft_benchmark"""

print_help="""--print benchmark_file

print the content of the benchmark file

Exaple:
--new benchmark.be soft_benchmark"""

def HELP(progname):
    print progname
    cmds=[NEW, PRINT, ADD_CC, EDIT_CC]
    for f in cmds:
        print f.__name__
        print f.__doc__

if __name__ == "__main__":
    main(sys.argv)
