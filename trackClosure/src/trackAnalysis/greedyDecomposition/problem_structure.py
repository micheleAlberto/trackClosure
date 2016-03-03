from collections import namedtuple
from itertools import combinations
from tqdm import tqdm
import numpy as np
from ...closure.point import point as Track

Clique = namedtuple('clique',['i','j','k'])
Keypoint = namedtuple('keypoint',['i','im','kp','pt'])
ProblemStructure = namedtuple('AnaliticalProblemStructure',[
    'images',
    'keypoints',
    'epipolars',
    'cliques',
    'distances',
    'cosines',
    'kpsToCliques'])

def filter_problem_structure(ps,cosine_threshold):
    images=ps.images
    keypoints= ps.keypoints
    epipolars= ps.epipolars
    clique_ids=[i for i,_ in enumerate(ps.cliques) if ps.cosines[i]<cosine_threshold]
    cliques=[ps.cliques[i] for i in clique_ids]
    distances=[ps.distances[i] for i in clique_ids]
    cosines=[ps.cosines[i] for i in clique_ids]
    kps2cliques=[[] for kp in kps]
        for ci,c in enumerate(cliques):
            for kp_i in c:
                kps2cliques[kp_i].append(ci)
    ps2=ProblemStructure(
            images,
            keypoints,
            epipolars,
            cliques,
            distances,
            cosines,
            kps2cliques)
    return ps2
    
def clique_error(c,keypoints,gEpG):
    error=0.
    epipolar = lambda src,dst:np.dot(
            gEpG[
                keypoints[src].im,
                keypoints[dst].im], 
            keypoints[src].pt)
    for i,j,k in [
        (c[0],c[1],c[2]),
        (c[2],c[0],c[1]),
        (c[1],c[2],c[0])]:
        prediction_i=np.cross(epipolar(j,i),epipolar(k,i))
        prediction_i=prediction_i[0:2]/prediction_i[2]
        observation_i=keypoints[i].pt[0:2]
        error+=np.linalg.norm(observation_i-prediction_i)
    return error

def clique_error2(c,keypoints,epipolars,gEpG):
    error=0.
    for i,j,k in [
        (c[0],c[1],c[2]),
        (c[2],c[0],c[1]),
        (c[1],c[2],c[0])]:
        prediction_i=np.cross(epipolars[j][i],epipolars[k][i])
        prediction_i=prediction_i[0:2]/prediction_i[2]
        observation_i=keypoints[i].pt[0:2]
        error+=np.linalg.norm(observation_i-prediction_i)
    return error

def triplet_error_and_cosine(c,keypoints,epipolars,gEpG):
    i,j,k=c
    dst_im=keypoints[i].im
    prediction_i=np.cross(epipolars[j][dst_im],epipolars[k][dst_im])
    prediction_i=prediction_i[0:2]/prediction_i[2]
    observation_i=keypoints[i].pt[0:2]
    error=np.linalg.norm(observation_i-prediction_i)
    cosine=sum(epipolars[j][dst_im][0:2]*epipolars[k][dst_im][0:2])
    #print "{}<-{}x{} cos:{} L2:{}".format(i,j,k,cosine,error)
    return error,cosine

def make_epipolar(src_kp,dst_im,gEpG):
    F=gEpG[src_kp.im,dst_im]
    ep=np.dot(F,src_kp.pt)
    normalization_term=np.linalg.norm(ep[0:2])
    return ep/normalization_term

def make_structure(T,gEpG):
    kps=[Keypoint(vi,v.id_image,v.id_keypoint,v.hpt()) for vi,v in enumerate(T.allViews())]
    # O(|T.allViews()|)
    cliques=[
        Clique(I.i,J.i,K.i) 
        for I,J,K in list(combinations(kps,3))
        if (
        ((I.im,J.im) in gEpG) and 
        ((I.im,K.im) in gEpG) and 
        ((K.im,J.im) in gEpG) ) ]
    # O(|combinations(T.allViews(),3)|) = 
    # O( |kps|*(|kps|-1)*(|kps|-2)/6) = 
    # O(|kps|^3)
    factors=[clique_error(c,kps,gEpG) for c in cliques]
    # O(|cliques|)<O(|kps|^3)
    kps2cliques=[[] for kp in kps]
    for ci,c in enumerate(cliques):
        for kp_i in c:
            kps2cliques[kp_i].append(ci)
    # O(|cliques|*3)<O(|kps|^3)
    return kps,cliques,factors,kps2cliques


def make_cliques(T,gEpG):
    def triplets_of_clique(c):
        return [ c, (c[1],c[2],c[0]),(c[2],c[0],c[1])]
    images=T.views.keys()
    kps=[Keypoint(vi,v.id_image,v.id_keypoint,v.hpt()) for vi,v in enumerate(T.allViews())]
    epipolars=[{
            dst_im:make_epipolar(kp,dst_im,gEpG) 
            for dst_im in images
            if (kp.im,dst_im) in gEpG} 
    for kp in kps]
    cliques=[]
    for I,J,K in list(combinations(kps,3)):
        c=Clique(I.i,J.i,K.i)
        epipolar_geometries_are_known=(
            ((I.im,J.im) in gEpG) and 
            ((I.im,K.im) in gEpG) and 
            ((K.im,J.im) in gEpG) )
        if epipolar_geometries_are_known:
            cliques.append(c)
    kps2cliques=[[] for kp in kps]
    for ci,c in enumerate(cliques):
        for kp_i in c:
            kps2cliques[kp_i].append(ci)
    return kps,epipolars,cliques,kps2cliques


def make_structure2(T,gEpG,cosine_threshold=2.85):
    def triplets_of_clique(c):
        return [ c, (c[1],c[2],c[0]),(c[2],c[0],c[1])]
    images=T.views.keys()
    kps=[Keypoint(vi,v.id_image,v.id_keypoint,v.hpt()) for vi,v in enumerate(T.allViews())]
    epipolars=[{
            dst_im:make_epipolar(kp,dst_im,gEpG) 
            for dst_im in images
            if (kp.im,dst_im) in gEpG} 
    for kp in kps]
    # O(|T.allViews()|)
    cliques=[]
    factors=[]
    for I,J,K in list(combinations(kps,3)):
        c=Clique(I.i,J.i,K.i)
        epipolar_geometries_are_known=(
            ((I.im,J.im) in gEpG) and 
            ((I.im,K.im) in gEpG) and 
            ((K.im,J.im) in gEpG) )
        if epipolar_geometries_are_known:
            factor=0.
            sum_of_cosines=0.
            for triplet in triplets_of_clique(c):
                e,cosine=triplet_error_and_cosine(c,keypoints,epipolars,gEpG)
                factor+=e
                sum_of_cosines+=np.abs(cosine)
            if sum_of_cosines<cosine_threshold:
                cliques.append(c)
                factors.append(factor/3.)
    # O(|combinations(T.allViews(),3)|) = 
    # O( |kps|*(|kps|-1)*(|kps|-2)/6) = 
    # O(|kps|^3)
    # O(|cliques|)<O(|kps|^3)
    kps2cliques=[[] for kp in kps]
    for ci,c in enumerate(cliques):
        for kp_i in c:
            kps2cliques[kp_i].append(ci)
    # O(|cliques|*3)<O(|kps|^3)
    return kps,epipolars,cliques,factors,kps2cliques


def analize_structure(T,gEpG):
    def triplets_of_clique(c):
        cc=[ c, 
            Clique(c[1],c[2],c[0]),
            Clique(c[2],c[0],c[1])]
        #print c
        #print cc
        return cc
    images=T.views.keys()
    kps=[Keypoint(vi,v.id_image,v.id_keypoint,v.hpt()) for vi,v in enumerate(T.allViews())]
    epipolars=[{
            dst_im:make_epipolar(kp,dst_im,gEpG) 
            for dst_im in images
            if (kp.im,dst_im) in gEpG} 
    for kp in kps]
    # O(|T.allViews()|)
    cliques=[]
    distances=[]
    cosines=[]
    for I,J,K in list(combinations(kps,3)):
        c=Clique(I.i,J.i,K.i)
        epipolar_geometries_are_known=(
            ((I.im,J.im) in gEpG) and 
            ((I.im,K.im) in gEpG) and 
            ((K.im,J.im) in gEpG) )
        if epipolar_geometries_are_known:
            _dis=[]
            _cos=[]
            #print '--'
            for triplet in triplets_of_clique(c):
                e,cosine=triplet_error_and_cosine(triplet,kps,epipolars,gEpG)
                #print "{}<-{}x{} cos:{} L2:{}".format(c[0],c[1],c[2],cosine,e)
                _dis.append(e)
                _cos.append(np.abs(cosine))
            cliques.append(c)
            distances.append(tuple(_dis))
            cosines.append(tuple(_cos))
    kps2cliques=[[] for kp in kps]
    for ci,c in enumerate(cliques):
        for kp_i in c:
            kps2cliques[kp_i].append(ci)
    # O(|cliques|*3)<O(|kps|^3)
    ps=ProblemStructure(
        images,
        kps,
        epipolars,
        cliques,
        distances,
        cosines,
        kps2cliques)
    return ps

def triplets_of_clique(c):
            cc=[ c, 
                Clique(c[1],c[2],c[0]),
                Clique(c[2],c[0],c[1])]
            return cc

def make_structure_factory(cosine_threshold):
    def make_structure(T,gEpG):
        images=T.views.keys()
        kps=[Keypoint(vi,v.id_image,v.id_keypoint,v.hpt()) for vi,v in enumerate(T.allViews())]
        epipolars=[{
                dst_im:make_epipolar(kp,dst_im,gEpG) 
                for dst_im in images
                if (kp.im,dst_im) in gEpG} 
            for kp in kps]
        #Cliques , Distances, Cosines
        cliques=[]
        distances=[]
        cosines=[]
        for I,J,K in list(combinations(kps,3)):
            c=Clique(I.i,J.i,K.i)
            epipolar_geometries_are_known=(
                ((I.im,J.im) in gEpG) and 
                ((I.im,K.im) in gEpG) and 
                ((K.im,J.im) in gEpG) )
            if epipolar_geometries_are_known:
                _dis=[]
                _cos=[]
                for triplet in triplets_of_clique(c):
                    e,cosine=triplet_error_and_cosine(triplet,kps,epipolars,gEpG)
                    _dis.append(e)
                    _cos.append(np.abs(cosine))
                if max(_cos)<cosine_threshold:
                    cliques.append(c)
                    distances.append(max(_dis))
                    cosines.append(max(_cos))
        # Inverted Index
        kps2cliques=[[] for kp in kps]
        for ci,c in enumerate(cliques):
            for kp_i in c:
                kps2cliques[kp_i].append(ci)
        ps=ProblemStructure(
            images,
            kps,
            epipolars,
            cliques,
            distances,
            cosines,
            kps2cliques)
        return ps
    return make_structure
            

def make_structure_sorted_by_factor(T,gEpG):
    kps=[Keypoint(vi,v.id_image,v.id_keypoint,v.hpt()) for vi,v in enumerate(T.allViews())]
    # O(|T.allViews()|)
    cliques=[
        Clique(I.i,J.i,K.i) 
        for I,J,K in tqdm(list(combinations(kps,3)),'cliques')
        if (
        ((I.im,J.im) in gEpG) and 
        ((I.im,K.im) in gEpG) and 
        ((K.im,J.im) in gEpG) ) ]
    # O(|combinations(T.allViews(),3)|) = 
    # O( |kps|*(|kps|-1)*(|kps|-2)/6) = 
    # O(|kps|^3)
    factors=[clique_error(c,kps,gEpG) for c in tqdm(cliques,'factors')]
    sorting_domain=range(len(factors))
    sorting_key=lambda c_id:factors[c_id]
    sorting_map=sorted(sorting_domain,key=sorting_key)
    sorted_cliques=[cliques[c_id] for c_id in sorting_map]
    sorted_factors=[factors[c_id] for c_id in sorting_map]
    kps2cliques=[[] for kp in kps]
    for ci,c in enumerate(sorted_cliques):
        for kp_i in c:
            kps2cliques[kp_i].append(ci)
    # O(|cliques|*3)<O(|kps|^3)
    return kps,sorted_cliques,sorted_factors,kps2cliques


def build_tracks(T,tracks,kps):
    """
    arguments:
    dict(int->int[]) tracks : maps track id to list of keypoint ids
    Keypoint[] kps : list of keypoints
    """
    L=[]
    for t in tracks.values():
        set_of_t=set(t)
        V=[v for vi,v in enumerate(T.allViews()) if vi in set_of_t]
        L.append(Track(0,V))
    return L


