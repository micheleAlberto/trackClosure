#!/usr/bin/env python
#coding: utf8
from itertools import groupby, chain, ifilter, combinations, product
import numpy as np
import cv2
import collections
from collections import Counter
from random import choice
import sys
from compactRepresentation import compactPoint
from mergeReport import validationReport
from score import iterativeScoreBoard
from classifiers import getExcludeClassifier,getMergeClassifier
from deprecator import deprecated


ExcludeClassifier=getExcludeClassifier()
MergeClassifier=getMergeClassifier()

#generatore di triplette (i,j,k) con
# i,j in P
# k in Q
# Fik e Fjk definite
@deprecated
def possible_reprojections(P_list, Q_list, PQ_EpG):
    for i, j in combinations(P_list, 2):
        for k in Q_list:
            if (i, k) in PQ_EpG and (j, k) in PQ_EpG:
                #print "yield possible reprojection:", i, j, k
                yield (i, j, k)

def observations(P_list, Q_list, PQ_EpG):
    IJK = [(i, j, k) for k in Q_list for i, j in combinations(P_list, 2) if (i, k) in PQ_EpG and (j, k) in PQ_EpG ]
    IKL = [(i, k, l) for i in P_list for k, l in combinations(Q_list, 2) if (k, i) in PQ_EpG and (l, i) in PQ_EpG ]
    I = [ i for i in P_list if i in Q_list]
    IJK=np.array(IJK)
    IKL=np.array(IKL)
    I=np.array(I)
    return IJK,IKL,I



#filtra le geometrie epipolari che incrociano due punti
def cross_EpG(Global_EpG, P_list, Q_list):
    xEpG = {
        (i, j): Global_EpG[i, j] 
        for i in P_list 
        for j in Q_list 
        if Global_EpG.has_key((i, j)) }
    xEpG_T = {
        (j, i):Fij.T 
        for (i, j), Fij in xEpG.iteritems() }
    xEpG.update(xEpG_T)
    #print "cross EpG : ",len(xEpG), " epipolar constraints"
    return xEpG

@deprecated
def pointTransfer(Fik, Fjk, mi, mj):
    #based on trifocal geometry
    #see http://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/FUSIELLO4/tutorial.html#x1-350005.1
    #1) Homogeneus coordinates
    #mi=np.array([vi.u,vi.v,1])
    #mj=np.array([vj.u,vj.v,1])
    #2) Epilines of points in I and J on K
    epiK = np.dot(Fik, mi)
    epjK = np.dot(Fjk, mj)
    #3) intersection of said epilines
    mk = np.cross(epiK, epjK)
    mk = mk/mk[2]
    return np.array([mk[0], mk[1]])

def pointTransferVectorized(P,Q,rEpG,maxLevel=8,alfa=0.8,IJK=None,IKL=None,I=None):
    #riempire buffer di memoria-IJK
    inlier_IJK=np.array([])
    rkp=np.array([])
    if len(IJK)>0:
        Fik=np.array([ rEpG[(ijk[0],ijk[2])] for ijk in IJK])
        Fjk=np.array([ rEpG[(ijk[1],ijk[2])] for ijk in IJK])
        mi=np.array([P[i][1] for i in IJK[:,0]])
        mj=np.array([P[j][1] for j in IJK[:,1]])
        kp=np.array([Q[k][1][0:2] for k in IJK[:,2]])
        level=np.array([ 
            max(Q[ijk[2]][2], P[ijk[0]][2], P[ijk[1]][2])*alfa+maxLevel*(1-alfa) 
            for ijk in IJK ])
        #calcolo effettivo:
        product=np.tensordot(Fik,mi,(2,1))
        EpIonK=np.array([product[i,:,i] for i in range(len(product))])
        product=np.tensordot(Fjk,mj,(2,1))
        EpJonK=np.array([product[i,:,i] for i in range(len(product))])
        MK=np.cross(EpIonK,EpJonK)
        rkp=(MK.T/MK[:,2]).T[:,0:2]
        dist=np.linalg.norm(kp-rkp,axis=1)
        inlier_IJK=dist<level
    inlier_IKL=np.array([])
    rip=np.array([])
    #riempire buffer di memoria IKL
    if len(IKL)>0:
        Fki=np.array([ rEpG[(ikl[1],ikl[0])] for ikl in IKL])
        Fli=np.array([ rEpG[(ikl[2],ikl[0])] for ikl in IKL])
        mk=np.array([Q[ikl[1]][1] for ikl in IKL])
        ml=np.array([Q[ikl[2]][1] for ikl in IKL])
        ip=np.array([P[ikl[0]][1][0:2] for ikl in IKL])
        level=np.array([ 
            max(Q[ikl[1]][2], Q[ikl[2]][2], P[ikl[0]][2])*alfa+maxLevel*(1-alfa) 
            for ikl in IKL ])
        #calcolo effettivo:
        product=np.tensordot(Fki,mk,(2,1))
        EpKonI=np.array([product[i,:,i] for i in range(len(product))])
        product=np.tensordot(Fli,ml,(2,1))
        EpLonI=np.array([product[i,:,i] for i in range(len(product))])
        MI=np.cross(EpKonI,EpLonI)
        rip=(MI.T/MI[:,2]).T[:,0:2]
        dist=np.linalg.norm(ip-rip,axis=1)
        inlier_IKL=dist<level
    inlier_I=np.array([])
    #riempire buffer di memoria - I
    if len(I)>0:
        mi_p=np.array([P[i][1][0:2] for i in I])
        mi_q=np.array([Q[i][1][0:2] for i in I])
        dist=np.linalg.norm(mi_p-mi_q,axis=1)
        level=np.array([ 
            max(Q[i][2],P[i][2])*alfa+maxLevel*(1.-alfa) 
            for i in I ])
        inlier_I=dist<level
    return inlier_IJK,rkp,inlier_IKL,rip,inlier_I








# clearCommons serve nel caso in cui un punto da unire (merge==True) presenti osservazioni non coerenti su un' immagine comune
#se i è la vista comune i appartiene a I e se i è incoerente inlier_I[i]==False
#in questo caso si mantiene la vista con maggior gain
@deprecated
def clearCommons(I,inlier_I,vr,P_inliers,P_outliers,Q_inliers,Q_outliers):
    for i,v in zip(I,inlier_I):
        if not v:
            pi=P_inliers[i]
            po=P_outliers[i]
            qi=Q_inliers[i]
            qo=Q_outliers[i]
            rp=pi/float(pi+po)
            rq=qi/float(qi+qo)
            gp=pi-po
            gq=qi-qo
            if gp>gq and rp>rq:
                vr.Q_exclude.add(i)
            elif gq>gq and rq>rq:
                vr.P_exclude.add(i)
@deprecated
def validation_old(Point_P, Point_Q, gEpG,radius,a=0.7):
    P = compactPoint(Point_P)
    P_list = P.keys()
    Q = compactPoint(Point_Q)
    Q_list = Q.keys()
    vr = validationReport(Point_P,P,Point_Q,Q)
    PQ_EpG = cross_EpG(gEpG,P_list,Q_list)
    #identificazione prove
    IJK,IKL,I=observations(P_list, Q_list, PQ_EpG)
    #osservazione
    inlier_IJK,rkp,inlier_IKL,rip,inlier_I=pointTransferVectorized(P,Q,PQ_EpG,maxLevel=radius,alfa=a,IJK=IJK,IKL=IKL,I=I)
    #calcolo punteggio
    inliers_count,outliers_count,P_inliers,Q_inliers,P_outliers,Q_outliers=score(P_list,Q_list,IJK,inlier_IJK,IKL,inlier_IKL,I,inlier_I)
    vr.R_in = inliers_count
    vr.R_out = outliers_count
    vr.merge=vr.R_in>vr.R_out
    if vr.merge :
        clearCommons(I,inlier_I,vr,P_inliers,P_outliers,Q_inliers,Q_outliers)
        qualityRatio=float(vr.R_in)/(vr.R_in+vr.R_out)
        P_worst = max(P_list, key=lambda I: P_outliers[I]-P_inliers[I] if I not in vr.P_exclude else -10000) 
        Q_worst = max(Q_list, key=lambda I: Q_outliers[I]-Q_inliers[I] if I not in vr.Q_exclude else -10000)
        P_gain = P_outliers[P_worst]-P_inliers[P_worst]
        Q_gain = Q_outliers[Q_worst]-Q_inliers[Q_worst]
        P_qualityRatio=P_inliers[P_worst]/float(P_inliers[P_worst]+P_outliers[P_worst]) if P_outliers[P_worst]>0 else 0.
        Q_qualityRatio=Q_inliers[Q_worst]/float(Q_inliers[Q_worst]+Q_outliers[Q_worst]) if Q_outliers[Q_worst]>0 else 0.
        if P_gain>0 and P_qualityRatio<qualityRatio and len(P_list)>2:
            vr.P_exclude.add(P_worst)
        if Q_gain>0 and Q_qualityRatio<qualityRatio and len(Q_list)>2:
            vr.Q_exclude.add(Q_worst) 
    return vr
            



def validation(Point_P, Point_Q, gEpG,radius,a=0.7):
    P = compactPoint(Point_P)
    P_list = P.keys()
    Q = compactPoint(Point_Q)
    Q_list = Q.keys()
    vr = validationReport()
    PQ_EpG = cross_EpG(gEpG,P_list,Q_list)
    #identificazione prove
    IJK,IKL,I=observations(P_list, Q_list, PQ_EpG)
    if len(IJK)+len(IKL)<4:
        vr.merge=True
        PE=[]
        QE=[]
        vr.setMerge(P,Q,PE,QE)
    #osservazione
    inlier_IJK,rkp,inlier_IKL,rip,inlier_I=pointTransferVectorized(P,Q,PQ_EpG,maxLevel=radius,alfa=a,IJK=IJK,IKL=IKL,I=I)
    #calcolo punteggio==>parte da rifare
    ISB=iterativeScoreBoard(P_list,Q_list,IJK,inlier_IJK,IKL,inlier_IKL,I,inlier_I)
    iterations=0
    while ISB.board.outliers_count > 0 and ISB.tick(ExcludeClassifier):
        iterations+=1
    #now the point is stable under worst point exclusion
    merge_x=ISB.mergeInputModel()
    vr.merge=MergeClassifier.predict(merge_x)
    if vr.merge:
        PE=ISB.Pe
        QE=ISB.Qe
        vr.setMerge(P,Q,PE,QE)
    else:
        vr.setSplit(P,Q,I)
    return vr       

