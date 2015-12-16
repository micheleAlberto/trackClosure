from deprecator import deprecated

def _internal_distance(x):
    D=[np.linalg.norm(x1-x2) for x1 in x for x2 in x]
    return np.average(D),max(D)
def _relative_distance(x,c):
    D=[np.linalg.norm(x1-c) for x1 in x]
    return np.average(D),max(D)
def _view_quality(P,compact,I):
    center=compact[I][1][:2]
    X=np.array([[v.v, v.u] for v in P.views[I] ])
    AvgI,MaxI=_internal_distance(X)
    AvgR,MaxR=_relative_distance(X,center)
    return AvgI,MaxI,AvgR,MaxR


class pointQuality(object):
    @deprecated
    def __init__(self,P,compactP):
        self.point_id=P.id
        self.views=len(P.allViews())
        self.images=len(P.views)
        Is=P.views.keys()
        rIs=range(len(Is))
        table=[list(_view_quality(P,compactP,I)) for I in Is]
        #AvgI,MaxI,AvgR,MaxR
        self.AverageInternalError=sum( table[I][0]*float(len(P.views[Is[I]])) for I in rIs)/sum(len(P.views[Is[I]]) for I in rIs)
        self.WorstAverageInternalError= max(table[I][0] for I in rIs)
        self.AverageWorstInternalError= np.average([table[I][1] for I in rIs])
        self.WorstInternalError= max(table[I][1] for I in rIs)
        self.AverageCenterError=sum( table[I][2]*float(len(P.views[Is[I]])) for I in rIs)/sum(len(P.views[Is[I]]) for I in rIs)
        self.WorstAverageCenterError= max(table[I][2] for I in rIs)
        self.AverageWorstCenterError= np.average([table[I][3] for I in rIs])
        self.WorstCenterError= max(table[I][3] for I in rIs)
        self.MaxRadius=max(compactP[I][2] for I in Is)
        self.MinRadius=min(compactP[I][2] for I in Is)
        self.AverageRadius=np.average([compactP[I][2] for I in Is])


class validationReportWithLogging(object):
#classe che rappresenta l' output di un operazione di validazione con supporto per i log
    @deprecated
    def __init__(self,P,compactP,Q,compactQ):
        self.P_quality=pointQuality(P,compactP)
        self.Q_quality=pointQuality(Q,compactQ)
        self.R_quality=None
        self.P_exclude = set()
        self.Q_exclude = set()
        self.merge = False
        self.R_in = 0
        self.R_out = 0
    @deprecated
    def finalize(self,R):
        self.P_exclude=len(self.P_exclude)
        self.Q_exclude=len(self.Q_exclude)
        if self.merge and R:
            self.R_quality=pointQuality(R,compactPoint(R))
    def __str__(self):
        if self.merge:
            s="merge with {} inliers, {} outliers;".format(self.R_in,self.R_out)
            s+="P-{};Q-{}".format(self.P_exclude,self.Q_exclude)
            return s
        else:
            s="abort with {} inliers, {} outliers;".format(self.R_in,self.R_out)
            return s


def merge_synthesis(P,Q,PE,QE):
    R_list=list(set(P.keys()+Q.keys()))
    R = {}
    for I in R_list :
        p_valid=(I in P and not I in PE)
        q_valid=(I in Q and not I in QE)
        if p_valid and q_valid:
            p_pt = P[I][1][0:2]
            q_pt = Q[I][1][0:2]   
            r_pt = (p_pt+q_pt)/2
            R[I] = r_pt
        elif p_valid and not q_valid:
            p_pt = P[I][1][0:2]
            R[I] = p_pt
        elif (not p_valid) and  q_valid:
            q_pt = Q[I][1][0:2]
            R[I] = q_pt
        else :
            pass
    return R

def split_synthesis(P,Q,commons):
    R = {c:(P[c][1][0:2],Q[c][1][0:2]) for c in commons}
    return R


class validationReport(object):
#classe che rappresenta l' output di un operazione di validazione
    def __init__(self):
        self.merge = False
    def setMerge(self,P,Q,PE,QE):
        self.P_exclude = PE
        self.Q_exclude = QE
        self.R=merge_synthesis(P,Q,PE,QE)
    def setSplit(self,P,Q,commons):
        self.PQ=split_synthesis(P,Q,commons)
    def __str__(self):
        if self.merge:
            s="merge with "
            s+="P-{};Q-{}".format(self.P_exclude,self.Q_exclude)
            return s
        else:
            s="abort merge"
            return s
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
    PQ          : a dictionary of expected observations {I:(ptP,ptQ)} for both points P and Q
                  common viewpoints should go in the scenepoint that has the nearest expected observation
                    
"""
