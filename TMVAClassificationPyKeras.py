import os,sys 
import time  
import getopt

import varsList
from ROOT import gSystem, gROOT, gApplication
from ROOT import TMVA, TFile, TTree, TCut
from subprocess import call
from os.path import isfile

from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adam

os.system("bash")
os.system("source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh")

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()
weightStrC = "pileupWeight*lepIdSF*EGammaGsfSF*MCWeight_singleLepCalc/abs(MCWeight_singleLepCalc)"
weightStrS = weightStrC
weightStrB = weightStrC

cutStrC = "(NJets_JetSubCalc >= 5 && NJetsCSV_JetSubCalc >= 2) && ((leptonPt_singleLepCalc > 35 && isElectron) || (leptonPt_singleLepCalc > 30 && isMuon))"
cutStrS = cutStrC+" && ( isTraining == 2 )"
cutStrB = cutStrC


DEFAULT_OUTFNAME = "weights/TMVA.root"
DEFAULT_INFNAME  = "180"
DEFAULT_TREESIG  = "TreeS"
DEFAULT_TREEBKG  = "TreeB"
DEFAULT_METHODS  = "Cuts,CutsD,CutsPCA,CutsGA,CutsSA,Likelihood,LikelihoodD,LikelihoodPCA,LikelihoodKDE,LikelihoodMIX,PDERS,PDERSD,PDERSPCA,PDEFoam,PDEFoamBoost,KNN,LD,Fisher,FisherG,BoostedFisher,HMatrix,FDA_GA,FDA_SA,FDA_MC,FDA_MT,FDA_GAMT,FDA_MCMT,MLP,MLPBFGS,MLPBNN,CFMlpANN,TMlpANN,SVM,BDT,BDTD,BDTG,BDTB,BDTF,RuleFit"
DEFAULT_NTREES   = "400"
DEFAULT_MDEPTH   = "2"
DEFAULT_MASS     = "180"
DEFAULT_VARLISTKEY = "BigComb"

def usage():
    print " "
    print "Usage: python %s [options]" % sys.argv[0]
    print "  -m | --methods    : gives methods to be run (default: all methods)"
    print "  -i | --inputfile  : name of input ROOT file (default: '%s')" % DEFAULT_INFNAME
    print "  -o | --outputfile : name of output ROOT file containing results (default: '%s')" % DEFAULT_OUTFNAME
    print "  -n | --nTrees : amount of trees for BDT study (default: '%s')" %DEFAULT_NTREES 
    print "  -d | --maxDepth : maximum depth for BDT study (default: '%s')" %DEFAULT_MDEPTH 
    print "  -k | --mass : mass of the signal (default: '%s')" %DEFAULT_MASS 
    print "  -l | --varListKey : BDT input variable list (default: '%s')" %DEFAULT_VARLISTKEY 
    print "  -t | --inputtrees : input ROOT Trees for signal and background (default: '%s %s')" \
          % (DEFAULT_TREESIG, DEFAULT_TREEBKG)
    print "  -v | --verbose"
    print "  -? | --usage      : print this help message"
    print "  -h | --help       : print this help message"
    print " "


def main():

    try:
        # retrieve command line options
        shortopts  = "m:i:n:d:k:l:t:o:vh?"
        longopts   = ["methods=", "inputfile=", "nTrees=", "maxDepth=", "mass=", "varListKey=", "inputtrees=", "outputfile=", "verbose", "help", "usage"]
        opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts )

    except getopt.GetoptError:
        print "ERROR: unknown options in argument %s" % sys.argv[1:]
        usage()
        sys.exit(1)

    infname     = DEFAULT_INFNAME
    treeNameSig = DEFAULT_TREESIG
    treeNameBkg = DEFAULT_TREEBKG
    outfname    = DEFAULT_OUTFNAME
    methods     = DEFAULT_METHODS
    nTrees      = DEFAULT_NTREES
    mDepth      = DEFAULT_MDEPTH
    mass        = DEFAULT_MASS
    varListKey  = DEFAULT_VARLISTKEY
    verbose     = True
    for o, a in opts:
        if o in ("-?", "-h", "--help", "--usage"):
            usage()
            sys.exit(0)
        elif o in ("-m", "--methods"):
            methods = a
        elif o in ("-d", "--maxDepth"):
        	mDepth = a
        elif o in ("-k", "--mass"):
        	mass = a
        elif o in ("-l", "--varListKey"):
        	varListKey = a
        elif o in ("-i", "--inputfile"):
            infname = a
        elif o in ("-n", "--nTrees"):
            nTrees = a
        elif o in ("-o", "--outputfile"):
            outfname = a
        elif o in ("-t", "--inputtrees"):
            a.strip()
            trees = a.rsplit( ' ' )
            trees.sort()
            trees.reverse()
            if len(trees)-trees.count('') != 2:
                print "ERROR: need to give two trees (each one for signal and background)"
                print trees
                sys.exit(1)
            treeNameSig = trees[0]
            treeNameBkg = trees[1]
        elif o in ("-v", "--verbose"):
            verbose = True

    varList = varsList.varList[varListKey]
    nVars = str(len(varList))+'vars'
    Note=''+methods+'_'+varListKey+'_'+nVars+'_mDepth'+mDepth
    outfname = "dataset/weights/TMVA_"+Note+".root"
    # Print methods
    mlist = methods.replace(' ',',').split(',')
    print "=== TMVAClassification: use method(s)..."
    for m in mlist:
        if m.strip() != '':
            print "=== - <%s>" % m.strip()
			
    # Import ROOT classes

    
    # check ROOT version, give alarm if 5.18 
    if gROOT.GetVersionCode() >= 332288 and gROOT.GetVersionCode() < 332544:
        print "*** You are running ROOT version 5.18, which has problems in PyROOT such that TMVA"
        print "*** does not run properly (function calls with enums in the argument are ignored)."
        print "*** Solution: either use CINT or a C++ compiled version (see TMVA/macros or TMVA/examples),"
        print "*** or use another ROOT version (e.g., ROOT 5.19)."
        sys.exit(1)
    

    # Output file
    outputFile = TFile( outfname, 'RECREATE' )
    factory = TMVA.Factory( "TMVAClassification", outputFile, 
                            "!V:!Silent:Color:DrawProgressBar:Transformations=I;:AnalysisType=Classification" )

    factory.SetVerbose( verbose )
    (TMVA.gConfig().GetIONames()).fWeightFileDir = "weights/"+Note

    dataloader = TMVA.DataLoader('dataset')

    for iVar in varList:
        if iVar[0]=='NJets_singleLepCalc': dataloader.AddVariable(iVar[0],iVar[1],iVar[2],'I')
        else: dataloader.AddVariable(iVar[0],iVar[1],iVar[2],'F')

    inputDir = varsList.inputDir
    iFileSig = TFile.Open(inputDir + infname)
    sigChain = iFileSig.Get("ljmet")
    dataloader.AddSignalTree(sigChain)
    bkg_list = []
    bkg_trees_list = []
    hist_list = []
    weightsList = []
    for i in range(len(varsList.bkg)):
        bkg_list.append(TFile.Open(inputDir+varsList.bkg[i]))
        print inputDir+varsList.bkg[i]
        bkg_trees_list.append(bkg_list[i].Get("ljmet"))
        bkg_trees_list[i].GetEntry(0)

        if bkg_trees_list[i].GetEntries() == 0:
            continue
        dataloader.AddBackgroundTree( bkg_trees_list[i], 1)

    signalWeight = 1 

    dataloader.SetSignalWeightExpression( weightStrS )
    dataloader.SetBackgroundWeightExpression( weightStrB )

    mycutSig = TCut( cutStrS )
    mycutBkg = TCut( cutStrB ) 

    dataloader.PrepareTrainingAndTestTree( mycutSig, mycutBkg, "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V" )

    kerasSetting = 'H:!V:VarTransform=G:FilenameModel=model.h5:NumEpochs=10:BatchSize=1028'

    print("Building model")

    model = Sequential()
    model.add(Dense(100, activation='relu', input_dim=7))
    model.add((Dense(100, activation="relu")))
    model.add((Dense(100, activation="relu")))
    model.add((Dense(100, activation="relu")))
    model.add((Dense(2, activation="sigmoid")))

    # Set loss and optimizer
    model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy',])

    # Store model to file
    model.save('model.h5')
    model.summary()

    if methods=="Keras": factory.BookMethod(dataloader, TMVA.Types.kPyKeras, "PyKeras",kerasSetting)
    
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()    
    
    outputFile.Close()
    # save plots:
    print "DONE"

# if __name__ == "__main__":
main()
os.system('exit')
