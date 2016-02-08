#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from ..closure.point import point as Track
from collections import namedtuple
from itertools import combinations
from tqdm import tqdm
#Factor = namedtuple('factor',['clique','e'])
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
        for I,J,K in tqdm(list(combinations(kps,3)),'cliques')
        if (
        ((I.im,J.im) in gEpG) and 
        ((I.im,K.im) in gEpG) and 
        ((K.im,J.im) in gEpG) ) ]
    # O(|combinations(T.allViews(),3)|) = 
    # O( |kps|*(|kps|-1)*(|kps|-2)/6) = 
    # O(|kps|^3)
    factors=[clique_error(c,kps,gEpG) for c in tqdm(cliques,'factors')]
    #opzione : 
    #ordinare cliques e factors in modo da anteporre le triplette 
    #con errore più alto; così le cliques che escludono keypoint vengono trovate
    #prima, riducendo le iterazioni interne alla verifica del keypoint
    # O(|cliques|)<O(|kps|^3)
    kps2cliques=[[] for kp in kps]
    for ci,c in enumerate(cliques):
        for kp_i in c:
            kps2cliques[kp_i].append(ci)
    # O(|cliques|*3)<O(|kps|^3)
    return kps,cliques,factors,kps2cliques

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


    
def select_new_keypoint(
        cliques,
        factors,
        kps2cliques,
        selected_keypoints,
        excluded_keypoints,
        radius,
        n_keypoints,
        first_improvement=True
        ):
    """
    args:
    
    kp[3] cliques [n_cliques] : list of lists of keypoints of a clique
    float factors [n_cliques] : list of errors on cliques of keypoints
    clique[] kps2cliques[n_keypoints] : list of cliques that refer each keypoint
    set(kp) selected_keypoints : keypoints already selected for the track
    set(kp) excluded_keypoints : keypoints already selected for another track
    float radius : the radius of the filter 
    first_improvement = True   : flag for first improvement heuristic
    
    returns:
 
    returns the id of a keypoint such that
        the keypoint IS NOT IN selected_keypoints
        the keypoint IS NOT IN excluded_keypoints
        all the cliques 
                that refer that keypoint 
            AND that have two elements in selected_keypoints
            SHOULD have error under a margin radius

    return -1 if no such keypoint exist 

    if using best improvement ( first_improvement= False ) such clique should 
    maximally extend the number of cliques supporting the track
    """
    best_keypoint=-1
    best_support_expansion=0
    two_keypoints_already_selected=lambda c: len(selected_keypoints.intersection(cliques[c]))==2
    small_factor=lambda f:factors[f]<radius
    test_clique=lambda c: (
            (not two_keypoints_already_selected(c)) or small_factor(c))
    KP=(kp 
        for kp in range(n_keypoints) 
        if (not kp in selected_keypoints)
        and (not kp in excluded_keypoints))
    for kp in KP:
        selected_cliques_are_correct = True
        c_it = 0
        adding_cliques = 0
        c_len = len(kps2cliques[kp])
        while selected_cliques_are_correct:
            if c_it==c_len:
                if first_improvement:
                    """
FIRST improvement search strategy return a keypoint identifier as soon as it is
proven consistent by all its cliques that are observed
                    """
                    return kp
                else:
                    """
BEST improvement search strategy return the keypoint identifier that maximize 
the number of cliques supporting the factor
                    """
                    if adding_cliques>best_support_expansion:
                        best_keypoint = kp
                        best_support_expansion = adding_cliques
                    #then exit the while loop over cliques
                    selected_cliques_are_correct = False
                    c_it+= 1 
            elif two_keypoints_already_selected(c_it):
                if small_factor(c_it):
                    c_it+= 1
                    adding_cliques+= 1
                else:
                    #a clique for this keypoint is not consistent
                    #reject this keypoint, exit the while loop
                    selected_cliques_are_correct = False
                    c_it+= 1
            else:
                c_it+= 1
        #if first_improvement reach this line no keypoint is found
        #then -1 is returned (best_keypoint was initialized as -1)
        #if best_improvement, the best keypoint is returned
        #if no keypoint is found -1 is returned
        return best_keypoint

def init_track(excluded_keypoints,kps,cliques,factors,kps2cliques):
    if len(excluded_keypoints)==0:
        clique_admissible=lambda c: True
    else:
        clique_admissible=lambda c: len(excluded_keypoints.intersection(cliques[c]))==0
    clique_factor=lambda c: factors[c]
    admissible_cliques=[c 
        for c in range(len(cliques)) 
        if clique_admissible(c)]
    if len(admissible_cliques)==0:
        print '[track_greedy_decomposition] no admissible cliques, initialization impossible'
        return set()    
    else:
        c=min(admissible_cliques, key=clique_factor)
        print '[track_greedy_decomposition] initialization on clique ',c
        print cliques[c], clique_factor(c)
        for kp_id in cliques[c]:
            print kps[kp_id]
        return set(cliques[c])

def make_track_greedy_decomposition(gEpG,radius,first_improvement):
    def initialization(cliques,factors):
        index=min(
            enumerate(factors), 
            key=lambda _if:_if[1])[0]
        return list(clique[index])
    def algo(T):
        tracks={}
        print '[track_greedy_decomposition] making structure'
        kps,cliques,factors,kps2cliques=make_structure(T,gEpG)
        # time cost grow as |keypoints|^3 in the dense case
        track_aggregation_is_possible=True
        while track_aggregation_is_possible:
            excluded_keypoints=set([kp for t in tracks for kp in tracks[t]])
            selected_keypoints=init_track(excluded_keypoints,kps,cliques,factors,kps2cliques)
            print '[track_greedy_decomposition] {} excluded, {} selected'.format(
                len(excluded_keypoints),len(selected_keypoints))
            print 'existing tracks :'
            for t in tracks:
                print tracks[t]
            print 'selected track :',selected_keypoints
            if len(selected_keypoints)>1:
                support_expansion_is_possible=True
                while support_expansion_is_possible:
                    kp=select_new_keypoint(
                        cliques,
                        factors,
                        kps2cliques,
                        selected_keypoints,
                        excluded_keypoints,
                        radius,
                        len(kps),
                        first_improvement)
                    if kp is None or kp == -1:
                        print '[track_greedy_decomposition] support expansion impossible'
                        support_expansion_is_possible = False
                    else:
                        print '[track_greedy_decomposition] support expansion kp:',kp
                        selected_keypoints.add(kp)
                t=max(tracks)+1 if len(tracks)>0 else 0
                tracks[t]=list(selected_keypoints)
                print 'new track ',t,' : ',tracks[t]
            else :
                track_aggregation_is_possible=False
        return build_tracks(T,tracks,kps)
    return algo
    
    
        


