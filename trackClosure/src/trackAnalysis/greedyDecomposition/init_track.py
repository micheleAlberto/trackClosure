

"""
Abstract interface for track initialization
  
initialize a track
    Arguments:
        set(int)        excluded_keypoints
        list(Keypoint)  kps
        list(Clique)    cliques
        list(float)     factors
        list(list(int)) kps2cliques

    Return:
        an admissible track as a set of available keypoint ids
    
    a track is a set of keypoint id

    DEF a keypoint is available if
        it does not belong to other completed tracks (excluded keypoints)

    DEF a track is admissible if
        every clique of keypoints that belong to the track has minimal error 

def init_track(excluded_keypoints,kps,cliques,factors,kps2cliques):
    return set()
    """

def init_track_min_factor(excluded_keypoints,kps,cliques,factors,kps2cliques):
    """
    Initialize a track from the clique that has lower factor
    Arguments:
        set(int)        excluded_keypoints
        list(Keypoint)  kps
        list(Clique)    cliques
        list(float)     factors
        list(list(int)) kps2cliques
    Return:
        an admissible track as a set of available keypoint ids
    """
    clique_admissible=lambda c: len(excluded_keypoints.intersection(cliques[c]))==0
    clique_factor=lambda c: factors[c]
    admissible_cliques=[c 
        for c in range(len(cliques)) 
        if clique_admissible(c)]
    if len(admissible_cliques)==0:
        return set()
    c=min(admissible_cliques, key=clique_factor)
    return set(cliques[c])


