#!/usr/bin/env python
#coding: utf8 
from point import point
from itertools import combinations
import numpy as np
#strategia
#individuare la massima distanza tra osservazioni sulla stessa immagine
#effettuare una bipartizione che divida a metà le due osservazioni più distanti
def epiline(pt,F):
    h=np.array(pt.tolist()+[1.])
    l=np.dot( F , h.T )
    return l/np.linalg.norm(l[0:2])

def find_max_distance(V):
    if len(V)==1:
        return (0,0),0
    def distance(ij):
        i,j=ij
        _i=V[i].pt()
        _j=V[j].pt()
        return np.linalg.norm(_i-_j)
    ij=max((_ij for _ij in combinations(range(len(V)),2) ), key=distance)
    return ij,distance(ij)
#bipartizione
#input 2 viste dirette da separare,viste dirette , viste indirette
#individuare epipolari
#ciascuna vista diretta va alla separante più vicina
#ciascuna vista indiretta va all' epipolare più vicina
def bipartition(ab,direct,opposite,F):
    a_i,b_i=ab
    p_a=direct[a_i].pt()
    p_b=direct[b_i].pt()
    A_direct=[direct[a_i]]
    B_direct=[direct[b_i]]
    for d in direct:
        p_d=d.pt()
        if np.linalg.norm(p_d-p_a)<np.linalg.norm(p_d-p_b):
            A_direct.append(d)
        else:
            B_direct.append(d)
    epl_a=epiline(p_a,F)
    epl_b=epiline(p_b,F)
    A_opposite=[]
    B_opposite=[]
    for o in opposite:
        oh=np.array(o.pt().tolist()+[1.])
        if np.dot(oh,epl_a)<np.dot(oh,epl_b):
            A_opposite.append(o)
        else:
            B_opposite.append(o)
    A=point(0,A_direct+A_opposite)
    B=point(0,B_direct+B_opposite)
    return A,B


def simpleFilter(p,I,J,Fij,radius=4.):#->[p1,p2.. pn]
    if len(p.views)<2:
        #print "empty view"
        return []
    if len(p.views[I])==0 or len(p.views[J])==0:
        #print "empty view"
        return []
    ij_I,max_distance_I=find_max_distance(p.views[I])
    ij_J,max_distance_J=find_max_distance(p.views[J])
    if max(max_distance_I,max_distance_J)<radius:
        #print "correct point"
        return [p]
    if max_distance_I>max_distance_J:
        A,B=bipartition(ij_I,p.views[I],p.views[J],Fij)
    else:
        A,B=bipartition(ij_J,p.views[J],p.views[I],Fij.T)
    return simpleFilter(A,I,J,Fij,radius=radius)+simpleFilter(B,I,J,Fij,radius=radius)
