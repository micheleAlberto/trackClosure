#!/usr/bin/env python
# -*- coding: utf-8 -*-

#example tracks
#-> central views
#-> connected components of those central views in dumb_closure
#-> views from the connected components
#-> two view matches that engage the views
from closure.transclosure import transitiveclosure as Partition
from closure.point import point as Track
import pickle
import math
def view_set(X):
    if type(X)==list:
        return [(v.id_image,v.id_keypoint) for t in X for v in t.allViews()]
    else:
        return [(v.id_image,v.id_keypoint) for v in X]
def view_dist(x,y):
    return math.sqrt((x.u-y.u)**2 + (x.v-y.v)**2)

def load_benchmark(filename):
    with open(filename) as fin:
        B=pickle.load(fin)
    return B
def save_benchmark(B,filename):
    with open(filename,'w') as fo:
        pickle.dump(B,fo)

radius=4.

class Benchmark:
    def __init__(self,label):
        self.label=label
        self.oracle=Partition()
        self.CC=Partition()
    def __str__(self):
        ss=["Benchmark :"+self.label +"\n"]
        for cc in self.CC.points.values():
            ss.append("  connected component "+str(cc.id)+"\n")
            for v_id in cc.views.keys():
                for v in cc.views[v_id]:
                    kp_id=v.id_keypoint
                    o_ids=[o.id for o in self.oracle.points.values() if (v_id,kp_id) in o]
                    s= "    {} {} x{} y{} o: {}\n".format(v_id,kp_id,v.u,v.v,", ".join(map(str,o_ids)))
                    ss+=s
        return "".join(ss)
    def addConnectedComponent(self,cc_track):
        """add a connected component to the benchmark"""
        self.CC.add_point(cc_track)
    def addOracle(self,oracleTrack):
        """add an oracle to the benchmark. 
        An oracle is a track that is certainly verified , that is, 
        it has been validated by hand that each keypoint is a representation of the same 3d landmark."""
        if len(oracleTrack.views)<2:
            return 
        L=self.CC.viewGroupQuery(oracleTrack.allViews())
        if not len(L)==1:
            print oracleTrack
            print "involves :",L
            for cc in [self.CC.points[l] for l in L]:
                print cc
        assert(len(L)==1)
        self.oracle.add_point(oracleTrack)
    def fetchMatches2(self,matches):
        image_ids=set([c[0] for c in self.benchmark_views])
        views={im:set([c[1] for c in self.benchmark_views if c[0]==im]) for im in image_ids}
        ans_matches={
            ij:[match_tup 
                for match_tup in matches[ij] 
                if match_tup[0] in views[ij[0]] 
                or match_tup[2] in views[ij[1]]
                ]
            for ij in matches}
        return ans_matches 
    def fetchMatches(self,tab,benchmark_match_label,match_label=None):
        image_ids=set([c[0] for c in self.benchmark_views])
        views={im:set([c[1] for c in self.benchmark_views if c[0]==im]) for im in image_ids}
        for M in tab.allMatches():
            if M.Ii in image_ids or M.Ij in image_ids:
                matches=M.mread(match_label)
                matches=[m for m in matches if m[0] in views[M.Ii] or m[1] in views[M.Ij]]
                M.mwrite(self.label,matches)
    def fetchMatches(self,matches):
        """
        omvg=OpenMVG()
        omvg.set_image_dir(sys.argv[1])
        omvg.set_feature_dir("./featDir")
        !!!matches=omvg.getMatches()
        epg=EpipolarGeometry()
        """
        
        image_ids=set([c[0] for c in self.benchmark_views])
        views={im:set([c[1] for c in self.benchmark_views if c[0]==im]) for im in image_ids}
        filtered_matches={}
        for ij in matches:
            if ((ij[0] in views) and (ij[1] in views):
                filtered_matches[ij]=[]
                for m in matches:
                    if ((m[0] in views[ij[0]]) or (m[2] in views[ij[1]])):
                        filtered_matches[ij].append(m)
        return 
    def testResult(self,testedPartition):
        """
        Test a given partition against the benchmark.
        Will return a couple:
            #1:the completeness score of the partition express the ability of the filter to keep the information it is provided
            #2:the correctness score of the partition express the coherence of the keypoint oservations merged by the filter
        """
        results={}
        for o in self.oracle.points.values():
            t_ids=testedPartition.viewGroupQuery(o.allViews())
            completeness_target=float(len(o.views))
            completeness_vector=[]
            correctness_vector=[]
            for t_id in t_ids:
                t=testedPartition.points[t_id]
                correct_views=0.
                for v_id in t.views:
                    if v_id in o.views:
                        max_distance=max(
                            view_dist(t_v,o_v) 
                            for t_v in t.views[v_id] 
                            for o_v in o.views[v_id] )
                        if max_distance<radius:
                            correct_views+=1.
                completeness_vector.append(correct_views/completeness_target)
                correctness_vector.append( correct_views/len(t.views) )
                print "oracle:",o.id
                print "completeness:",completeness_vector
                print "correctness :",correctness_vector
            completeness_score=max(completeness_vector)
            correctness_score=sum(correctness_vector)/len(correctness_vector)
            #alternativa:
            #correctness_score=sum([correctness_vector[i]*completeness_vector[i] for i in range(len(correctness_vector)) ])
            results[o.id]=(completeness_score,correctness_score)
        return results
    def cc2oracles(self,cc_id):
        cc=self.CC.points[cc_id]
        return self.oracle.viewGroupQuery(cc.allViews())
        
        
    
        
            
            
