from deprecator import deprecated

import numpy as np
import matplotlib.pyplot as plt
from random import random
from collections import Counter
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import dummy

from syntheticGenerator import Generator
#Machine Learning Models
from sklearn import linear_model
from sklearn import svm
from sklearn import tree
MLtools={
      'lrl2':lambda : linear_model.LogisticRegression(C=1000, penalty='l2', tol=1e-6),
      'lrl1':lambda : linear_model.LogisticRegression(C=1000, penalty='l1', tol=1e-6),
      'svc-rbf':lambda : svm.SVC(),
      'svc-lin':lambda : svm.SVC(kernel='linear'),
      'svc-sig':lambda : svm.SVC(kernel='sigmoid'),
      'tree'   :lambda : tree.DecisionTreeClassifier()}

def trainClassifier(method, X, Y, Xv, Yv):
    tool=MLtools[method]()
    classifier=tool.fit(X, Y)
    sbagliati=Counter([val(Yv[i],classifier.predict(Xv[i])) for i in range(len(Xv))])
    performance={i:sbagliati[i]/float(len(Xv)) for i in sbagliati}
    return performance,classifier

def crossClassifierPerformance(models,X,Y):
    YY=[]
    for x,y in zip(X,Y):
        yy=np.array([y]+[models[m].predict(x) for m in models])
        YY.append(yy)
    return YY

def clfCouple(YY,i,j):
    mixed=0
    joint=0
    Awrong=0
    Bwrong=0
    AorBwrong=0
    for yy in YY:
        o=yy[0]
        a=yy[i]
        b=yy[j]
        if a!=b:
            mixed+=1
        if a!=o:
            Awrong+=1
        if b!=o:
            Bwrong+=1
        if a!=o and b!=o:
            AorBwrong+=1
        if a==o or b==o:
            joint+=1
    if AorBwrong==0:
        AorBwrong=0.1
    return float(mixed)/len(YY)

def quadratic(xx):
    xxn=list(xx)
    xxn=[i*j for i in xxn for j in xxn ]
    return xxn
def val(o,p):
    if p==o:
        return True
    elif o and not p:
        return 'fn'
    else :
        return 'fp'

def trainExcludeClassifiers(trainingSamples=10000,validationSamples=4000,literals='abc',pointLenght=5):
    #training ExcludeClassifier
    nt=trainingSamples
    nv=validationSamples
    gen=Generator()
    gen.genPoints(literals,pointLenght)
    #training data
    XY=gen.genExcludeCases(nt)
    X=np.array([list(xy[0]) for xy in XY])
    Y=np.array([xy[1] for xy in XY])
    nt=len(X)
    print nt,' training examples'
    #validation data
    XYv=gen.genExcludeCases(nv)
    Xv=np.array([list(xy[0]) for xy in XYv])
    Yv=np.array([xy[1] for xy in XYv])
    nv=len(Xv)
    print nv,' validation examples'
    ExcludeStat={}
    ExcludeModels={}
    for method in MLtools: 
        print 'training '+method
        perf,clf=trainClassifier(method,X,Y,Xv,Yv)
        ExcludeModels[method]=clf
        ExcludeStat[method]=perf
        print ExcludeStat[method]
    return (ExcludeStat,ExcludeModels)


def compareExcludeClassifiers(samples=10000,trainingSamples=10000,validationSamples=4000,literals='abc',pointLenght=5):
    e_stat,e_models=trainExcludeClassifiers(
        trainingSamples=trainingSamples,
        validationSamples=validationSamples,
        literals=literals,
        pointLenght=pointLenght)
    gen=Generator()
    gen.genPoints(literals,pointLenght)
    XY=gen.genExcludeCases(samples)
    X=np.array([list(xy[0]) for xy in XY])
    Y=np.array([xy[1] for xy in XY])
    YY=crossClassifierPerformance(e_models,X,Y)
    return [[clfCouple(YY,i,j) for j in range(len(e_models)+1)] for i in range(len(e_models)+1)]
    """
    g = sns.PairGrid(YY)
    g.map_diag(plt.hist)
    g.map_offdiag(plt.heatmap)"""



def trainMergeClassifiers(ExcludeClassifier,trainingSamples=10000,validationSamples=4000,literals='abc',pointLenght=5):
    #training MergeClassifier
    gen=Generator()
    gen.genPoints(literals,pointLenght)
    nt=trainingSamples
    nv=validationSamples
    Xt,yt=gen.genMergeCases(nt,ExcludeClassifier)
    print nt,' training examples'
    gen=Generator()
    gen.genPoints(literals,pointLenght)
    Xv,yv=gen.genMergeCases(nv,ExcludeClassifier)
    print nv,' validation examples'
    MergeStat={}
    MergeModels={}
    for method in MLtools:
        print 'training '+method
        perf,clf=trainClassifier(method,Xt,yt,Xv,yv)
        MergeStat[method]=perf
        MergeModels[method]=clf
        print perf
    return (MergeStat,MergeModels)

    

#scikit learn suggest to use joblib instead of pickle for serialization of models
#http://scikit-learn.org/stable/modules/model_persistence.html
from sklearn.externals import joblib 
import os.path
train_path=os.path.dirname(dummy.__file__)+'/'
MergeClassifier_filename='merge_clf.pkl'
ExcludeClassifier_filename='exclude_clf.pkl'
def getExcludeClassifier():
    clf = joblib.load(train_path+ExcludeClassifier_filename) 
    return clf
def saveExcludeClassifier(clf):
    FN=joblib.dump(clf, train_path+ExcludeClassifier_filename,compress=3)
    print 'saved in : ' , FN
    return
def getMergeClassifier():
    clf = joblib.load(train_path+MergeClassifier_filename) 
    return clf
def saveMergeClassifier(clf):
    FN=joblib.dump(clf, train_path+MergeClassifier_filename,compress=3)
    print 'saved in : ' , FN
    return  

MergeClassifier='TODO'
ExcludeClassifier='TODO'

def TrainAndSave_ExcludeClassifier(argv):
    print 'training exclude classifier'
    stat,models=trainExcludeClassifiers(
        trainingSamples=10000,
        validationSamples=4000,
        literals='abc',
        pointLenght=5)
    bestMethod=max(stat,key=lambda x:stat[x][True])
    bestClf=models[bestMethod]
    bestStat=stat[bestMethod]
    chosenMethod="svc-rbf"
    chosenClf=models[chosenMethod]
    chosenStat=stat[chosenMethod]
    if bestMethod!=chosenClf:
        print 'warning the best method is not the default one'
        print 'best :',bestMethod
        print bestStat
        print 'chosen :',chosenMethod
        print chosenStat
    print 'saving classifier ',chosenMethod
    saveExcludeClassifier(chosenClf)
    return

def TrainAndSave_MergeClassifier(argv):
    print 'training merge classifier'
    ExcludeClassifier=getExcludeClassifier()
    stat,models=trainMergeClassifiers(
        ExcludeClassifier,
        trainingSamples=10000,
        validationSamples=4000,
        literals='abc',
        pointLenght=5)
    bestMethod=max(stat,key=lambda x:stat[x][True])
    bestClf=models[bestMethod]
    bestStat=stat[bestMethod]
    chosenMethod="svc-rbf"
    chosenClf=models[chosenMethod]
    chosenStat=stat[chosenMethod]
    if bestMethod!=chosenClf:
        print 'warning the best method is not the default one'
        print 'best :',bestMethod
        print bestStat
        print 'chosen :',chosenMethod
        print chosenStat
    print 'saving classifier ',chosenMethod
    saveMergeClassifier(chosenClf)
    return

def main(argv):
    l=len(argv)
    if l>1 and 'train' in argv[1]:
        if l==2:
            TrainAndSave_ExcludeClassifier(argv)
            TrainAndSave_MergeClassifier(argv)
            return
        elif l>2 and 'merge' in argv[2]:
            TrainAndSave_MergeClassifier(argv)
            return
        elif l>2 and 'exclude' in argv[2]:
            TrainAndSave_ExcludeClassifier(argv)
            return
    return

if __name__ == "__main__":
    main(sys.argv)


