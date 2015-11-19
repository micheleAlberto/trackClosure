#!/usr/bin/env python
# -*- coding: utf-8 -*-
from deprecator import deprecated

def score(P_list,Q_list,PPQ,PPQ_inliers,PQQ,PQQ_inliers,C,C_inliers,Pe=[],Qe=[]):
    P_inliers = {i:0 for i in P_list}
    Q_inliers = {i:0 for i in Q_list}
    P_outliers = {i:0 for i in P_list}
    Q_outliers = {i:0 for i in Q_list}
    inliers_count = 0
    outliers_count = 0
    for ijk,v in zip(PPQ,PPQ_inliers):
        i,j,k=ijk
        if not (i in Pe or j in Pe or k in Qe):
            if v:
                inliers_count += 1
                P_inliers[i] += 1
                P_inliers[j] += 1
                Q_inliers[k] += 1
            else :
                outliers_count += 1
                P_outliers[i] += 1
                P_outliers[j] += 1
                Q_outliers[k] += 1
    for ikl,v in zip(PQQ,PQQ_inliers):
        i,k,l=ikl
        if not (i in Pe or k in Qe or l in Qe):
            if v:
                inliers_count += 1
                P_inliers[i] += 1
                Q_inliers[k] += 1
                Q_inliers[l] += 1
            else :
                outliers_count += 1
                P_outliers[i] += 1
                Q_outliers[k] += 1
                Q_outliers[l] += 1
    for i,v in zip(C,C_inliers):
        if not (i in Pe or i in Qe):
            if v:
                inliers_count += 1
                P_inliers[i] += 1
                Q_inliers[i] += 1
            else:
                outliers_count += 1
                P_outliers[i] += 1
                Q_outliers[i] += 1
    return inliers_count,outliers_count,P_inliers,Q_inliers,P_outliers,Q_outliers

#classe che calcola i conteggi di inlier e outlier, generali e per vista
class ScoreBoard:
    def __init__(self,P_list,Q_list,PPQ,PPQ_inliers,PQQ,PQQ_inliers,C,C_inliers,Pe=[],Qe=[]):
        score(P_list,Q_list,PPQ,PPQ_inliers,PQQ,PQQ_inliers,C,C_inliers,Pe=[],Qe=[])
        (self.inliers_count, 
        self.outliers_count, 
        self.P_inliers, 
        self.Q_inliers, 
        self.P_outliers, 
        self.Q_outliers)=score(P_list,Q_list,PPQ,PPQ_inliers,PQQ,PQQ_inliers,C,C_inliers,Pe,Qe)
        self.gP={I:self.P_inliers[I]-self.P_outliers[I] for I in P_list}
        self.gQ={I:self.Q_inliers[I]-self.Q_outliers[I] for I in Q_list}
    def worstP(self):
        return min(self.gP,key=self.gP.get)
    def worstQ(self):
        return min(self.gQ,key=self.gQ.get) 
    def accountability_P(self,i):
        return float(self.P_outliers[i])/self.outliers_count
    def accountability_Q(self,i):
        return float(self.Q_outliers[i])/self.outliers_count
    def gain(self):
        return self.inliers_count-self.outliers_count

#classe che screma iterativamente le viste ricalcolando la scorebored e eliminando iterativamente quella peggiore
class iterativeScoreBoard:
    def __init__(self,P_list,Q_list,PPQ,PPQ_inliers,PQQ,PQQ_inliers,C,C_inliers,Pe=[],Qe=[]):
        self.Pe=Pe
        self.Qe=Qe
        self.P=P_list
        self.Q=Q_list
        self.IJK=PPQ
        self.IJK_v=PPQ_inliers
        self.IKL=PQQ
        self.IKL_v=PQQ_inliers
        self.I=C
        self.I_v=C_inliers
        self.update()
    def update(self):
        self.board=ScoreBoard(
                    self.P,self.Q,
                    self.IJK,self.IJK_v,
                    self.IKL,self.IKL_v,
                    self.I,self.I_v,
                    Pe=self.Pe, Qe=self.Qe)
    def mergeInputModel(self):
        #IN,OUT,pqSUM,pqDIFF
        IN=self.board.inliers_count
        OUT=self.board.outliers_count
        np=len(self.P)-len(self.Pe)
        nq=len(self.Q)-len(self.Qe)
        SUM=np+nq
        DIFF=np-nq if np>nq else nq-np
        return IN,OUT,SUM,DIFF
    def excludeInputModelP(self,i):
        #INi,OUTi,IN,OUT
        IN=self.board.inliers_count
        OUT=self.board.outliers_count
        INi=self.board.P_inliers[i]
        OUTi=self.board.P_outliers[i]
        return INi,OUTi,IN,OUT
    def excludeInputModelQ(self,i):
        #INi,OUTi,IN,OUT
        IN=self.board.inliers_count
        OUT=self.board.outliers_count
        INi=self.board.Q_inliers[i]
        OUTi=self.board.Q_outliers[i]
        return INi,OUTi,IN,OUT
    def excludeInputModels(self):
        XP=[self.excludeInputModelP(i) for i in self.P]
        XQ=[self.excludeInputModelQ(j) for j in self.Q]
        return XP,XQ
    @deprecated
    def tick_old(self,acceptance=0.2):
        wp=self.board.worstP()
        wq=self.board.worstQ()
        ap=self.board.accountability_P(wp)
        aq=self.board.accountability_Q(wq)
        if ap>acceptance or aq>acceptance:
            update=False
            if ap>aq and self.board.gP[wp]<0:
                update=True
                self.Pe.append(wp)
                #print 'worst P ',wp,ap
            elif self.board.gQ[wq]<0:
                update=True
                self.Qe.append(wq)
                #print 'worst Q ',wq,aq
            if update:
                self.update()
        return self.board.gain()
    def clearCommons(self,updateTable=False):
        need_update=False
        for i,Image in enumerate(self.I):
            if not self.I_v[i] and (not Image in self.Pe) and (not Image in self.Qe):
                gP=self.board.gP[Image]
                gQ=self.board.gQ[Image]
                if gP>gQ:
                    self.Qe.append(Image)
                else:
                    self.Pe.append(Image)
                need_update=True
        if updateTable and need_update:
            self.update()
        return self
    def tick(self,classifier):
        #esegue un iterazione della board:
        #seleziona degli elementi peggiori
        #li sottopone al vaglio del classificatore
        #li esclude se non risultano idonei
        #aggiorna la board
        #restituisce 
        #   true se il punto è stato modificato
        #   false se il punto è stabile
        wp=self.board.worstP()
        wq=self.board.worstQ()
        wp_x=self.excludeInputModelP(wp)
        wq_x=self.excludeInputModelQ(wq)
        wp_exclude=classifier.predict(wp_x)
        wq_exclude=classifier.predict(wq_x)
        need_update=False
        if wp_exclude:
            self.Pe.append(wp)
            need_update=True
        if wq_exclude:
            self.Qe.append(wq)
            need_update=True
        if need_update:
            self.update()
        return need_update
