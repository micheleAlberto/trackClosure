import numpy as np
import cv2
from math import sin , cos
from colors import BLUE, GREEN, RED, YELLOW, PURPLE, PURPLO, COLORS

def drawView(img,v,color=(255,0,0),scale=12,angle=None,img_scale=1.):
    #print "Draw:",(v.u,v.v)
    p=(v.u/img_scale,v.v/img_scale)
    p=(int(p[0]), int(p[1]))
    cv2.circle(img,p,scale,color,3)
    if angle:
        q=(p[0]+cos(angle)*scale,p[1]+sin(angle)*scale)
        q=(int(q[0]), int(q[1]))
        cv2.line(img,p,q,color,lineType=cv2.CV_AA)
    
def drawViews(img,V,color):
    for i,v in enumerate(V):
        cv2.putText(img, '{}'.format(i), (v.u,v.v),cv2.FONT_HERSHEY_DUPLEX, 1, color) 
        cv2.circle(img,(v.u,v.v),12,color,3)

def drawEpiline(img,F,v,color=(0,255,0),label=False,img_scale=1.):
    h=np.array([v.u,v.v,1])
    ep=np.dot(F,h)
    x1=0
    x2=len(img[0])#*img_scale
    y1=(-(ep[2])/ep[1])/img_scale
    #y2=-(ep[2]+x2*ep[0])/ep[1]
    #print x1,x2 ,y1,y2
    #p1=(int(x1),int(y1))
    #len(img[0])*img_scale
    y2=-(ep[2]/img_scale+len(img[0])*ep[0])/ep[1]
    p1=(0,int(y1))
    p2=(int(x2),int(y2))
    cv2.line(img,p1,p2,color)
    if label:
        if type(label) is type(True):
            cv2.putText(img, '{}'.format(v.id_keypoint), p1,cv2.FONT_HERSHEY_DUPLEX, 1, color) 
        elif type(label) is type('string'):
            cv2.putText(img, label, p1,cv2.FONT_HERSHEY_DUPLEX, 1, color) 

def imgallery(images,show=False):
    t=tuple(images)
    I=np.hstack(t)
    if show:
        imshow(I)
    return I


    
def save_gallery(images,filename):
    t=tuple(images)
    I=np.hstack(t)
    cv2.imwrite(filename,I)
    return I
    
def imageToColorMap(imageBins):
    i2c={}
    i=0
    for I in imageBins:
        i2c[I.index]=COLORS[i%len(COLORS)]
        i+=1
    return i2c

def getIMG(i,labelColor=False):
    if type(i)==str:
        I=cv2.imread(i)
    else:
        I=i.imread()
    img=cv2.cvtColor(I,cv2.COLOR_GRAY2BGR)
    if labelColor:
        bottom_left=(0,len(img))
        cv2.putText(img, str(i.index), bottom_left,cv2.FONT_HERSHEY_DUPLEX, 10, labelColor) 
    return img

def filterEpG(gEpG, images):
    e={}
    for i in images:
        for j in images:
            if (i,j) in gEpG:
                e[(i,j)]=gEpG[(i,j)]
            elif (j,i) in gEpG:
                e[(i,j)]=gEpG[(j,i)].T
    return e

#def foo(tracks,imageBins):->np.ndarray 
#immagine opencv che visualizza le tracce sulle immagini
def visualize(track,imageBins,gEpG,save=False,show=False):
    i2c=imageToColorMap(imageBins)
    indexes=i2c.keys()
    epipolarGeometries=filterEpG(gEpG, indexes)
    images={I.index:getIMG(I,labelColor=i2c[I.index]) for I in imageBins}
    for i,img in images.iteritems():
        I=[I for I in imageBins if I.index==i][0]
        #draw views:
        I_archive = I.archive_read()
        if 'scale' in I_archive:
            scale = I_archive['scale']
        else :
            scale = False
        if 'angle' in I_archive:
            angle = I_archive['angle']
        else :
            angle=False
        for v in track.views[i]:
            kp_id=v.id_keypoint
            s=scale[kp_id] if scale else 12
            a=angle[kp_id] if angle else 0
            drawView(img,v,color=i2c[i],scale=s,angle=a)           
        #draw epilines:
        for v_id in track.views :
            if v_id is not i and (v_id,i) in epipolarGeometries:
                F=epipolarGeometries[(v_id,i)]
                for v in track.views[v_id]:
                    drawEpiline(img,F,v,color=i2c[v_id],label=True)
    ims=[images[k] for k in sorted(images.keys())]
    if save:
        return save_gallery(ims,save)
    return imgallery(ims,show=show)


        
        
