import scipy.spatial.Delaunay as Delauny

TriangulationTransfer=namedtuple('delauny triangulation',['src','dst','tri'])

def compute_structure(src_img,dst_img,part):
    track_ids=[t.id 
        for t in part.points.values() 
        if (src_img in t.views) 
        and (dst_img in t.views)]
    dst_pts=np.array([part[t_id].views[dst_img][0].pt() for t in t_id])
    src_pts=np.array([part[t_id].views[src_img][0].pt() for t in t_id])
    tri = Delaunay(dst_pts)
    tt=TriangulationTransfer(src_pts,dst_pts,tri)
    return tt

def all_pixels_in_triangle(_pts):   
    #this is called rasterization of a triangle
    bbox=min(_pts[:,0]),max(_pts[:,0]),min(_pts[:,1]),max(_pts[:,1])
    PX=(
        (x,y) 
        for x in range(bbox[0],bbox[1]) 
        for y in range(bbox[2],bbox[3]))
    return (px for px in PX if px in _pts)#TODO:http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle
    
def compute_layer(src_IM,dst_IM,tt):
    flow_size=(dst_IM.shape[0],dst_IM.shape[1],2)
    flow=np.zeros(flow_size,np.float)
    for triangle in tt.tri.simplices:
        src_pts=tt.src[triangle]
        dst_pts=tt.dst[triangle]
        M=cv2.getAffineTransform(src_pts, dst_pts)
        for x,y in dst_IM[triangle]:        
            flow[x,y]=np.dot(M,[x,y,1])
        mx,my=M
    return 



    for triangle in tri.simplices:
