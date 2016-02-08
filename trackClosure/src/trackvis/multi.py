import numpy as np
import cv2
from math import sin , cos
from itertools import cycle
from ..roamfree.trackCentroid import centroid
from ..trackAnalysis.trackAnalisys import compactPoint, observations_weak, observations_strict, pointTransferVectorized
from trackvis import drawEpiline # drawEpiline(img,F,v,color=(0,255,0),label=False,img_scale=1.)
"""
module for multi track drawing
given an image id, some tracks , an epipolar geometry 
will draw in different colors each track 
track centroids may be displayed
track keypoints may be displayed
track shadows may be displayes
"""
kp_style={'xs':(2,1), 's':(4,1), 'm':(8,2), 'l':(14,4), 'xl':(20,5)}

def draw_kp(IM,uv,color,scale,radius,thickness):
    P=(int(uv[0]/scale), int(uv[1]/scale))
    cv2.circle(IM,P,radius,color,thickness)
"""
uv : keypoint
color : track
scale : gui scale
radius : style
thickness : style
"""
def computeMultiTrackShadows(I,gEpG,tracks,weak=False):
    """
    compute shadow points from many tracks on a single image
    return a distionary indexed by track id
    """
    shadows_of={}
    for tid,t in enumerate(tracks):
        if len(t.views)>2:
            P = compactPoint(t)
            P_list = P.keys()
            IJK=(
                observations_weak(P_list,gEpG)
                if weak
                else observations_strict(P_list,gEpG))
            shadows_of[tid]=pointTransferVectorized(I,IJK,P,gEpG) 
    return shadows_of

def drawEpiline(img,ep,color,img_scale):
    x1=0
    x2=len(img[0])#*img_scale
    y1=(-(ep[2])/ep[1])/img_scale
    #y2=-(ep[2]+x2*ep[0])/ep[1]
    #print x1,x2 ,y1,y2
    #p1=(int(x1),int(y1))
    #len(img[0])*img_scale
    y2=-(ep[2]/img_scale+len(img[0])*ep[0])/ep[1]
    p1=(0,int(y1))
    p2=(int(x2),int(y2))
    cv2.line(img,p1,p2,color)
    


class multiTrackDrawing:
    def __init__(self,tracks,gEpG,colors,scale):
        self.tracks=tracks
        self.T=len(tracks)
        self.gEpG=gEpG
        self.colors={t:c 
            for t,c in zip(
                range(len(tracks)),
                cycle(colors))}
        self.scale=scale
    def set_scale(self,scale):
        self.scale=scale
    def draw_some_points(self,image_id,image,style,kp_map):
        kps=kp_map
        for tid in kps:
            for kp in kps[tid]:
                draw_kp(
                    image,
                    kp, 
                    self.colors[tid],
                    self.scale,
                    style[0],style[1])
    def draw_keypoints(self,image_id,image):
        kps=self.get_keypoints(image_id)
        self.draw_some_points(image_id,image,kp_style['m'],kps)
    def draw_centroids(self,image_id,image):
        kps=self.get_centroids(image_id)
        self.draw_some_points(image_id,image,kp_style['l'],kps)
    def draw_shadows(self,image_id,image):
        kps=self.get_shadows(image_id)
        self.draw_some_points(image_id,image,kp_style['s'],kps)
    def get_keypoints(self,image_id):
        V=(lambda tid:
            self.tracks[tid].views[image_id] 
            if image_id in self.tracks[tid].views 
            else [])
        V2KP=lambda v:(v.u,v.v)
        return {tid: [V2KP(v) for v in V(tid)] for tid in range(self.T)}
    def get_centroids(self,image_id):
        KP=lambda tid: centroid(self.tracks[tid].views[image_id])
        tup=lambda v:(v.u,v.v)
        return {tid: [tup(KP(tid))] 
                for tid in range(self.T)
                if image_id in self.tracks[tid]}
    def get_shadows(self,image_id):
        shadows=computeMultiTrackShadows(image_id,self.gEpG,self.tracks)
        return {tid:[(s[0],s[1]) for s in shadows[tid]] for tid in shadows}
    def get_epilines(self,image_id):
        epilines_of={}
        for tid in range(self.T):
         epilines_of[tid]=[]
         if image_id in self.tracks[tid].views:
          for j in self.tracks[tid].views:
           if j is not image_id:
            if (j,image_id) in self.gEpG:
             F = self.gEpG[j,image_id]
             for v in self.tracks[tid].views[j]:
                h=np.array([v.u,v.v,1])
                ep=np.dot(F,h)
                epilines_of[tid].append(ep)
        return epilines_of
    def draw_epilines(self, image_id, image):
        eps = self.get_epilines(image_id)
        for tid in eps:
            drawEpiline(
                image,
                eps[tid],
                self.colors[tid],
                self.scale)





        
