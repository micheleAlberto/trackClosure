from collections import Counter, namedtuple
import numpy as np

from itertools import combinations

Shadow=namedtuple('shadow', ['i', 'j', 'k'])
Point=namedtuple('point', ['i', 'h','r'])

def centroid_direct(x):
    c=np.mean(x,0)
    r=np.mean(np.linalg.norm(x-c,axis=1))
    return c,r

def compactPoint(P):
    """
    map the representation of a track as an equivalence graph (closure.point.point)
    to a geometrical representation
        * free from graph topology
        * that sample at most one keypoint in homoegenus coordinates per image
    the sample keypoint is chosen to be baricenter of the keypoints
    return {image_id:(image_id,homogeneus_keypoint,keypoint_radius) for image_id in P.views}
    """
    compact = {}
    #print 'compactPoint {}, maximum distance {}'.format(P, maxdist)
    for I in P.views.keys():
        vs = np.array([[v.u, v.v] for v in P.views[I] ])
        #center, radius = cv2.minEnclosingCircle(vs)
        center, radius = centroid_direct(vs)
        #print "img {}, p {}, r {}".format(I,center, radius)
        h = np.array([center[0], center[1], 1])
        compact[I] = Point(I, h, radius)
    return compact

def pointTransferVectorized(k,IJK,P,gEpG):
    if ((k not in IJK) or len(IJK[k])==0):
        return []
    Fik=np.array([ gEpG[(s.i,s.k)] for s in IJK[k]])
    Fjk=np.array([ gEpG[(s.j,s.k)] for s in IJK[k]])
    mi=np.array([P[s.i].h for s in IJK[k] ])
    mj=np.array([P[s.j].h for s in IJK[k]])
    product=np.tensordot(Fik,mi,(2,1))
    EpIonK=np.array([product[i,:,i] for i in range(len(product))])
    product=np.tensordot(Fjk,mj,(2,1))
    EpJonK=np.array([product[i,:,i] for i in range(len(product))])
    MK=np.cross(EpIonK,EpJonK)
    rkp=(MK.T/MK[:,2]).T[:,0:2]
    return rkp
    
def observations(P_list,gEpG):
    #triplets: images i and j project to image k 
    IJK={
        k:[
            Shadow(i, j, k)
            for i, j in combinations(P_list, 2) 
            if ((i, k) in gEpG 
            and (j, k) in gEpG)
          ] 
    for k in P_list}
    return IJK

def observations_weak(P_list,gEpG):
    #triplets: images i and j project to image k 
    IJK={
        k:[
            Shadow(i, j, k)
            for i, j in combinations(P_list, 2) 
            if ((i, k) in gEpG 
            and (j, k) in gEpG
            and not (i, j) in gEpG)
          ] 
    for k in P_list}
    return IJK

def observations_strict(P_list,gEpG):
    #triplets: images i and j project to image k 
    IJK={
        k:[
            Shadow(i, j, k) 
            for i, j in combinations(P_list, 2) 
            if ((i, k) in gEpG 
            and (j, k) in gEpG 
            and (i, j) in gEpG)]
    for k in P_list}
    return IJK

def computeWeakShadows(gEpG,track):
    P = compactPoint(track)
    P_list = P.keys()
    IJK = observations_weak(P_list,gEpG)
    shadows_on={
        k:pointTransferVectorized(k,IJK,P,gEpG) 
        for k in P_list}
    return shadows_on

def computeShadows(gEpG,track):
    P = compactPoint(track)
    P_list = P.keys()
    IJK = observations_strict(P_list,gEpG)
    shadows_on={
        k:pointTransferVectorized(k,IJK,P,gEpG) 
        for k in P_list}
    return shadows_on

def computeMultiTrackShadows(I,gEpG,tracks,weak=False):
    shadows_of={}
    for t in tracks:
        if len(t.views)>2:
            P = compactPoint(t)
            P_list = P.keys()
            IJK=(
                observations_weak(P_list,gEpG)
                if weak
                else observations_strict(P_list,gEpG))
            shadows_of[t.id]=pointTransferVectorized(I,IJK,P,gEpG) 
    return shadows_of
    


