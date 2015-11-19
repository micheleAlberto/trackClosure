"""
This module implements functions to map keypoints of one partition to tracks of another
fetch maps one track to tracks of another partition
partition_transfer maps many tracks of a partition to other tracks in another partition

the soft versions allow to map not only when the keypoint in present in the 
partition but also when it is close a keypoint in the partition
"""

import closure.trackclosure.transitiveclosure as Partition

def fetch(partition,track):
    """ 
    extract from partition identifiers of tracks that match the track
    """
    track_ids=[]
    for v in track.allViews():
        vk=v.key()
        if ((vk[0] in partition.views) 
        and (vk[1] in partition.views[vk[0]])):
            track_id=partition.views[vk[0]][vk[1]]
            track_ids.append(track_id)
    return track_ids

def soft_fetch(partition,track):
    """ 
    extract from partition identifiers of tracks that match the track or end up 
    near a matched keypoint
    """
    return soft_fetch_views(partition,track.allViews())


def soft_fetch_views(partition,views):
    """ 
    extract from partition identifiers of tracks that match the keypoints in the
    list views or end up near one of those keypoint (no further than 10. pixels)
    """
    track_ids=[]
    for v in views:
        vk=v.key()
        if (vk[0] in partition.views) :
            if (vk[1] in partition.views[vk[0]]):
                track_id=partition.views[vk[0]][vk[1]]
                track_ids.append(track_id)
            else:
                nearest_keyponint = nearest_view(v,partition)
                if (nearest_keyponint 
                and np.linalg.norm(v.pt(),nearest_keyponint.pt())<10.):
                   track_id=partition.views[vk[0]][nearest_keyponint.id_image]
                   track_ids.append(track_id)
    return track_ids   

def nearest_view(v0,partition):
    nearest=min(
        key=lambda v: np.linalg.norm(v0.pt(),v.pt()),
        (v 
            for t_id in partition.views[image_id]
            for v in partition.points[t_id].views[image_id]
        ),
        None)
    return nearest

def partition_transfer(part_x,part_y,track_ids_y):
    """
    extract from partition x identifiers of tracks that match the tracks
    identified by a vector of track identifiers in partition y
    """
    track_ids_x=map(lambda track_id_y:fetch(part_x,part_y.points[track_id_y]),track_ids_y)
    return track_ids_x

def soft_partition_transfer(part_x,part_y,track_ids_y):
    """
    extract from partition x identifiers of tracks that match the tracks
    identified by a vector of track identifiers in partition y
    """
    track_ids_x=map(lambda track_id_y:soft_fetch(part_x,part_y.points[track_id_y]),track_ids_y)
    return track_ids_x


def track_is_wrong(track_x,oracle):
    """
    returns
        -1  if unknown : we have no known oracles for the given track
        0   if correct : there is a unique oracle for the track
        1   if wrong   : there are multiple known oracles for the track
    """
    xO=soft_fetch(oracle,track_x)
    return len(xO)-1


from collections import Counter

def dominant(list_of_indexes):
    c=Counter(list_of_indexes)
    return max(c,key=c.get)
 
