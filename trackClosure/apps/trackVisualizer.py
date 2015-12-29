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

from ..src.trackvis import trackvis as vis
#find getIMG

        right_key=1113939%256
        left_key=1113937%256
        up_key=1113938%256
        down_key=1113940%256
        new_key=1048686%256 #n
        del_key=1048676%256 #d
        toggle_label=1048684%256 #l
        toggle_epilines=1048677%256 #e
        quit_key= 1048689%256 #q

def visualize(
        image_dir,
        cc_track_file,
        epipolar_geometry_file,
        cc_ids):
    omvg=OpenMVG()
    omvg.set_image_dir(image_dir)
    omvg.set_feature_dir("data")
    image_id2name,name2image_id = omvg.loadImageMap()
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    CC=load_tracks(cc_track_file)
    print "connected components file: ",cc_track_file, " id:",cc_ids
    for cc_id in cc_ids:
        cc=CC.points[cc_id]
        visualize_cc(cc, gEpg, image_id2name)

def shift_left(l):
    return l[1:]+[l[0]]

def shift_right(l):
    return [l[-1]]+l[:-1]

def draw_kps(IM, V,scale):
     #draw all keypoints with color ORACLE2COLOR[VIEW2ORACLE[VIEW]]
     for v in V:
        v_id = (v.id_image,v.id_keypoint)
        color = vis.BLUE
        vis.drawView(IM,v,color=color,img_scale=scale)
    return IM

def draw_epiline(IM, im, cc, gEpG,scale):
    epipolarGeometries=vis.filterEpG(gEpG, cc.views)
    for im_id in cc.views:
        if (im_id is not im) 
        and (im_id,im) in epipolarGeometries):
            F=epipolarGeometries[(im_id,im)]
            for v in cc.views[im_id]:
                v_id=v.key()
                vis.drawEpiline(IM,F,v,color=vis.BLUE,label=True,img_scale=scale)


def visualize_cc(cc, gEpg, image_id2name,scale):
    I = {im_id:vis.getIMG(image_id2name[im_id]) for im_id in cc.views}
    native_image_height,native_image_width,=I.values()[0].shape[0:2]
    img_size=(target_width,int(native_image_height/scale))
    I = {im_id:cv2.resize(IM,img_size) for im_id, IM in I.iteritems()}
    I = {im_id:draw_epilines(IM, cc, gEpG,scale) for im_id, IM in I.iteritems()}
    I = {im_id:draw_kps(IM, cc.views[im_id],scale) for im_id, IM in I.iteritems()}
    cv2.namedWindow(str(cc.id))
    key = None
    redraw = True
    image_indexes = sorted(I.keys())
    while key is not quit_key:
        if redraw:
            images = [I[i] for i in image_indexes[:3]]
            redraw=False
            GAL=imgallery(images,show=False)
            cv2.imshow(str(cc.id),GAL)
        key=cv2.waitKey(20)%256
        if key==right_key:
            image_indexes=shift_right(image_indexes)
            redraw=True
        elif key=left_key:
            image_indexes=shift_left(image_indexes)
            redraw=True

def main(argv):
    if len(argv)<5:
        print """
    Track Visualization
    how to use:
    trackVis image_directory cc_track_file epipolar_geometry_file cc_id1 [cc_id_n]
    es:
    trackVis dataset data/cc.pk data/matches.epg 78493 21344 3433 7545
    """
    visualize(
        argv[1], # image_dir,
        argv[2], # cc_track_file,
        argv[3], # epipolar_geometry_file,
        argv[4:]) # cc_ids)

if __name__ == "__main__":
    main(sys.argv)



