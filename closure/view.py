#!/usr/bin/env python
#coding: utf8 
from itertools import groupby,chain,ifilter
import numpy as np
from validation.deprecator import deprecated

class view (object):
    def __init__(self,id_image,id_keypoint,u,v):
        self.id_image=id_image
        self.id_keypoint=id_keypoint
        self.u=u
        self.v=v
    def pt(self):
        return np.array([self.u,self.v])
    def hpt(self):
        return np.array([self.u,self.v,1.])
    def key(self):
        return (self.id_image,self.id_keypoint)
    def __str__(self):
        return "view <im:{},kp:{},u:{},v:{}>".format(self.id_image,self.id_keypoint,self.u,self.v)
    def __hash__(self):
        return (self.id_image<<15)+self.id_keypoint
    def __eq__(self, other):
        if (self.id_image==other.id_image) and (self.id_keypoint==other.id_keypoint):
            return True
        else:
             return False
    @deprecated
    def header(self):
        return 1<<((self.id_image+self.id_keypoint)%64)
    def feature(self,f=None):
        if np.any(f):
            self.f=f
        else :
            return self.f
