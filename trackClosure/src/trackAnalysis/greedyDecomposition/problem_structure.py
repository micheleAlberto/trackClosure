from collections import namedtuple
from itertools import combinations
from tqdm import tqdm
import numpy as np
from ...closure.point import point as Track

Clique = namedtuple('clique',['i','j','k'])
Keypoint = namedtuple('keypoint',['i','im','kp','pt'])

def clique_error(c,keypoints,gEpG):
    error=0.
    epipolar = lambda src,dst:np.dot(
            gEpG[
                keypoints[src].im,
                keypoints[dst].im], 
            keypoints[src].pt)
    for i,j,k in [
        (c[0],c[1],c[2]),
        (c[2],c[0],c[1]),
        (c[1],c[2],c[0])]:
        prediction_i=np.cross(epipolar(j,i),epipolar(k,i))
        prediction_i=prediction_i[0:2]/prediction_i[2]
        observation_i=keypoints[i].pt[0:2]
        error+=np.linalg.norm(observation_i-prediction_i)
    return error


def make_structure(T,gEpG):
    kps=[Keypoint(vi,v.id_image,v.id_keypoint,v.hpt()) for vi,v in enumerate(T.allViews())]
    # O(|T.allViews()|)
    cliques=[
        Clique(I.i,J.i,K.i) 
        for I,J,K in list(combinations(kps,3))
        if (
        ((I.im,J.im) in gEpG) and 
        ((I.im,K.im) in gEpG) and 
        ((K.im,J.im) in gEpG) ) ]
    # O(|combinations(T.allViews(),3)|) = 
    # O( |kps|*(|kps|-1)*(|kps|-2)/6) = 
    # O(|kps|^3)
    factors=[clique_error(c,kps,gEpG) for c in cliques]
    # O(|cliques|)<O(|kps|^3)
    kps2cliques=[[] for kp in kps]
    for ci,c in enumerate(cliques):
        for kp_i in c:
            kps2cliques[kp_i].append(ci)
    # O(|cliques|*3)<O(|kps|^3)
    return kps,cliques,factors,kps2cliques

def make_structure_sorted_by_factor(T,gEpG):
    kps=[Keypoint(vi,v.id_image,v.id_keypoint,v.hpt()) for vi,v in enumerate(T.allViews())]
    # O(|T.allViews()|)
    cliques=[
        Clique(I.i,J.i,K.i) 
        for I,J,K in tqdm(list(combinations(kps,3)),'cliques')
        if (
        ((I.im,J.im) in gEpG) and 
        ((I.im,K.im) in gEpG) and 
        ((K.im,J.im) in gEpG) ) ]
    # O(|combinations(T.allViews(),3)|) = 
    # O( |kps|*(|kps|-1)*(|kps|-2)/6) = 
    # O(|kps|^3)
    factors=[clique_error(c,kps,gEpG) for c in tqdm(cliques,'factors')]
    sorting_domain=range(len(factors))
    sorting_key=lambda c_id:factors[c_id]
    sorting_map=sorted(sorting_domain,key=sorting_key)
    sorted_cliques=[cliques[c_id] for c_id in sorting_map]
    sorted_factors=[factors[c_id] for c_id in sorting_map]
    kps2cliques=[[] for kp in kps]
    for ci,c in enumerate(sorted_cliques):
        for kp_i in c:
            kps2cliques[kp_i].append(ci)
    # O(|cliques|*3)<O(|kps|^3)
    return kps,sorted_cliques,sorted_factors,kps2cliques


def build_tracks(T,tracks,kps):
    """
    arguments:
    dict(int->int[]) tracks : maps track id to list of keypoint ids
    Keypoint[] kps : list of keypoints
    """
    L=[]
    for t in tracks.values():
        set_of_t=set(t)
        V=[v for vi,v in enumerate(T.allViews()) if vi in set_of_t]
        L.append(Track(0,V))
    return L


