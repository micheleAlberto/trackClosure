from collections import namedtuple, Counter
import numpy as np
Candidate= namedtuple('candidate_keypoint',['index','value'])
def better(cand1,cand2):
    if cand1.value>cand2.value:
        return cand1
    else :
        return cand2

def select_first_admissible_keypoint(
        cliques,
        factors,
        kps2cliques,
        selected_keypoints,
        excluded_keypoints,
        radius,
        n_keypoints
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
       
    DEF a keypoint is available if
            it does not belong to the current track (selected keypoints)
            it does not belong to other completed tracks (excluded keypoints)
    DEF a keypoint is admissible if
        all the cliques that the keypoint belongs to are either admissible 
            or not relevant
        it belongs to at least one relevant admissible clique
    DEF a clique is admissible if 
        the relevant factor is lower than radius
    DEF a clique is relevant if
        two of its keypoint are in the current track (selected keypoints)
    RETURN:
    the id of an available, admissible keypoint
    return -1 if no such keypoint exist 
    """
    relevant_clique=lambda c: len(selected_keypoints.intersection(cliques[c]))==2
    def clique_inspector(kp):
        correct_cliques = 0
        for c_ind in kps2cliques[kp]:
            if relevant_clique(c_ind):
                if factors[c_ind]<radius:
                    correct_cliques+=1
                else:
                    return 0 # one clique is wrong
        return correct_cliques
    available_KP=(kp 
        for kp in range(n_keypoints) 
        if (not kp in selected_keypoints)
        and (not kp in excluded_keypoints))
    for kp in available_KP:
        selected_cliques_are_correct = True
        correct_cliques = clique_inspector(kp)
        if correct_cliques>0 :
            return kp
    return -1



def select_best_admissible_keypoint(
        cliques,
        factors,
        kps2cliques,
        selected_keypoints,
        excluded_keypoints,
        radius,
        n_keypoints
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
       
    DEF a keypoint is available if
            it does not belong to the current track (selected keypoints)
            it does not belong to other completed tracks (excluded keypoints)
    DEF a keypoint is admissible if
        all the cliques that the keypoint belongs to are either admissible 
            or not relevant
        it belongs to at least one relevant admissible clique
    DEF a clique is admissible if 
        the relevant factor is lower than radius
    DEF a clique is relevant if
        two of its keypoint are in the current track (selected keypoints)
    RETURN:
    the id of an available, admissible keypoint such that the number of verified cliques is maximal
    return -1 if no such keypoint exist 
    """
    relevant_clique=lambda c: len(selected_keypoints.intersection(cliques[c]))==2
    def other_keypoint_in_relevant_clique(c_ind):
        for kp in cliques[c_ind]:
            if not kp in selected_keypoints:
                return kp
    def clique_inspector(kp):
        correct_cliques = 0
        for c_ind in kps2cliques[kp]:
            if relevant_clique(c_ind):
                if factors[c_ind]<radius:
                    correct_cliques+=1
                else:
                    return 0 # one clique is wrong
        return correct_cliques
    def good_available_keypoints():
        #cliques that are eligible to be satisfied
        c_eligible=set([ 
            c_ind 
            for kp_sel in selected_keypoints
            for c_ind in kps2cliques[kp_sel]
            if ( relevant_clique(c_ind) 
            and (not other_keypoint_in_relevant_clique(c_ind) in excluded_keypoints)
            and (factors[c_ind]<radius))]
            )
        good_kps=Counter(map(other_keypoint_in_relevant_clique,c_eligible))
        return sorted(good_kps,key=lambda kp_id:-good_kps[kp_id])
    for kp in good_available_keypoints():
        selected_cliques_are_correct = True
        correct_cliques = clique_inspector(kp)
        if correct_cliques>0 :
            return kp
    return -1

def select_close_admissible_keypoint(
        cliques,
        factors,
        kps2cliques,
        selected_keypoints,
        excluded_keypoints,
        radius,
        n_keypoints
        ):
    """
    args:
    
    kp[3] cliques [n_cliques] : list of lists of keypoints of a clique
    float factors [n_cliques] : list of errors on cliques of keypoints
    clique[] kps2cliques[n_keypoints] : list of cliques that refer each keypoint
    set(kp) selected_keypoints : keypoints already selected for the track
    set(kp) excluded_keypoints : keypoints already selected for another track
    float radius : the radius of the filter 
    (int) n_keypoints : the number of keypoints
       
    DEF a keypoint is available if
            it does not belong to the current track (selected keypoints)
            it does not belong to other completed tracks (excluded keypoints)
    DEF a keypoint is admissible if
        all the cliques that the keypoint belongs to are either admissible 
            or not relevant
        it belongs to at least one relevant admissible clique
    DEF a clique is admissible if 
        the factor associated with the clique is lower than radius
    DEF a clique is relevant if
        every keypoint in the clique except one belong to the current track
        (selected keypoints) 
    RETURN:
    the id of an available, admissible keypoint such that the number of verified cliques is maximal
    return -1 if no such keypoint exist 
    """
    def relevant_clique(c):
        _clique=cliques[c]
        return len(selected_keypoints.intersection(_clique))==(len(_clique)-1)
    def other_keypoint_in_relevant_clique(c_ind):
        for kp in cliques[c_ind]:
            if not kp in selected_keypoints:
                return kp
    def clique_inspector(kp):
        correct_cliques = 0
        for c_ind in kps2cliques[kp]:
            if relevant_clique(c_ind):
                if factors[c_ind]<radius:
                    correct_cliques+=1
                else:
                    return 0 # one clique is wrong
        return correct_cliques
    def good_available_keypoints():
        #cliques that are eligible to be satisfied by adding a keypoint
        c_eligible=set([ 
            c_ind 
            for kp_sel in selected_keypoints
            for c_ind in kps2cliques[kp_sel]
            if ( relevant_clique(c_ind) 
            and (not other_keypoint_in_relevant_clique(c_ind) in excluded_keypoints)
            and (factors[c_ind]<radius))]
            )
        good_kps=Counter(map(other_keypoint_in_relevant_clique,c_eligible))
        kp_err=lambda kp: np.average([factors[c_ind] for c_ind in kps2cliques[kp] if c_ind in c_eligible])
        return sorted(good_kps,key=kp_err)
    for kp in good_available_keypoints():
        selected_cliques_are_correct = True
        correct_cliques = clique_inspector(kp)
        if correct_cliques>0 :
            return kp
    return -1
        
def select_admissible_keypoint_picky(
        cliques,
        factors,
        kps2cliques,
        selected_keypoints,
        excluded_keypoints,
        radius,
        n_keypoints,
        discard_keypoints
        ):
    """
    args:
    
    kp[3] cliques [n_cliques] : list of lists of keypoints of a clique
    float factors [n_cliques] : list of errors on cliques of keypoints
    clique[] kps2cliques[n_keypoints] : list of cliques that refer each keypoint
    set(kp) selected_keypoints : keypoints already selected for the track
    set(kp) excluded_keypoints : keypoints already selected for another track
    float radius : the radius of the filter 
    int discard_keypoints     : number of keypoints to discard
       
    DEF a keypoint is available if
            it does not belong to the current track (selected keypoints)
            it does not belong to other completed tracks (excluded keypoints)
    DEF a keypoint is admissible if
        all the cliques that the keypoint belongs to are either admissible 
            or not relevant
        it belongs to at least one relevant admissible clique
    DEF a clique is admissible if 
        the relevant factor is lower than radius
    DEF a clique is relevant if
        two of its keypoint are in the current track (selected keypoints)
    RETURN:
    the id of an available, admissible keypoint that expand the support of the 
    track by a number of cliques higher than at least other discard_keypoints       
    keypoints that are available and admissible for the track
    return -1 if no such keypoint exist 
    """
    relevant_clique=lambda c: len(selected_keypoints.intersection(cliques[c]))==2
    def clique_inspector(kp):
        correct_cliques = 0
        for c_ind in kps2cliques[kp]:
            if relevant_clique(c_ind):
                if factors[c_ind]<rad:
                    correct_cliques+=1
                else:
                    return 0 # one clique is wrong
        return correct_cliques
    available_KP=(kp 
        for kp in range(n_keypoints) 
        if (not kp in selected_keypoints)
        and (not kp in excluded_keypoints))
    best=Candidate(-1,-1)
    better_than=0
    for kp in available_KP:
        selected_cliques_are_correct = true
        correct_cliques = clique_inspector(kp)
        if correct_cliques>0 :
            best=better(
                best,
                Candidate(kp,correct_cliques))
            if better_than>discard_keypoints:
                return best.index
    return best.index

       
