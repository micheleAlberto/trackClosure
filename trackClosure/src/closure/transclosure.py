#!/usr/bin/env python
#coding: utf8 
from itertools import groupby,chain,ifilter
import numpy as np
from validation import validation
from point import point
from fromMatches import simpleFilter
from view import view
import cv2
from validation.deprecator import deprecated
import ipdb
import pickle
import closure_pb2
from tqdm import tqdm




class LockedInsertion(Exception):
    def __init__(self,p):
        self.p=p

class transitiveclosure(object):
    def __init__(self):
        self.points={} #mappa point_id->[point]
        self.views={} #mappa view_id->{kp_id -> point_id}
        self.max=0
        self.freePoints=[]
    def allViews(self):
        return [(I,kp) for I in self.views.keys() for kp in self.views[I].keys()]
    def view_number(self):
        return sum(len(self.views[I]) for I in self.views.keys())
    def hasView(self,im_id,kp_id):
        return ((im_id in self.views) and (kp_id in self.views[im_id]))
    def setView(self,im_id,kp_id,p_id,onLock=None):
        if im_id in self.views:
            if __debug__ and onLock and (kp_id in self.views[im_id]):
                assert(self.views[im_id][kp_id]==onLock)
            self.views[im_id][kp_id]=p_id
        else:
            self.views[im_id]={kp_id:p_id}
    def viewQuery(self,im_id,kp_id):
        return self.views[im_id][kp_id]
    def viewPointViewQuery(self,im_id,kp_id):
        V=self.points[self.viewQuery(im_id,kp_id)].allViews()
        return [(v.id_image,v.id_keypoint) for v in V]
    def pointViewQuery(self,Point_id):
        V=self.points[Point_id].allViews()
        return [(v.id_image,v.id_keypoint) for v in V]
    def assert_no_empy_point(self):
        for p_id,P in self.points:
            assert len(P.views)>0
            for Im_id,vs in P.views:
                assert len(vs)>0
        return True
    def assert_every_point_indexed_exist2(self):
        allPoints1=self.points.keys()
        allPoints2=set([p_id for v in self.views.values() for p_id in v.values() ])
        for p1 in allPoints1:
            assert( p1 in allPoints2)
            for I,kp in self.pointViewQuery(p1):
                assert (self.viewQuery(I,kp)==p1)
        for p2 in allPoints2:
            assert( p2 in allPoints1)
        for I,kp in self.allViews():
            assert(kp in self.views[I])
            p_id=self.views[I][kp]
            assert(I in self.points[p_id].views)
            assert(kp in [v.id_keypoint for v in self.points[p_id].views[I]])
        return True
    def assert_every_point_indexed_exist(self):
        #from view to points, assert inclusion of the view in the point
        for I,kp in self.allViews():
            p=self.views[I][kp]
            P=self.points[p]
            assert I in P.views, "scene point "+str(P.id)+" lacks view "+str(I)
            assert kp in [v.id_keypoint for v in P.views[I]] , "scene point "+str(P.id)+" lacks view point "+str((I,kp))
        #from points to view, assert existence and reference to the point
        for p in self.points:
            P=self.points[p]
            for I in P.views:
                assert I in self.views, "view {} is in scene point {} but in the view index".format(I,p)
                for kp in [v.id_keypoint for v in P.views[I]]:
                    assert kp in self.views[I], "view point {} is in scene point {} but not in view index".format((I,kp),p)
                    assert p==self.views[I][kp] ,"view point {} is in scene point {} but point to {}".format((I,kp),p,self.views[I][kp])
        return True
    def viewGroupQuery(self,views):
        if type(views)==list:
            vv=set([v.id_image for v in views])
            vv={v_id:[v for v in views if v.id_image == v_id] for v_id in vv}
            return self.viewGroupQuery(vv)
        point_ids=[];
        for v_id in views:
            for v in views[v_id]:
                kp_id=v.id_keypoint
                if self.hasView(v_id,kp_id):
                    point_id=self.views[v_id][kp_id]
                    #linea di controllo , costosa da computare, si puo togliere 
                    #controlla che la vista sia effettivamente presente nel punto
                    #assert(len([v for v in self.points[point_id].views[v_id] if ((v.id_image==v_id) and ( v.id_keypoint == kp_id)) ])>0)
                    point_ids.append(point_id)
        return list(set(point_ids))
    def __str__(self):
        return 'transitive closure:\n'+'\n'.join([str(p) for p in self.points.values()])
    def _insertPoint(self,point,onLock=None):
        assert(point.id==0)
        if len(self.freePoints)>0:
            point.id=self.freePoints.pop()
            #print "found a free point name ",point.id, " from ",self.freePoints
        else :
            self.max+=1
            point.id=self.max
            #print "next maximum ",point.id , " no free points"
        assert(not point.id in self.points)
        self.points[point.id]=point
        for view in point.allViews():
            self.setView(view.id_image,view.id_keypoint,point.id,onLock=onLock)
        return
    def removePoint(self,point_id,removeViews=True):
        assert(point_id in self.points)
        if removeViews:
            for v in self.points[point_id].allViews():
                try:
                    assert(self.views[v.id_image][v.id_keypoint]==point_id )
                    del self.views[v.id_image][v.id_keypoint]
                except:
                    pass
        del self.points[point_id]
        if self.max!=point_id:
            self.freePoints.append(point_id)
        elif self.max>1 :
            self.max-=1
        elif self.max==1 and len(self.points)==0:
            self.max=0
            self.freePoints=[]
        while self.max in self.freePoints:
            self.freePoints.remove(self.max)
            self.max-=1
        return
    def lockPoint(self,p, label=-1):
        """mark the scene point and all its view points as locked with some lock label"""
        lockedViews=[v.key() for v in p.allViews()]
        for im,kp in lockedViews:
            self.views[im][kp]=label
        del self.points[p.id]
        return lockedViews
    def removeLockedPoints(self,point_id):
        for v in self.points[point_id].allViews():
            assert(self.views[v.id_image][v.id_keypoint]<0 )
        del self.points[point_id]
        if point_id==self.max :
            self.max-=1
            while self.max in self.freePoints:
                self.max-=1
        else:
            self.freePoints.append(point_id)
        return
    def add_edge(self,v1,v2,radius=4.):
        i1,kp1=v1.key()
        i2,kp2=v2.key()
        if self.hasView(i1,kp1):
            p1=self.viewQuery(i1,kp1)
            if self.hasView(i2,kp2):
                p2=self.viewQuery(i2,kp2)
                if not p1==p2:
                    # H1,H2
                    viewList=self.points[p1].allViews()+self.points[p2].allViews()
                    #new_point=self.newPoint(viewList)
                    self.removePoint(p1)
                    self.removePoint(p2)
                    new_point=self.newPoint(viewList) 
            else :
                #H1
                self.points[p1].add_view(v2)
                self.setView(i2,kp2,p1)   
        else :
            if self.hasView(i2,kp2):
                #H2
                p2=self.viewQuery(i2,kp2)
                self.points[p2].add_view(v1)
                self.setView(i1,kp1,p2)
            else:
                #NEW
                self.newPoint([v1,v2])
        return
    def newPoint(self,views):
        pointId=0 
        p=point(pointId,views)
        self._insertPoint(p)
        return p
    def closure(self,trc2):
        for p2Id in trc2.points.keys():
            p2=trc2.points[p2Id]
            assert(p2Id>0)
            self.add_point(p2,lock_label=-p2Id)
        return 
    def robust_closure(self,trc2,gEpG,radius=4.):
        #print "[robust_closure] with Global view informations: ",   gEpG
        for p2Id in trc2.points.keys():
            p2=trc2.points[p2Id]
            assert(p2Id>0)
            self.robust_add_point(p2,gEpG,radius=radius,lock_label=-p2Id)
        return self
    @staticmethod
    def fromMatchList(matches,im_i,im_j,
        kp_i=None,kp_j=None,ft_i=None,ft_j=None,Fij=None):
        tr=transitiveclosure()
        if matches is None or len(matches)<12:
            return tr
        has_kp=(type(kp_i)==np.ndarray) and (type(kp_j)==np.ndarray)
        has_ft=(type(ft_i)==np.ndarray) and (type(ft_j)==np.ndarray)
        if has_kp and has_ft:
            for ei,e in enumerate(matches):
                i,j=e
                _kp_i=kp_i[i]
                _kp_j=kp_j[j]
                _ft_i=ft_i[i]
                _ft_j=ft_j[j]
                v1=view(im_i,i,_kp_i[0],_kp_i[1])
                v2=view(im_j,j,_kp_j[0],_kp_j[1])
                v1.feature(f=_ft_i)
                v2.feature(f=_ft_j)
                tr.add_edge(v1,v2)
        elif has_kp:
            for ei,e in enumerate(matches):
                i,j=e
                _kp_i=kp_i[i]
                _kp_j=kp_j[j]
                v1=view(im_i,i,_kp_i[0],_kp_i[1])
                v2=view(im_j,j,_kp_j[0],_kp_j[1])
                tr.add_edge(v1,v2)
        else:
            for ei,e in enumerate(matches):
                i,j=e
                v1=view(im_i,i,-1,-1)
                v2=view(im_j,j,-1,-1) 
                tr.add_edge(v1,v2)
        #tr.assert_every_point_indexed_exist()
        if type(Fij) is np.ndarray:
            print len(tr.points) , "2 view tracks to be filtered"
            filtered_tr=transitiveclosure()
            for track in tr.points.values():
                for new_track in simpleFilter(track,im_i,im_j,Fij,radius=16.):
                    filtered_tr.newPoint(new_track.allViews())
            return filtered_tr
        else:
            return tr
    def add_view_definition(self,im_i,kp,ft):
        for p_id in list(self.points):
            if self.points[p_id].views.has_key(im_i):
                for v in self.points[p_id].views[im_i]:
                    kp_id=v.id_keypoint
                    pointOnImage=kp[kp_id]
                    v.u=pointOnImage[0]
                    v.v=pointOnImage[1]
                    if np.any(ft) :
                        v.feature(ft[kp_id])
        return self
    def query_image_intersection(self,image_ids):
        points=set()
        for im_id in self.views.keys():
            points_here=set(self.views[im_id].values())
            points.intersection_update(points_here)
        return points
    def query_image_union(self,image_ids):
        points=set()
        for im_id in self.views.keys():
            points_here=set(self.views[im_id].values())
            points.update(points_here)
        return points           
    def query_image_pair(self,image_id_i,image_id_j,VI,VIH):
        points=self.query_image_list([image_id_i,image_id_j],VI,VIH)
        matches=[]
        kpI=[]
        kpJ=[]
        for p in points:
            for vi in p.views[image_id_i]:
                for vj in p.views[image_id_j]:
                    matches.append((vi.id_keypoint, vj.id_keypoint))
                    kpI.append([vi.u,vi.v])
                    kpJ.append([vj.u,vj.v])
        return matches,kpI,kpJ
    def findFoundamentalMat(self,image_id_i,image_id_j):
        matches,kpI,kpJ=self.query_image_pair(image_id_i,image_id_j)
        if len(matches)<10:
            return None
        ptI=np.array(kpI)
        ptJ=np.array(kpJ)
        F,Mask=cv2.findFoundamentalMat(ptI,ptJ)
        return F
    def prune(self,minimum_visibility):
        newTR=transitiveclosure()
        k=minimum_visibility
        for p_id in self.points.keys():
            if len(self.points[p_id].views)>=k:
                newViews=reduce(lambda l1,l2:l1+l2,self.points[p_id].views.values(),[])
                np=newTR.newPoint(newViews)
        return newTR
    def prune_in_place(self,minimum_visibility):
        k=minimum_visibility
        for p_id in self.points.keys():
            if len(self.points[p_id].views)<k:
                self.removePoint(p_id)
        return 
    def viewIndex(self):
        VI={} #mappa im_id->[points]
        for p_id in self.points:
            p=self.points[p_id]
            for im_id in p.views:
                if VI.has_key(im_id):
                    VI[im_id].append(p_id)
                else:
                    VI[im_id]=[p_id]
        return VI
    def add_point(self,p2,lock_label=-1):
        if True:
            L=self.viewGroupQuery(p2.views);
            if len(L)==0:
                self.newPoint(p2.allViews())
                return
            #L è la popolazione di punti in self che interagiscono con p2
            locked_points=[self.points[l] for l in L]
            #print "[] adding :",p2," matching points ",locked_points
            locked_views=[]
            for p1 in locked_points:
                locked_views+=self.lockPoint(p1, label=lock_label)
            #now self should be in a correct transient state
            #se le proprietà delle equivalenze sono rispettate non serve acquisire un lock anche sui punti
            new_points=synthPoints(p2,locked_points)
            new_views=set([v.key() for p in new_points for v in p.allViews()])
            for new_point in new_points:
                self._insertPoint(new_point,onLock=lock_label)
            #clean missing view points from the view index
            missing_views_to_clear=set(locked_views)
            missing_views_to_clear.difference_update(new_views)
            for im,kp in missing_views_to_clear:
                assert(self.views[im][kp]==lock_label)
                del self.views[im][kp]
        return
    def robust_add_point(self,p2,gEpG,radius=4.,lock_label=-1):
        if len(gEpG)>0:
            L=self.viewGroupQuery(p2.views);
            if len(L)==0:
                self.newPoint(p2.allViews())
                return
            #L è la popolazione di punti in self che interagiscono con p2
            locked_points=[self.points[l] for l in L]
            #print "[] adding :",p2," matching points ",locked_points
            locked_views=[]
            for p1 in locked_points:
                locked_views+=self.lockPoint(p1, label=lock_label)
            #now self should be in a correct transient state
            #se le proprietà delle equivalenze sono rispettate non serve acquisire un lock anche sui punti
            new_points=robustSynthPoints(p2,locked_points,gEpG,radius)
            new_views=set([v.key() for p in new_points for v in p.allViews()])
            for new_point in new_points:
                self._insertPoint(new_point,onLock=lock_label)
            #clean missing view points from the view index
            missing_views_to_clear=set(locked_views)
            missing_views_to_clear.difference_update(new_views)
            for im,kp in missing_views_to_clear:
                assert(self.views[im][kp]==lock_label)
                del self.views[im][kp]
        return
        
def matches2tracks(tup):
    matches,im_i,im_j,kp_i,kp_j,Fij=tup
    tr=transitiveclosure.fromMatchList(
        matches,im_i,im_j,kp_i=kp_i,kp_j=kp_j,Fij=Fij)
    print "[matches2tracks] ",im_i,im_j,",",len(matches),"=>",len(tr.points)
    return tr
def robust_closure(trc1,trc2,gEpG,radius=4.):
    if trc1.view_number()>trc2.view_number():
        return trc1.robust_closure(trc2,gEpG,radius=radius)
    else:
        return trc2.robust_closure(trc1,gEpG,radius=radius)
def track_closure(trc1,trc2):
    return trc1.closure(trc2)
def robust_add_point(trc1,p2,gEpG,radius=4.,lock_label=-1):
    return trc1.robust_add_point(p2,gEpG,radius=radius,lock_label=lock_label) 
def add_point(trc1,p2,lock_label=-1):
    return trc1.add_point(p2,lock_label=lock_label) 

"""
validationReport:
    merge       : True means P and Q should be merged, False they should be kept apart
with merge==True
    P_exclude   : indices of the views of P that are not reliable and should be removed
    Q_exclude   : indices of the views of Q that are not reliable and should be removed
    R           : a dictionary of expected observations {I:pt}
                  I is the index of the view , pt is a 2d point on that view
                  viewpoints of PxQ on I are expected to be near pt
with merge==False
    PQ          : a dictionary of expected observations {I:(ptP,ptQ)} for points P and Q
                  common viewpoints should go in the scenepoint that has the nearest expected observation
                    
"""

def hard_merge(p,q):
    PuQ=point(0,[])
    inserted=set()
    for v in (p.allViews()+q.allViews()):
        if not v.key() in inserted:
            inserted.add(v.key())
            PuQ.add_view(v)
    return PuQ
def merge(vr,p,q,radius=4.,permissiveLimit=4):
    PuQ=point(0,[])
    inserted=set()
    for im_id in vr.R:
        permissive=False
        samples=0
        pt=vr.R[im_id]
        if im_id in p.views:
            for v in p.views[im_id]:
                key=v.key()
                dist=np.linalg.norm(vr.R[im_id]-v.pt())
                if (dist<radius or permissive) and not key in inserted:
                    inserted.add(v.key())
                    PuQ.add_view(v)
        if im_id in q.views:
            for v in q.views[im_id]:
                key=v.key()
                dist=np.linalg.norm(vr.R[im_id]-v.pt())
                if (dist<radius or permissive) and not key in inserted:
                    inserted.add(v.key())
                    PuQ.add_view(v)
    if not PuQ.not_empty():
        print 'empty point from merge' 
        #ipdb.set_trace()
    return PuQ

def split(vr,p,q):
    A=[v.key() for I in vr.PQ for v in p.views[I] ]
    B=[v.key() for I in vr.PQ for v in q.views[I] ]
    commonViews=set(A).intersection(B)
    for k in commonViews:
        im_id=k[0]
        p_center,q_center=vr.PQ[im_id]
        pt=[v for v in p.views[im_id] if v.id_keypoint==k[1]][0].pt()
        p_better_than_q=(
            np.linalg.norm(p_center-pt)
            <
            np.linalg.norm(q_center-pt)
            )   
        if p_better_than_q:
            to_be_removed=[v for v in q.views[im_id] if v.id_keypoint==k[1]][0]
            q.views[im_id].remove(to_be_removed)
            if len(q.views[im_id])==0:
                del q.views[im_id]
        else:
            to_be_removed=[v for v in p.views[im_id] if v.id_keypoint==k[1]][0]
            p.views[im_id].remove(to_be_removed)
            if len(p.views[im_id])==0:
                del p.views[im_id]
    #assert p.not_empty() , 'empty point from split'
    #assert q.not_empty(), 'empty point from split'
    return p,q
        
from validation.noValidation import noValidation
def robustSynthPoints(leader,followers,gEpG,radius):
    new_points=[]
    new_leader=point(0,leader.allViews())
    for p_old in followers:
        p=point(0,p_old.allViews())
        validation_report=validation(new_leader,p,gEpG,radius)
        if validation_report.merge:
            new_leader=merge(validation_report,new_leader,p,radius=radius,permissiveLimit=4)
        else:
            new_leader,q=split(validation_report,new_leader,p)
            new_points.append(q)
    new_points.append(new_leader)
    #dubbio: è dimostrabile l' unicità delle viste dentro new_points?
    return new_points

def synthPoints(leader,followers):
    new_points=[]
    new_leader=point(0,leader.allViews())
    for p_old in followers:
        p=point(0,p_old.allViews())
        new_leader=hard_merge(new_leader,p)
    new_points.append(new_leader)
    #dubbio: è dimostrabile l' unicità delle viste dentro new_points?
    return new_points


def propagation(selected,all_matches,views=None):
    if not views:
        A=set([m[0] for m in selected])
        B=set([m[1] for m in selected])
    elif type(views)==tuple:
        A=set([v.id_keypoint for v in views[0]])
        B=set([v.id_keypoint for v in views[1]])
    elif type(views)==list:
        A=set(view[0])
        A=set(view[1])
    next=[m for m in all_matches if m[0] in A or m[1] in B]
    if len(next)==len(selected):
        return next
    else:
        return propagation(next,all_matches)


def pickle_load_tracks(filename):
    with open(filename) as fin:
        T=pickle.load(fin)
    return T

def pickle_save_tracks(T,filename):
    with open(filename,'w') as fo:
        pickle.dump(T,fo)

def load_tracks(filename):
    if (
            ('.' in filename )
        and ('pk' in filename.split('.')[-1])
        ):
        return pickle_load_tracks(filename)
    else:
        return protobuf_load_tracks(filename)

def save_tracks(T,filename):
    if (
            ('.' in filename )
        and ('pk' in filename.split('.')[-1])
        ):
        return pickle_save_tracks(T,filename)
    else:
        return protobuf_save_tracks(T,filename)

def serialize_partition(part):
    pb_part=closure_pb2.Partition()
    for t in tqdm(part.points.values(),"serializing partition"):
        pb_t=pb_part.tracks.add()
        for v in t.allViews():
            pb_v = pb_t.views.add()
            pb_v.image=v.id_image
            pb_v.keypoint=v.id_keypoint
            pb_v.u=v.u
            pb_v.v=v.v
    return pb_part.SerializeToString()

def pbView(v):
    return view(v.image,v.keypoint,v.u,v.v)

def parse_partition(pb_blob):
    pb_part = closure_pb2.Partition()
    pb_part.ParseFromString(pb_blob)
    partition = transitiveclosure()
    for pb_t in tqdm(pb_part.tracks,"reading partition"):
        V=[pbView(pb_v) for pb_v in pb_t.views]
        t= point(0,V)
        partition._insertPoint(t)
    return partition

def protobuf_save_tracks(T,filename):
    serialize_partition(T)
    with open(filename,'wb') as fout:
        fout.write(serialize_partition(T))

def protobuf_load_tracks(filename):
    with open(filename,'rb') as fin:
        pb_blob=fin.read()
        partition=parse_partition(pb_blob)
    return partition
        
