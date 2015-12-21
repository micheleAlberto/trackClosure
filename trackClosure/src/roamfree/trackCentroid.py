

def centroid(views):
    if len(views)==1:
        return views[0]
    U,V=0.,0. 
    for view_point in views:
        U+=view_point.u
        V+=view_point.v
    U=U/len(views)
    V=V/len(views)
    best_sample=min(views, key=lambda view_point: pow((view_point.u-U),2)+pow((view_point.v-V),2) )
    return best_sample
        
