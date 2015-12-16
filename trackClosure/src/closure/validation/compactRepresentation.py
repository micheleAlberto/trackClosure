#compactRepresentation.py
from deprecator import deprecated
import numpy as np
    #trasforma la rappresentazione del punto
    #da transclosure.point
    #a un dizionari di triplette I:(I,h,r)
    #   I : immagine
    #   h : centro del cerchio minimo che comprende le viste in coordinate omogenee
    #   r : raggio del cerchio
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
        compact[I] = (I, h, radius)
    return compact

#aggregation function : center, radius <- np.array([[v.v, v.u] for v in P.views[I] ])
# punti: np.array([[v.v, v.u] for v in P.views[I] ])
# cv2.minEnclosingCircle
# centroide: np.mean(punti,0)
# distanze : np.linalg.norm(punti-centroide,axis=1)
# pesi : kernel(distanze)
# centroide_iterativo : np.sum(punti*pesi,0)/np.sum(pesi)

def centroid_direct(x):
    c=np.mean(x,0)
    r=np.mean(np.linalg.norm(x-c,axis=1))
    return c,r

from random import choice
def centroid_iterative(x,tresh=0.2):
    c=choice(x)+tresh
    #c=np.mean(x,0)
    #walk=[c]
    dist=np.linalg.norm(x-c,axis=1)
    mean_dist=np.mean(dist)
    w=mean_dist/dist
    next_c=np.sum(x.T*w,1).T/np.sum(w)
    diff=np.linalg.norm(next_c-c)
    c=next_c
    i=1
    while(diff>tresh):
        dist=np.linalg.norm(x-c,axis=1)
        mean_dist=np.mean(dist)
        w=mean_dist/dist
        next_c=np.sum(x.T*w,1).T/np.sum(w)
        diff=np.linalg.norm(next_c-c)
        c=next_c
        #walk.append(c)
        #print i, c
        i+=1
    r=np.sum(dist*w)/np.sum(w)
    return c,r
