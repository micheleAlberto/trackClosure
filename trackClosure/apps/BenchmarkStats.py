#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import sys
import pandas as pd
from ..src.closure.transclosure import load_tracks
from ..src.closure.point import point
from ..src.benchmark.benchmark import Benchmark
from ..src.benchmark.benchmark import save_benchmark
from ..src.benchmark.benchmark import load_benchmark
from ..src.benchmark.OracleGui import oracle_gui
from ..src.geometry.epipolarGeometry import EpipolarGeometry
from ..src.fromOpenMVG.wrapper import OpenMVG
from ..src.trackAnalysis.greedyDecomposition.problem_structure import make_cliques , triplet_error_and_cosine , analize_structure
#make_cliques(T,gEpG):
#triplet_error_and_cosine(c,keypoints,epipolars,gEpG):
def STATS(
        benchmark_file,
        epipolar_geometry_file,
        csv_output_file):
    """
    Compute a pandas dataframe of that describe errors on point transfer on the 
    connected components of the given benchmark
    ----Arguments:
    (str) benchmark_file 
    (str) epipolar_geometry_file
    (str) csv_output_file
    """
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    bm=load_benchmark(benchmark_file)
    #Data series to be pushed in the pandas dataframe
    ds_cc_id=[]
    ds_i=[]
    ds_j=[]
    ds_k=[]
    ds_t_err=[]
    ds_t_cos=[]
    ds_correct_pair=[]
    ds_correct_triplet=[]
    ds_type=[]
    print "benchmark file: ",benchmark_file
    def O(i,kps):
        return bm.oracle.viewQuery(kps[i].im,kps[i].kp)
    for cc_id in bm.CC.points.keys():
        cc=bm.CC.points[cc_id]
        o_ids=bm.cc2oracles(cc_id)
        kps,epipolars,cliques,kps2cliques=make_cliques(cc,gEpG)
        for c in cliques:
            triplets=[c,(c[1],c[2],c[0]),(c[2],c[0],c[1])]
            for triplet in triplets:
                i, j , k = triplet
                t_err, t_cos = triplet_error_and_cosine(triplet,kps,epipolars,gEpG)
                try:
                    correct_pair = (O(i,kps)==O(j,kps))
                    correct_triplet = correct_pair and (O(i,kps)==O(k,kps))
                    ds_cc_id.append(cc_id)
                    ds_i.append(i)
                    ds_j.append(j)
                    ds_k.append(k)
                    ds_t_err.append(t_err)
                    ds_t_cos.append(t_cos)
                    ds_correct_pair.append(correct_pair)
                    ds_correct_triplet.append(correct_triplet)
                    ds_type.append( 
                        't' if correct_triplet else 
                        'p' if correct_pair else
                        'f')
                except :
                    print "ERR:",i, j , k
    DF=pd.DataFrame.from_dict({
            'cc':ds_cc_id,
            'i':ds_i,
            'j':ds_j,
            'k':ds_k,
            'distance':ds_t_err,
            'cosine':ds_t_cos,
            'correctPair':ds_correct_pair,
            'correctTriplet':ds_correct_triplet,
            'type':ds_type})
    DF.to_csv(csv_output_file)

def STATS_UI():
    import pickfs as pk
    benchmark_file= pk.pick_file(text='select a benchmark file',extensions=['be'])
    epipolar_geometry_file= pk.pick_file(text='select an epipolar geometry file',extensions=['epg'])
    csv_output_file= 'benchstats.csv'
    STATS(
        benchmark_file,
        epipolar_geometry_file,
        csv_output_file)
    STATS_STRUCTURE(
        benchmark_file,
        epipolar_geometry_file,
        csv_output_file)
    

def STATS_STRUCTURE(
        benchmark_file,
        epipolar_geometry_file,
        csv_output_file):
    """
    Compute a pandas dataframe of that describe distances and epipolar angles on 
    cliques on the connected components of the given benchmark
    ----Arguments:
    (str) benchmark_file 
    (str) epipolar_geometry_file
    (str) csv_output_file
    """
    gEpG=EpipolarGeometry.load(epipolar_geometry_file)
    bm=load_benchmark(benchmark_file)
    #Data series to be pushed in the pandas dataframe
    ds_c_id=[]
    ds_clique=[]
    ds_t_dis=[]
    ds_t_cos=[]
    ds_oracle=[]
    print "benchmark file: ",benchmark_file
    def O(i,ps):
        return bm.oracle.viewQuery(ps.keypoints[i].im,ps.keypoints[i].kp)
    for cc_id in bm.CC.points.keys():
        cc=bm.CC.points[cc_id]
        o_ids=bm.cc2oracles(cc_id)
        ps=analize_structure(cc,gEpG)
        for cc_id,c,_dis,_cos in zip(
                    range(len(ps.cliques)),
                    ps.cliques,
                    ps.distances,
                    ps.cosines):
            try:
                i,j,k=c
                correct = (O(i,ps)==O(j,ps)) and (O(i,ps)==O(k,ps))
                ds_c_id.append(cc_id)
                ds_clique.append(c)
                ds_t_dis.append(_dis)
                ds_t_cos.append(_cos)
                ds_oracle.append(correct)
            except :
                print cc_id,"-ERR:",i, j , k
    DF=pd.DataFrame.from_dict({
            'c_id':ds_c_id,
            'clique':ds_clique,
            'distance':ds_t_dis,
            'cosine':ds_t_cos,
            'oracle':ds_oracle})
    DF.to_csv(csv_output_file)
 


