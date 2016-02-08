import pickle
import closure_pb2
from point import point
from view import view
from transclosure import transitiveclosure
from tqdm import tqdm

def pickle_load_tracks(filename):
    with open(filename) as fin:
        T=pickle.load(fin)
    return T

def pickle_save_tracks(T,filename):
    with open(filename,'w') as fo:
        pickle.dump(T,fo)

def load_tracks(filename):
    if (
            ('.' in filename )
        and ('pk' in filename.split('.')[0])
        ):
        return pickle_load_tracks(filename)
    else:
        return protobuf_load_tracks(filename)

def save_tracks(T,filename):
    if (
            ('.' in filename )
        and ('pk' in filename.split('.')[0])
        ):
        return pickle_save_tracks(T,filename)
    else:
        return protobuf_save_tracks(T,filename)

def serialize_partition(part):
    pb_part=closure_pb2.Partition()
    for t in tqdm(part.points.values(),"serializing partition"):
        pb_t=pb_part.tracks.add()
        for v in t.allViews():
            pb_v = pb_t.views.add()
            pb_v.image=v.id_image
            pb_v.keypoint=v.id_keypoint
            pb_v.u=v.u
            pb_v.v=v.v
    return pb_part.SerializeToString()

def pbView(v):
    return view(v.image,v.keypoint,v.u,v.v)

def parse_partition(pb_blob):
    pb_part = closure_pb2.Partition()
    pb_part.ParseFromString(pb_blob)
    partition = transitiveclosure()
    for pb_t in tqdm(pb_part.tracks,"reading partition"):
        V=[pbView(pb_v) for pb_v in pb_t.views]
        t= point(0,V)
        partition._insertPoint(t)
    return partition

def protobuf_save_tracks(T,filename):
    serialize_partition(T)
    with open(filename,'wb') as fout:
        fout.write(serialize_partition(T))

def protobuf_load_tracks(filename):
    with open(filename,'rb') as fin:
        pb_blob=fin.read()
        partition=parse_partition(pb_blob)
    return partition
        
            


