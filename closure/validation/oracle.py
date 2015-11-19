from collections import Counter



class Oracle:
#oracolo che definisce le risposte corrette note le associazioni viste-punti reali
    @staticmethod
    def dominant(x):
        s=x if type(x)==str else ''.join(x)
        if type(s)==str:
            counter=Counter(s.replace('?',''))
            if len(counter.keys())==0:
                return '?'
        return counter.most_common(1)[0][0]
    @staticmethod
    def dominants(x):
        s=x if type(x)==str else ''.join(x)
        if type(s)==str:
            counter=Counter(s.replace('?',''))
            if len(counter.keys())==0:
                return '?'
        tups=counter.most_common()
        ds=[ t[0] for t in tups if tups[0][1]==t[1]]
        return ds
    @staticmethod
    def mergeResult(P,Q):
        d=Oracle.dominant(P)
        R=''.join(d if d in [P[i],Q[i]] else '?' for i in range(len(P)))
        return R
    @staticmethod
    def splitResult(P,other):
        Q=other
        d=Oracle.dominant(P)
        NP=''.join(d if d in [P[i],Q[i]] else '?' for i in range(len(P)))
        return NP
    @staticmethod
    def excludeOnMerge(P):
        ds=Oracle.dominants(P)
        E=[i for i,v in enumerate(P) if not v in ds and v!='?']
        return E
    @staticmethod
    def mergeDecision(P,Q):
        P_ds=Oracle.dominants(P)
        Q_ds=Oracle.dominants(Q)
        return len([c for c in P_ds if c in Q_ds])>0
    @staticmethod
    def mergeDecision_old(P,Q):
        return Oracle.dominant(P)==Oracle.dominant(Q)
    @staticmethod
    def value(p,q):
        return p if (p==q or q=='?' ) else q if p=='?' else '?'
