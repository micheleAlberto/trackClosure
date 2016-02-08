
from problem_structure import make_structure 
from problem_structure import build_tracks
#from problem_structure import make_structure_sorted_by_factor as make_structure
from init_track import init_track_min_factor as init_track
from keypoint_selection import select_first_admissible_keypoint as select_new_keypoint
from keypoint_selection import select_admissible_keypoint_picky
from keypoint_selection import select_best_admissible_keypoint, select_close_admissible_keypoint
import numpy as np
from itertools import combinations

picky_kp_select=(lambda cliques,
                        factors,
                        kps2cliques,
                        selected_keypoints,
                        excluded_keypoints,
                        radius,
                        n_kp:   
                select_admissible_keypoint_picky(
                        cliques,
                        factors,
                        kps2cliques,
                        selected_keypoints,
                        excluded_keypoints,
                        radius,
                        n_keypoints,
                        10)
                        )

keypoint_selectors = [
    select_new_keypoint, 
    select_best_admissible_keypoint,
    select_close_admissible_keypoint,
    select_admissible_keypoint_picky]     
          
def make_track_greedy_decomposition(gEpG,radius,keypoint_selector=2):
    if type(keypoint_selector)==int:
        kp_functor=keypoint_selectors[keypoint_selector]
    else:
        kp_functor=keypoint_selector
    def track_greedy_decomposition(T):
        """
        track_greedy_decomposition(T):
        given: kps,cliques,factors,kps2cliques
            tracks = {}
            excluded_keypoints = {}
            while T = initialize track (...)
                while kp = select keypoint (...)
                    add keypoint kp to T
                add track T to tracks
            return tracks        
        """
        kps,cliques,factors,kps2cliques=make_structure(T,gEpG)
        tracks={}
        track_initialization_is_possible = True
        excluded_keypoints=set()
        iteration=0
        while track_initialization_is_possible:
                current_track=init_track(excluded_keypoints,kps,cliques,factors,kps2cliques)
                if not len(current_track)<2:
                    support_expansion_is_possible=True        
                    while support_expansion_is_possible:
                        kp=kp_functor(
                            cliques,
                            factors,
                            kps2cliques,
                            current_track,
                            excluded_keypoints,
                            radius,
                            len(kps))
                        if kp == -1:
                            support_expansion_is_possible = False
                        else:
                            current_track.add(kp)
                else:
                    track_initialization_is_possible = False
                excluded_keypoints.update(current_track)
                tracks[iteration]=list(current_track)
                iteration+=1
        return build_tracks(T,tracks,kps)
    return track_greedy_decomposition


class decomposition_tuner:
    def __init__(self,gEpG,T):
        self.gEpG=gEpG
        self.T=T
        structure=make_structure(T,gEpG)
        self.kps,self.cliques,self.factors,self.kps2cliques=structure
    def merging_support(self,t1,t2):
        #print 'mergin cost ',t1,' ', t2
        s1=set(t1)
        s2=set(t2)
        count=0.
        for c_id,c in enumerate(self.cliques):
            m1 = len(s1.intersection(c))
            m2 = len(s2.intersection(c))
            if (m1+m2==3) and (m1<3) and (m2<3):
              if self.factors[c_id]<1400.:
                count+=1.
        return count
    def get_track_twin_pair(self,tracks,min_support):
        TIDs=sorted(tracks.keys(),key=lambda tid:len(tracks[tid]))
        pair_gen=( (tid1,tid2)
            for tid1,tid2 in combinations(TIDs,2)
            if self.merging_support(
                tracks[tid1],
                tracks[tid2])>min_support)
        for tid1,tid2 in pair_gen:
            return tid1,tid2
    def build_tracks(self,tracks):
        return build_tracks(self.T,tracks,self.kps)
    def solve_for(self,radius,selector_method=0):
        tracks={}
        track_initialization_is_possible = True
        excluded_keypoints=set()
        iteration=0
        while track_initialization_is_possible:
                current_track=init_track(excluded_keypoints,self.kps,self.cliques,self.factors,self.kps2cliques)
                #print '[track decomposition] track {} = {}'.format(
                #      iteration,current_track)
                if not len(current_track)<2:
                    support_expansion_is_possible=True        
                    while support_expansion_is_possible:
                        kp=keypoint_selectors[selector_method](
                            self.cliques,
                            self.factors,
                            self.kps2cliques,
                            current_track,
                            excluded_keypoints,
                            radius,
                            len(self.kps))
                        if kp == -1:
                            support_expansion_is_possible = False
                        else:
                            current_track.add(kp)
                            #print '[track decomposition] track {} += kp {}'.format(
                            #       iteration,kp)
                else:
                    track_initialization_is_possible = False
                excluded_keypoints.update(current_track)
                tracks[iteration]=list(current_track)
                iteration+=1
        #print '[track decomposition] orphans:',[i for i in range(len(self.kps)) if not i in excluded_keypoints]
        return self.build_tracks(tracks)

        
