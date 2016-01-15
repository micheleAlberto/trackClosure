import numpy as np
import cv2
from ..closure.point import point
from ..trackvis import trackvis as vis
from ..trackAnalysis.trackAnalisys import computeMultiTrackShadows
COLORS=vis.COLORS
from random import choice
oracle_gui_help_text= """
key     actions:
 ->     next image
 <-     previus image
 up     next oracle
 dw     previus oracle
 n      new oracle
 d      delete oracle
 e      toggle epilines
 l      toggle labels
 q      quit
"""

def drawShadow(img,kp,img_scale,color,weak):
    p=(int(kp[0]/img_scale), int(kp[1]/img_scale))
    if weak:
        cv2.circle(img,p,3,color,2)
    else:
        cv2.circle(img,p,5,color,2)

def draw_shadows(img,S,img_scale,color=vis.RED,weak=False):
    for p in S:
        drawShadow(img,p,img_scale,color,weak)
    return img


class oracle_gui():
    def __init__(self,image_id2NameFunctor,gEpG,cc):     
        self.gEpG=gEpG
        print "reading ",len(gEpG)," epipolar geometries"
        self.cc=cc
        self.image_ids=sorted(cc.views.keys())
        self.view2oracle={}
        self.oracles=[0]
        self.current_oracle=self.oracles[0]
        self.oracle2color={0:COLORS[0]}
        self.current_image_id=self.image_ids[0]
        self.windowName='image'
        self.keep_gui_going=True
        self.draw_epilines=True
        self.draw_label=True
        self.draw_shadows=False
        self.draw_weak_shadows=False
        self.active_view=None
        self.t=0.;
        self.IMGS={i:cv2.imread(image_id2NameFunctor(i)) for i in self.image_ids}
        native_image_height,native_image_width,=self.IMGS.values()[0].shape[0:2]
        target_width=600
        self.scale=float(native_image_width)/target_width
        img_size=(target_width,int(native_image_height/self.scale))
        self.IMGS={i:cv2.resize(self.IMGS[i],img_size) for i in self.image_ids}
    def add_oracle(self,oracle_track):
        #add an oracle track to the gui, used to implement an edit function of the gui
        new_o=max(self.oracles)+1
        self.oracles.append(new_o)
        self.oracle2color[new_o]=COLORS[new_o%len(COLORS)]
        for v in oracle_track.allViews():
            v_id=(v.id_image,v.id_keypoint)
            self.view2oracle[v_id]=new_o
    def help(self):
        print oracle_gui_help_text
        return
    def toggle_epilines(self):
        self.draw_epilines= not self.draw_epilines
        print 'drawing epilines: ',self.draw_epilines
        return self.draw()
    def toggle_labels(self):
        self.draw_label= not self.draw_label
        print 'drawing labels: ',self.draw_label
        return self.draw()
    def right(self):
        i=self.image_ids.index(self.current_image_id)
        i=(i+1)%len(self.image_ids)
        self.current_image_id=self.image_ids[i]
        print 'current image: ',self.current_image_id
        return self.draw()
    def left(self):
        i=self.image_ids.index(self.current_image_id)
        i=(i-1)%len(self.image_ids)
        self.current_image_id=self.image_ids[i] 
        print 'current image: ',self.current_image_id
        return self.draw() 
    def up(self):
        i=self.oracles.index(self.current_oracle)
        i=(i+1)%len(self.oracles)
        self.current_oracle=self.oracles[i] 
        print 'current oracle: ',self.current_oracle
        return self.draw() 
    def down(self):
        i=self.oracles.index(self.current_oracle)
        i=(i-1)%len(self.oracles)
        self.current_oracle=self.oracles[i]
        print 'current oracle: ',self.current_oracle
        return self.draw()
    def new_oracle(self):
        new_o=max(self.oracles)+1
        self.oracles.append(new_o)
        self.oracle2color[new_o]=COLORS[new_o%len(COLORS)]
        print 'new oracle :',new_o
        print 'current oracle: ',self.current_oracle
        return self.draw()
    def del_oracle(self):
        for X in list(self.view2oracle):
            if self.view2oracle[X]==self.current_oracle:
                del self.view2oracle[X]
        self.oracles.remove(self.current_oracle)
        del self.oracle2color[self.current_oracle]
        self.current_oracle=self.oracles[0]
        return self.draw()
    def quit(self):
        self.keep_gui_going=False
    def toggle_weak_shadows(self):
        self.draw_weak_shadows=not self.draw_weak_shadows
        return self.draw()
    def toggle_shadows(self):
        self.draw_shadows=not self.draw_shadows
        return self.draw()
    def draw(self):
        if False:
            print "image: ",self.current_image_id
            for v in self.cc.views[self.current_image_id]:
                v_id=(v.id_image,v.id_keypoint)
                if v_id in self.view2oracle:
                    print v_id,(v.u,v.v),'->', self.view2oracle[v_id]
                else:
                    print v_id,(v.u,v.v) 
        img=np.copy(self.IMGS[self.current_image_id])
        #draw all keypoints with color ORACLE2COLOR[VIEW2ORACLE[VIEW]]
        for v in self.cc.views[self.current_image_id]:
            v_id=(v.id_image,v.id_keypoint)
            if v_id in self.view2oracle:
                o_id=self.view2oracle[v_id]
                color=self.oracle2color[o_id]
            else :
                o_id=None
                color=(0, 0, 0  ) #black
            vis.drawView(img,v,color=color,img_scale=self.scale)
        #write "image N, oracle O" with color ORACLE2COLOR[O]
        if self.draw_label:
            #print "drawing text"
            text="I:{} O:{}".format(self.current_image_id,self.current_oracle)
            labelColor=self.oracle2color[self.current_oracle]
            bottom_left=(0,len(img))
            cv2.putText(img, text, 
                bottom_left,
                cv2.FONT_HERSHEY_DUPLEX, 
                5, 
                labelColor,
                thickness=4,
                bottomLeftOrigin=False) 
        #draw epilines from the same oracle
        if self.draw_epilines:
            epipolarGeometries=vis.filterEpG(self.gEpG, self.image_ids)
            #print "drawing epilines ",len(epipolarGeometries),"/",len(gEpG),":",self.image_ids
            #for ep in epipolarGeometries:
            #    print "EP:",ep
            for im_id in self.image_ids:
                if (im_id is not self.current_image_id 
                and (im_id,self.current_image_id) in epipolarGeometries):
                    F=epipolarGeometries[(im_id,self.current_image_id)]
                    for v in self.cc.views[im_id]:
                        v_id=(v.id_image,v.id_keypoint)
                        if v_id in self.view2oracle:
                            #print "epipolar line from ",v_id," with oracle ",o_id
                            o_id=self.view2oracle[v_id]
                            color=self.oracle2color[o_id]
                            vis.drawEpiline(img,F,v,color=color,label=True,img_scale=self.scale)
        if self.draw_shadows:
            current_shadows = computeMultiTrackShadows(
                self.current_image_id,
                self.gEpG,
                self.get_oracles_with_id(),
                weak=False)
            for o_id in current_shadows:
                draw_shadows(
                    img,
                    current_shadows[o_id],
                    self.scale,
                    color=self.oracle2color[o_id],
                    weak=False)
        if self.draw_weak_shadows:
            current_weak_shadows = computeMultiTrackShadows(
                self.current_image_id,
                self.gEpG,
                self.get_oracles_with_id(),
                weak=True)
            for o_id in current_weak_shadows:
                draw_shadows(
                    img,
                    current_weak_shadows[o_id],
                    self.scale,
                    color=self.oracle2color[o_id],
                    weak=True)
        self.cached=img
        return img
    def draw_active(self,img):
        if (self.active_view 
        and self.active_view.id_image==self.current_image_id):
            self.t+=0.1
            vis.drawView(img,
                self.active_view,
                color=self.oracle2color[self.current_oracle],
                scale=20,
                angle=self.t,
                img_scale=self.scale)
    def play(self):
        right_key=1113939%256
        left_key=1113937%256
        up_key=1113938%256
        down_key=1113940%256
        new_key=1048686%256 #n
        del_key=1048676%256 #d
        toggle_label=1048684%256 #l
        toggle_epilines=1048677%256 #e
        quit_key= 1048689%256 #q
        toggle_shadow_weak=ord('z')
        toggle_shadow_strict=ord('x')
        key=None
        mouse_handler=self.get_mouse_event_handler()
        cv2.namedWindow(self.windowName)
        cv2.setMouseCallback(self.windowName,mouse_handler)
        self.keep_gui_going=True
        self.redraw=False
        base_image=self.draw()
        while self.keep_gui_going:
            #img=self.draw()
            img=np.copy(base_image)
            self.draw_active(img)
            cv2.imshow(self.windowName,img)
            key=cv2.waitKey(20)%256
            if key is not -1%256 :
                print key
            if   key==right_key:
                base_image=self.right()
            elif key==left_key:
                base_image=self.left()
            elif key==up_key:
                base_image=self.up()
            elif key==down_key:
                base_image=self.down()
            elif key==new_key:  
                base_image=self.new_oracle()
            elif key==del_key and len(oracles)>1:
                base_image=self.del_oracle()
            elif key==quit_key:
                self.quit()
            elif key==toggle_label:
                base_image=self.toggle_labels()
            elif key==toggle_epilines:
                base_image=self.toggle_epilines()
            elif key==toggle_shadow_strict:
                base_image=self.toggle_shadows()
            elif key==toggle_shadow_weak: 
                base_image=self.toggle_weak_shadows()
            if self.redraw:
                base_image=self.draw()
                self.redraw=False
    def get_oracles(self):
        list_of_oracle_tracks=[]
        for o_id in self.oracles:
            v_ids=( v_id for v_id in self.view2oracle if self.view2oracle[v_id]==o_id)
            vs=[]
            for v_id in v_ids:
                for v in self.cc.views[v_id[0]]:
                    if v.id_keypoint==v_id[1]:
                        vs.append(v)
            O=point(0,vs)
            list_of_oracle_tracks.append(O)
        return list_of_oracle_tracks
    def get_oracles_with_id(self):
        list_of_oracle_tracks=[]
        for o_id in self.oracles:
            v_ids=( v_id for v_id in self.view2oracle if self.view2oracle[v_id]==o_id)
            vs=[]
            for v_id in v_ids:
                for v in self.cc.views[v_id[0]]:
                    if v.id_keypoint==v_id[1]:
                        vs.append(v)
            O=point(o_id,vs)
            list_of_oracle_tracks.append(O)
        return list_of_oracle_tracks
    def get_mouse_event_handler(self):
        def mouse_event_handler(event,x,y,flags,param):
            v=select_keypoint(x*self.scale,y*self.scale,self.cc,self.current_image_id)
            if not v:
                self.active_view=None
                return
            v_id=(v.id_image,v.id_keypoint)
            if not self.active_view is v:
                print 'active: ', v_id
            self.active_view=v
            if event == cv2.EVENT_LBUTTONDBLCLK :
                print v_id,"-->",self.current_oracle
                self.view2oracle[v_id]=self.current_oracle
                self.redraw=True
            if event == cv2.EVENT_RBUTTONDBLCLK and v_id in self.view2oracle:
                print 'del: ', v_id
                del self.view2oracle[v_id]
                self.redraw=True
            return
        return mouse_event_handler
    

def select_keypoint(x,y,CC,im_id):
    #a simple nearest neighbour procedure
    V=CC.views[im_id]
    dist=lambda xv: ((xv.u-x)**2+(xv.v-y)**2)
    md=100000.
    mv=None
    mv=min(V,key=dist)
    sV=sorted(V,key=dist)
    #askp=input('print select_keypoint?')
    if dist(mv)>10000.:
        return None
    if False:
        print x,y,mv.u,mv.v
        for v in sV:
            print "\t",(v.u,v.v), ':',dist(v)
    return mv

