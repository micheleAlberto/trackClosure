from ...closure.point import point as Track

HARD_LIMIT=400
def split_views(V):
    sV=sorted(V,key=lambda v:v.u)
    l=len(sV)
    return sV[:l/2],sV[l/2:]

def split(t):
    va=[]
    vb=[]
    for v_id in t.views:
        a,b=split_views(t.views[v_id])
        va+=a
        vb+=b
    ta=Track(0,va)
    tb=Track(0,vb)
    return ta,tb

def safe_decomposition(tl):
    next_tl=[]
    has_splitted=False
    for t in tl:
        l=len(t.allViews())
        if l>HARD_LIMIT:
            ta,tb=split(t)
            la=len(ta.allViews())
            lb=len(tb.allViews())
            print "WARNING: track with {} splitted: {} + {}".format(l,la,lb)
            has_splitted=True
            next_tl.append(ta)
            next_tl.append(tb)
        else:
            next_tl.append(t)
    if has_splitted:
        return safe_decomposition(next_tl)
    else:
        return next_tl
    
    
    
    
    
