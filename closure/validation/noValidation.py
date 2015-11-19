from mergeReport import validationReport
from compactRepresentation import compactPoint
def validation(Point_P, Point_Q):
    P = compactPoint(Point_P)
    P_list = P.keys()
    Q = compactPoint(Point_Q)
    Q_list = Q.keys()
    vr = validationReport()
    vr.merge=True
    PE=[]
    QE=[]
    vr.setMerge(P,Q,PE,QE)
    return vr

noValidation=validation
