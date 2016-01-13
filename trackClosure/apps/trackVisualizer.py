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
from ..src.partitionAnalysis.partitionAnalisys import most_k_tracks
    #(partition,n, key=lambda t:len(t.views)):
from ..src.trackvis import trackvis as vis
from ..src.trackvis.cvkeys import (
    right_key, left_key,
    pag_up_key, pag_down_key,
    e_key, s_key, t_key,q_key)
from ..src.trackvis.cvkeys import get_key
from time import clock

quit_key= q_key
scale_up_key=pag_up_key
scale_down_key=pag_down_key
epiline_toggle=e_key

def VISUALIZE(
        image_dir,
        cc_track_file,
        epipolar_geometry_file,
        cc_ids,
        scale):
    """
    Visualize a list of tracks from a file.
    ----Arguments
    (str) image_dir : directory that hosts the images
    (str) cc_track_file : the partition file 
    (str) epipolar_geometry_file : the epipolar geometry file
    (int []) cc_ids : the list of tracks to visualize
    (float) scale : divisor to scale the image visualization
    ----GUI commands
    q : quit the current image, open the next one
    right-left : shift images
    1,2,3,4,5,6: set the number of images to display
    e : toggle epilines
    t : toggle image label
    page-up,page-down: scale images up or down
    s : save image; the file will be named after the connected components id
    """
    omvg=OpenMVG()
    omvg.set_image_dir(image_dir)
    omvg.set_feature_dir("data")
    image_id2name,name2image_id = omvg.loadImageMap()
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    CC=load_tracks(cc_track_file)
    print "connected components file: ",cc_track_file, " id:",cc_ids
    for cc_id in cc_ids:
        cc=CC.points[cc_id]
        print cc
        visualize_cc(
            cc, 
            gEpG, 
            {image_id:
                image_dir+image_id2name[image_id] 
                for image_id in image_id2name},
            scale)

def VISUALIZE_K(
        image_dir,
        cc_track_file,
        epipolar_geometry_file,
        k,
        scale):
    """
    Visualize k most observed tracks.
    ----Arguments
    (str) image_dir : directory that hosts the images
    (str) cc_track_file : the partition file 
    (str) epipolar_geometry_file : the epipolar geometry file
    (int) k : the number of track to visualize
    (float) scale : divisor to scale the image visualization
    ----GUI commands
    q : quit the current image, open the next one
    right-left : shift images
    1,2,3,4,5,6: set the number of images to display
    e : toggle epilines
    t : toggle image label
    page-up,page-down: scale images up or down
    s : save image; the file will be named after the connected components id
    """
    c0 = clock()
    omvg=OpenMVG()
    omvg.set_image_dir(image_dir)
    omvg.set_feature_dir("data")
    image_id2name,name2image_id = omvg.loadImageMap()
    c_omvg=clock()
    print 'openmvg : OK [{}]'.format(c_omvg-c0)
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    c_gepg=clock()
    print 'epipolar geometries : OK [{}, {}]'.format(len(gEpG),c_gepg-c_omvg)
    CC=load_tracks(cc_track_file)
    c_cc=clock()
    print 'tracks : OK [{}, {}]'.format(len(CC.points),c_cc-c_gepg)
    cc_ids=most_k_tracks(CC,k)
    print "connected components file: ",cc_track_file, " id:",cc_ids
    for cc_id in cc_ids:
        cc=CC.points[cc_id]
        print cc
        visualize_cc(
            cc, 
            gEpG, 
            {image_id:
                image_dir+image_id2name[image_id] 
                for image_id in image_id2name},
            scale)

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

def draw_epilines(IM, im, cc, gEpG,scale):
    epipolarGeometries=vis.filterEpG(gEpG, cc.views)
    for im_id in cc.views:
        if ((im_id is not im) 
        and ((im_id,im) in epipolarGeometries)):
            F=epipolarGeometries[(im_id,im)]
            for v in cc.views[im_id]:
                v_id=v.key()
                vis.drawEpiline(IM,F,v,color=vis.GREEN,img_scale=scale)
    return IM

def find_right_text_scale(im_id,w,h,t):
    def stop_condition(s):
        tsize=cv2.getTextSize(str(im_id), cv2.FONT_HERSHEY_SIMPLEX, s, t)
        if tsize[0]>w or tsize[1]>h:
            return False
        return True
    tscale=1.
    while stop_condition(tscale):
        tscale=tscale*1.2
    return tscale/1.2

key_num_image_map={49:3,50:4,51:6,52:8,53:9,54:12}

    
def visualize_cc(cc, gEpG, image_id2name,scale):
    """
    ----Arguments
    cc: a connected component
    gEpG: a dictionary of fundamental matrices
    image_id2name : a dictionary to map image ids to files
    scale: a divisor to scale the image visualization
    ----GUI commands
    q : quit the current image, open the next one
    right-left : shift images
    1,2,3,4,5,6: set the number of images to display
    e : toggle epilines
    t : toggle image label
    l : toggle labels
    page-up,page-down: scale images up or down
    s : save image; the file will be named after the connected components id
    """
    should_draw_epilines=False
    should_draw_text=False
    my_scale=scale
    num_images=3
    redraw = True
    save= False
    quitting=False
    image_indexes = sorted(cc.views)
    def _draw(im_id):
        _i=vis.getIMG(image_id2name[im_id],color=True)
        native_image_height,native_image_width,=_i.shape[0:2]
        img_size=(int(native_image_width/my_scale),int(native_image_height/my_scale))
        ii=cv2.resize(_i,img_size)
        if should_draw_text:
            tscale=find_right_text_scale(im_id,img_size[0],img_size[1],3)
            cv2.putText(ii, str(im_id), (0,img_size[1]-10),cv2.FONT_HERSHEY_SIMPLEX, 1, vis.RED,3) 
        if should_draw_epilines:
            ii=draw_epilines(ii, im_id, cc, gEpG, my_scale)
        ii=draw_kps(ii, cc.views[im_id],my_scale)
        #print 'image #{} : {}'.format(im_id,image_id2name[im_id])
        return ii
    cv2.namedWindow(str(cc.id))
    num_images_d=dict(zip('1234567',[3,4,6,8,9,12,16]))
    while not quitting: 
        if redraw:
            images = [_draw(im_id) for im_id in image_indexes[:num_images]]
            redraw=False
            GAL = vis.auto_grid(images)
            cv2.imshow(str(cc.id),GAL)
            if save:
                cv2.imwrite(str(cc.id)+'.jpg',GAL)
                save=False
        key=get_key()
        if key is 255:
            pass
        elif key in [scale_up_key, ord('+')]:
            my_scale=my_scale*1.1
            redraw=True
        elif key in [scale_down_key, ord('-')]:
            my_scale=my_scale/1.1
            redraw=True
        elif key is ord('t'):
            should_draw_text= not should_draw_text
            redraw=True
        elif key is ord('e'):
            should_draw_epilines= not should_draw_epilines
            redraw=True
        elif key is ord('s'):
            redraw=True
            save=True
        elif key is right_key:
            image_indexes = shift_right(image_indexes)
            redraw = True
        elif key is left_key:
            image_indexes = shift_left(image_indexes)
            redraw=True
        elif key is ord('q'):
            quitting=True
        elif chr(key) in num_images_d :
            num_images=num_images_d[chr(key)]
            redraw=True


            
            
            


def main(argv):
    if len(argv)<4:
        print """
    Track Visualization
    how to use:
    trackVis image_directory cc_track_file epipolar_geometry_file cc_id1 [cc_id_n]
    es:
    trackVis dataset data/cc.pk data/matches.epg 78493 21344 3433 7545
        """
        return
    elif len(argv)==4:
        visualize_k(
        argv[1], # image_dir,
        argv[2], # cc_track_file,
        argv[3], # epipolar_geometry_file,
        10, # number of connected components to survey
           1.)  # scale
    elif len(argv)>4:
        visualize(
        argv[1], # image_dir,
        argv[2], # cc_track_file,
        argv[3], # epipolar_geometry_file,
        argv[4:], # cc_ids
            1.)  # scale

if __name__ == "__main__":
    main(sys.argv)


