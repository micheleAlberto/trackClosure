#!/usr/bin/env python
#coding: utf8 
from itertools import groupby,chain,ifilter
import numpy as np
import cv2
from view import view
from validation.deprecator import deprecated

class point :
    def __init__(self,point_id,views,header=None):
        self.id=point_id
        images=set([v.id_image for v in views])
        self.views={I:[v for v in views if v.id_image==I] for I in images}
        #mappa id_immagine -> vista
        #if False and len(views)>0:
        #    self.header=header if header else reduce(lambda h1,h2: h1|h2,[v.header() for v in views])
        #else:
        #    self.header=0L
        #self.viewHeader=reduce(lambda h1,h2: h1|h2,[1<<(id_image%64) for id_image in self.views],0L)
    def __str__(self):
        header="point <id:{}\n".format(self.id)
        body='\n'.join(['\t'+str(v) for im_id in self.views for v in self.views[im_id]])
        return header+body+'>\n'
    @staticmethod
    @deprecated
    def have_intersection(p1,p2):
        #if (p1.header & p2.header)!=0: #l' header può escludere un possibile match  
        if True:
            for image_id in p1.views.keys(): #per ogni immagine che vede p1
                if p2.views.has_key(image_id): #se questa è vista anche da p2
                    for i in p1.views[image_id]: #si cerca un intersezione tra i due insiemi di osservazioni per quell' immagine
                        for j in p2.views[image_id]:
                            if i.id_keypoint==j.id_keypoint:
                                return True
        return False
    def getKeypointsIds(self,image_id):
        return [v.id_keypoint for v in self.views[image_id]]
    def allViews(self):
        return [v for im_id in self.views for v in self.views[im_id]]
    def mergeWith(self,otherP,excluding=None): #implementa una riscrittura di otherP come self
        if not excluding:
            #self.header=self.header | otherP.header #merge headers
            #self.viewHeader=self.viewHeader | otherP.viewHeader
            #now merge view sets without duplicates
            for image_id in otherP.views.keys():  #per ogni immagine che vede il punto importato
                if self.views.has_key(image_id):  #caso A) se questa è già contenuta nel punto orginale
                    view_set_for_image_id= set(chain (otherP.views[image_id],self.views[image_id])) 
                    #unione con vincolo di unicità, funziona grazie a view.__eq__
                    self.views[image_id]=list(view_set_for_image_id)
                else :#caso B) se questa non è contenuta nel punto orginale
                    self.views[image_id]=otherP.views[image_id] #il vettore di viste viene importato
            return self
        elif len(excluding)>0:
            #now merge view sets without duplicates
            gen=(image_id for image_id in otherP.views.keys() if image_id not in excluding)
            for image_id in gen:  #per ogni immagine che vede il punto importato
                if self.views.has_key(image_id):  #caso A) se questa è già contenuta nel punto orginale
                    view_set_for_image_id= set(chain (otherP.views[image_id],self.views[image_id])) 
                    #unione con vincolo di unicità, funziona grazie a view.__eq__
                    self.views[image_id]=list(view_set_for_image_id)
                else :#caso B) se questa non è contenuta nel punto orginale
                    self.views[image_id]=otherP.views[image_id] #il vettore di viste viene importato
            #self.header=reduce(lambda h1,h2: h1|h2,[v.header() for v in self.allViews()])
            #self.viewHeader=reduce(lambda h1,h2: h1|h2,[1<<(id_image%64) for id_image in self.allViews()],0L)
            return self
    def add_view(self,v):
        #self.header=self.header | v.header()
        if v.id_image in self.views:
            self.views[v.id_image].append(v)
        else:
            self.views[v.id_image]=[v]
        return
    def not_empty(self):
        return (len(self.views)>1)
    def __contains__(self, item):
        if type(item)==int:
            image_id=item
            return (image_id in self.views)
        elif (type(item)==tuple and len(item)==2) :
            try:
                image_id,kp_id=item
                if (image_id in self.views):
                    for v in self.views[image_id]:
                        if v.id_keypoint == kp_id:
                            return True
                return False
            except:
                assert False,"{} : {} wrong item type for view contains".format(type(item)," ".join(types)) 
        assert False,"{} : wrong item type for view contains".format(type(item))


