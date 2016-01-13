import cv2

def get_key():
    key = cv2.waitKey(20)
    return key%256

def make_key_handler(functor_dictionary):
    D={ord(k) if type(k)==str else k : functor_dictionary[k] for k in functor_dictionary}
    def key_handler():
        k=get_key()
        if k in D:
            D[k]()
    return key_handler

right_key=65363%256
left_key=65361%256

pag_up_key=65365%256 
pag_down_key=65366%256
e_key=101 
q_key= 113
s_key=115
t_key=116
