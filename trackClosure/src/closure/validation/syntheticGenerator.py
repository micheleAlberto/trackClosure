from deprecator import deprecated
from itertools import product,combinations
from random import choice


from oracle import Oracle
from score import iterativeScoreBoard
def tfPartitions(V,Pval,Qval,case):
    if len(V)==0:
        return []
    if len(V)==1:
        return interpretation(V[0],Pval,Qval,case)
    else:
        VV=tfPartitions(V[1:],Pval,Qval,case)
        t=[x+v for v in VV for x in interpretation(V[0],Pval,Qval,case)]
        return t


def interpretation(v,Pval,Qval,case):
    if type(v)==int and case==0:
        p,q=Pval[v],Qval[v]
        assert('?' not in [p,q])
        if 'x' in [p,q]:
            #print v,p,q,'x'
            return [[True],[False]]
        elif p==q:
            #print v,p,q,True
            return [[True]]
        else :
            #print v,p,q,False
            return [[False]]
    elif type(v)==tuple:
        if case==1:
            i,j,k=v
            p1,p2,q=Pval[i],Pval[j],Qval[k]
            assert('?' not in [p1,p2,q] )
            if 'x' in [p1,p2,q]:
                #print i,j,k,p1,p2,q,'x'
                return [[True],[False]]
            elif p1==p2 and p2==q:
                #print i,j,k,p1,p2,q,True
                return [[True]]
            else:
                #print i,j,k,p1,p2,q,False
                return [[False]]
        elif case==2:
            i,k,l=v
            p,q1,q2=Pval[i],Qval[k],Qval[l]
            assert('?' not in [p,q1,q2])
            if 'x' in [p,q1,q2]:
                #print i,k,l,p,q1,q2,'x'
                return [[True],[False]]
            elif p==q1 and q1==q2:  
                #print i,k,l,p,q1,q2,True
                return [[True]]
            else:
                #print i,k,l,p,q1,q2,False
                return [[False]]
    assert(False)


class Schema:
#classe che rappresenta il problema costituito dall' unione di due punti nota l' associazione delle rispettive viste a punti reali
    def __init__(self,P,Q):
        assert(len(P)==len(Q))
        self.Pv=P
        self.Qv=Q
        self.commons=[]
        self.Q_only=[]
        self.P_only=[]
        for i,t in enumerate(zip(P,Q)):
            vp,vq=t
            if vp!='?' :
                if vq!='?':
                    self.commons.append(i)
                else:
                    self.P_only.append(i)
            else:
                if vq!='?':
                    self.Q_only.append(i)
        self.P=self.commons+self.P_only
        self.Q=self.commons+self.Q_only
        IJK,IKL,I=self.observations()
    def observations(self):
        self.IJK = [(i, j, k) for k in self.Q for i, j in combinations(self.P, 2) if k is not i and k is not j ]
        self.IKL = [(i, k, l) for i in self.P for k, l in combinations(self.Q, 2) if i is not k and i is not l]
        self.I = [i for i in self.commons]
        return self.IJK,self.IKL,self.I
    def expandX(self):
        Pval=self.Pv
        Qval=self.Qv
        IJK_v=tfPartitions(self.IJK,Pval,Qval,1)
        IKL_v=tfPartitions(self.IKL,Pval,Qval,2)
        I_v=tfPartitions(self.I,Pval,Qval,0)
        self.realizations=[(ijk_v,ikl_v,i_v) 
            for ijk_v in (IJK_v if len(IJK_v)>0 else [tuple()]) 
            for ikl_v in (IKL_v if len(IKL_v)>0 else [tuple()])
            for i_v in   (I_v   if len(I_v  )>0 else [tuple()])]
        return self.realizations
    @deprecated
    def clearCommons(self,I,inlier_I,P_inliers,P_outliers,Q_inliers,Q_outliers):
        Q_exclude=[]
        P_exclude=[]
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
                    Q_exclude.append(i)
                elif gq>gq and rq>rq:
                    P_exclude.append(i)
        return P_exclude,Q_exclude
    @deprecated
    def splitCommons(self,I,inlier_I,P_inliers,P_outliers,Q_inliers,Q_outliers):
        Q_exclude=[]
        P_exclude=[]
        for i,v in zip(I,inlier_I):
            pi=P_inliers[i]
            po=P_outliers[i]
            qi=Q_inliers[i]
            qo=Q_outliers[i]
            gp=pi-po
            gq=qi-qo
            if gp>gq :
                Q_exclude.append(i)
            else:
                P_exclude.append(i)
        return P_exclude,Q_exclude
    def mergeView(self,v,P_exclude,Q_exclude):
        Pv=self.Pv
        Qv=self.Qv
        if v in P_exclude and v in Q_exclude:
            return '?'
        elif v in P_exclude:
            return Qv[v]
        elif v in P_exclude:
            return Pv[v]
        elif Qv[v]==Pv[v]:
            return Pv[v]
        elif Qv[v]=='?':
            return Pv[v]
        elif Pv[v]=='?':
            return Qv[v]
        else:
            return 'x' 
    def scoring2exclude(self,realization):
        self.iSB=iterativeScoreBoard(
        self.P,self.Q,
        self.IJK,realization[0],
        self.IKL,realization[1],
        self.I,realization[2],Pe=[],Qe=[])
        iterations=0
        return self.iSB
    def scoring2merge(self,realization,ExcludeClassifier):
        self.iSB=iterativeScoreBoard(
        self.P,self.Q,
        self.IJK,realization[0],
        self.IKL,realization[1],
        self.I,realization[2],Pe=[],Qe=[])
        iterations=0
        while self.iSB.board.outliers_count > 0 and self.iSB.tick(ExcludeClassifier):
            iterations+=1
        return self.iSB
    @deprecated  
    def scoring2merge_old(self,realization,blameRatio=0.2):
        self.iSB=iterativeScoreBoard(
        self.P,self.Q,
        self.IJK,realization[0],
        self.IKL,realization[1],
        self.I,realization[2],Pe=[],Qe=[])
        g=self.iSB.board.gain()
        iterations=0
        while self.iSB.board.outliers_count > 0 and self.iSB.tick(acceptance=blameRatio)>g:
            g=self.iSB.board.gain()
            #print iterations , self.iSB.board.inliers_count ," vs ", self.iSB.board.outliers_count 
            iterations+=1
        return self.iSB
    @deprecated
    def scoring(self,realization,blameRatio=0.2):
        self.iSB=iterativeScoreBoard(
        self.P,self.Q,
        self.IJK,realization[0],
        self.IKL,realization[1],
        self.I,realization[2],Pe=[],Qe=[])
        g=self.iSB.board.gain()
        iterations=0
        while self.iSB.board.outliers_count > 0 and self.iSB.tick()>g:
            g=self.iSB.board.gain()
            #print iterations , self.iSB.board.inliers_count ," vs ", self.iSB.board.outliers_count 
            iterations+=1
        merge=self.iSB.board.gain()>0           
        if merge:
            P_exclude,Q_exclude=self.clearCommons(
                self.I,realization[2],
                self.iSB.board.P_inliers,
                self.iSB.board.P_outliers,
                self.iSB.board.Q_inliers,
                self.iSB.board.Q_outliers)
            self.iSB=iterativeScoreBoard(
                self.P,self.Q,
                self.IJK,realization[0],
                self.IKL,realization[1],
                self.I,realization[2],
                Pe=P_exclude,Qe=Q_exclude)
            g=self.iSB.board.gain()
            iterations=0
            while self.iSB.board.outliers_count > 0 and self.iSB.tick()>g:
                g=self.iSB.board.gain()
                #print iterations , self.iSB.board.inliers_count ," vs ", self.iSB.board.outliers_count 
                iterations+=1
            P_exclude=self.iSB.Pe
            Q_exclude=self.iSB.Qe
            out=[self.mergeView(i,P_exclude,Q_exclude) for i in range(len(self.Pv))]
            out=''.join(out)
        else:
            P_exclude,Q_exclude=self.splitCommons(
                self.I,realization[2],
                self.iSB.board.P_inliers,
                self.iSB.board.P_outliers,
                self.iSB.board.Q_inliers,
                self.iSB.board.Q_outliers)
            p_out=[self.Pv[i] if i not in P_exclude else '?' for i in range(len(self.Pv))]
            q_out=[self.Qv[i] if i not in Q_exclude else '?' for i in range(len(self.Qv))]
            out=[''.join(p_out),''.join(q_out)]
        return merge,P_exclude,Q_exclude,out
    def report(self):
        print ';'.join( 
            ['P{}+P{}->Q{}'.format(ijk[0],ijk[1],ijk[2]) for ijk in self.IJK]+
            [ 'P{}<-Q{}+Q{}'.format(ikl[0],ikl[1],ikl[2]) for ikl in self.IKL]+
            ['P{}-Q{}'.format(i,i) for i in self.I]+
            ['---']+
            ['merge','P exclude','Q exclude','output'])
        for r in self.realizations:
            s=self.scoring(r)
            print ';'.join(
                ['INlier' if b else 'OUTlier' for b in r[0]+r[1]+r[2]]+
                ['---']+
                ['merge' if s[0] else 'split' ,str(s[1]),str(s[2]),str(s[3])]
                )

class Generator():
#classe per generare casi di test con oracolo
    def __init__(self):
        pass
    def genPoints(self,logical_points,p_lenght):
        LS=logical_points+'?'
        point_generator = product(LS,repeat=p_lenght)      
        self.points=[''.join(p) for p in point_generator ]
        return self.points
    @deprecated
    def genMergeCase_old(self,filterFunc=None,blame=0.2):
        #use old manual exclude classifier so it s deprecated
        compliant=False
        x1,x2,Y=None,None,None
        while not compliant:
            x1='a'+choice(self.points)
            x2='a'+choice(self.points)
            Y=Oracle.mergeDecision(x1,x2)
            compliant=filterFunc(x1,x2,Y) if filterFunc else True
        #print x1,x2,'=>',Y
        s=Schema(x1,x2)
        R=s.expandX()[0]
        iSB=s.scoring2merge_old(R,blameRatio=blame)
        X=iSB.mergeInputModel()
        #X=IN,OUT,SUM,DIFF
        return X,Y
    def genMergeCase(self,ExcludeClassifier,filterFunc=None):
        compliant=False
        x1,x2,Y=None,None,None
        while not compliant:
            x1='a'+choice(self.points)
            x2='a'+choice(self.points)
            Y=Oracle.mergeDecision(x1,x2)
            compliant=filterFunc(x1,x2,Y) if filterFunc else True
        #print x1,x2,'=>',Y
        s=Schema(x1,x2)
        R=s.expandX()[0]
        iSB=s.scoring2merge(R,ExcludeClassifier)
        X=iSB.mergeInputModel()
        #X=IN,OUT,SUM,DIFF
        return X,Y
    @deprecated
    def genMergeCases_old(self,n,filterFunc=None):
        return [self.genMergeCase(filterFunc=filterFunc) for i in range(n)]
    def genMergeCases(self,n,ExcludeClassifier,filterFunc=None):
        XY=[self.genMergeCase(ExcludeClassifier,filterFunc=filterFunc) for i in range(n)]
        return zip(*XY)
    def genExcludeCaseGroup(self,filterFunc=None):
        x1,x2=None,None
        merge=False
        compliant=False
        while not (merge and compliant):
            x1='a'+choice(self.points)
            x2='a'+choice(self.points)
            merge=Oracle.mergeDecision(x1,x2)
            compliant=filterFunc(x1,x2,merge) if filterFunc else True
        s=Schema(x1,x2)
        R=s.expandX()[0]
        iSB=s.scoring2exclude(R)
        exP,exQ=iSB.excludeInputModels()
        exP_Y=Oracle.excludeOnMerge(x1)
        exQ_Y=Oracle.excludeOnMerge(x2)
        return zip(exP,[i in exP_Y for i in range(len(x1))])+zip(exQ,[i in exQ_Y for i in range(len(x2))])
    def genExcludeCases(self,n,filterFunc=None):
        cases=[]
        while len(cases)<n:
            cases+=self.genExcludeCaseGroup(filterFunc=filterFunc)
        return cases
