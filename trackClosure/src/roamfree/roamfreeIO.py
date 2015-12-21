from trackCentroid import centroid

fictional_base=0
fictional_step=1000
fictional_counter=0

def write_rf_tracks(image_names,tracks,filename):
    I2TS={im_id:imageNameToTimestamp(I) for im_id,I in image_names.iteritems()}
    with open(filename,'w') as fp:
        for t_id,t in tracks.points.items(): 
            for v_id,V in t.views.items():
                ts=I2TS[v_id]
                obs=centroid(V)
                x,y=obs.u,obs.v
                fp.write("{},{},{},{},{}\n".format(ts,t_id,v_id,x,y))
    return

def write_rf_viewTimestamp(image_names,filename):
    with open(filename,'w') as fp:
        I2TS={im_id:imageNameToTimestamp(I) for im_id,I in image_names.iteritems()}
        for i in sorted(I2TS.keys()):
            fp.write("{},{}\n".format(i,I2TS[i]))

def write_rf_view_stats(tracks,filename='views.csv'):
    with open(filename,'w') as fp:
        I2TS={im_id:imageNameToTimestamp(I) for im_id,I in image_names.iteritems()}
        for I in tracks.views:
            V=tracks.views[I]
            ts=I2TS[I]
            points=list(set(V.values()))
            P2=len([p for p in points if len(tracks.points[p].views)>=2])
            P3=len([p for p in points if len(tracks.points[p].views)>=3])
            P4=len([p for p in points if len(tracks.points[p].views)>=4])
            P5=len([p for p in points if len(tracks.points[p].views)>=5])
            P6=len([p for p in points if len(tracks.points[p].views)>=6])
            O=len(V)
            fp.write("{},{},{},{},{},{}\n".format(ts,P2,P3,P4,P5,P6))


"""
    def export_greedy_order(self,tracks,filename='greedy')


def greedy(init_couple,V2P,P2V):
    def n_visibles(views,points,n):
        return len([p for p in points if len(views.intersection(P2V[p]))>=n])
    def score
    v0,v1=init_couple
    used_tracks=set(V2P[v0]+V2P[v1])
    """
        

                    
            
    
        

def imageNameToTimestamp(name):
    global fictional_counter
    splitted_name=name.split('_')
    try:
        return int(splitted_name[0])
    except:
        fictional_counter+=1
        return fictional_counter*fictional_step+fictional_base
        


