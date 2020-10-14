#!/usr/bin/python

import os, sys, time, math, getpass, datetime, pickle, itertools, getopt
from argparse import ArgumentParser
from ROOT import TH1D, gROOT, TFile, TTree
import numpy as np

import varsList
from analyze import analyze
import utils

gROOT.SetBatch(1)

argparse = ArgumentParser()
argparse.add_argument("-y","--year",default="2017")
argparse.add_argument("-n","--variable",help="Select a variable to plot")
argparse.add_argument("-c","--categorized",action="store_true",help="Iterate through multiple categories of jet tagging")
argparse.add_argument("-l","--lepton",default="E",help="Choose electron (E) or muon (M)")
argparse.add_argument("-p","--pdf",action="store_true",help="Produce pdf hists")
argparse.add_argument("-s","--sys",action="store_true",help="Produce all the systematic hists")
argparse.add_argument("-d","--dataset",help="Dataset containing results from DNN training")
argparse.add_argument("-H","--hotjet",default="0p",help="HOT-tagged jet cut ( default is 0p=0+)")
argparse.add_argument("-t","--tjet",default="0p",help="T-tagged jet cut (default is 0p=0+)")
argparse.add_argument("-W","--Wjet",default="0p",help="W-tagged jet cut (default is 0p=0+)")
argparse.add_argument("-b","--bjet",default="2p",help="b-tagged jet cut (default is 2p=2+)")
argparse.add_argument("-j","--jet",default="4p",help="Jet cut (default is 4p=4+)")
argparse.add_argument("-v","--verbose",action="store_true",help="Verbosity on or off")

args = argparse.parse_args()

# read in arguments
nhottlist = [args.hotjet]
nttaglist = [args.tjet]
nWtaglist = [args.Wjet]
nbtaglist = [args.bjet]
njetslist = [args.jet]

# if running multiple categories, all jet levels are used
if args.categorized:
    nhottlist = ["0","1p"]
    nttaglist = ["0","1p"]
    nWtaglist = ["0","1p"]
    nbtaglist = ["2","3","4p"]
    njetslist = ["4","5","6","7","8","9","10p"]

allSamples = varsList.all2017 if args.year == "2017" else varsList.all2018
inputDir = varsList.step3DirLPC2017 if args.year=="2017" else varsList.step3DirLPC2018
dataset = args.dataset.split("/")[0]

varList = varsList.varList["Step3"]
varIndx = np.argwhere(np.asarray(varList)[:,0] == args.variable)

sig = []
bkg = []
data = []
hdamp = []
ue = []

for key in allSamples.keys():
    if "tttt" in str(key).lower():
        sig.append(key)
    elif "data" in str(key).lower():
        data.append(key)
    elif "hdamp" in str(key).lower():
        hdamp.append(key)
    elif "ue" in str(key).lower():
        ue.append(key)
    else:
        bkg.append(key)

if args.verbose:
    print("{} signal samples found".format(len(sig)))
    print("{} data samples found".format(len(data)))
    print("{} hdamp samples found".format(len(hdamp)))
    print("{} ue samples found".format(len(ue)))
    print("{} background samples found".format(len(bkg)))

categories = [
    "is{}_nHDT{}_nT{}_nW{}_nB{}_nJ{}".format(cat[0],cat[1],cat[2],cat[3],cat[4],cat[5]) for cat in list(itertools.product(
        args.lepton,nhottlist,nttaglist,nWtaglist,nbtaglist,njetslist
    ))
]

def read_tree(file):
    if not os.path.exists(file):
        print("Error: {} does not exist.  Exiting program...".format(file))
        os._exit(1)
    rootFile = TFile(file,"READ")
    rootTree = rootFile.Get("ljmet")
    return rootFile, rootTree

def run_data(categories,label,data,minBin,maxBin,nBin):
    treeData = {}
    fileData = {}
    for i, cat in enumerate(categories):
        dataHists = {}
        for sample in data:
            fileData[sample], treeData[sample] = read_tree( inputDir + allSamples[sample][0] )
            dataHists.update(analyze(
                treeData,sample,"",False,args.pdf,args.variable,
                [args.variable,np.linspace(minBin,maxBin,nBin).tolist(),label],
                cat, args.year, args.verbose
            ))
            if i == len(categories) - 1:
                del treeData[cat]
                del fileData[cat]
        if not os.path.isdir("{}/data_hists/".format(dataset)):
            os.system("mkdir {}/data_hists/".format(dataset))
        if not os.path.isdir("{}/data_hists/{}/".format(dataset,args.variable)):
            os.system("mkdir {}/data_hists/{}/".format(dataset,args.variable))
        pickle.dump(dataHists,open("{}/data_hists/{}/{}_{}.p".format(dataset,args.variable,args.variable,cat),"wb"))

def run_signal(categories,label,sig,minBin,maxBin,nBin):
    treeSig = {}
    fileSig = {}
    for i, cat in enumerate(categories):
        sigHists = {}
        for sample in sig:
            fileSig[sample], treeSig[sample] = read_tree( inputDir + allSamples[sample][0] )
            if args.sys:
                for sys in ["jec","jer"]:
                    for dir in ["Up","Down"]:
                        fileSig[sample+sys+dir], treeSig[sample+sys+dir] = read_tree(
                            inputDir + sys.Upper() + dir.lower() + "/" + allSamples[sample][0]
                        )
            #print("sample: "+sample)
            #print("minBin={},maxBin={},nBin={}".format(minBin,maxBin,nBin))
            #print("label: "+label)
            #print("category: "+cat) 
            sigHists.update(analyze(
                treeSig, sample, "", args.sys, args.pdf, args.variable, 
                (args.variable, np.linspace(minBin,maxBin,nBin).tolist(),label),
                cat, args.year, args.verbose
                ))
            if i == len(categories) - 1:
                del treeSig[sample]
                del fileSig[sample]
                if args.sys:
                    for sys in ["jec","jer"]:
                        for dir in ["Up","Down"]:
                            del treeSig[sample+sys+dir]
                            del fileSig[sample+sys+dir]
        if not os.path.isdir("{}/sig_hists/".format(dataset)):
            os.system("mkdir {}/sig_hists/".format(dataset))
        if not os.path.isdir("{}/sig_hists/{}/".format(dataset,args.variable)):
            os.system("mkdir {}/sig_hists/{}/".format(dataset,args.variable))
        pickle.dump(sigHists,open("{}/sig_hists/{}/{}_{}.p".format(dataset,args.variable,args.variable,cat),"wb"))

def run_background(categories,label,bkg,hdamp,ue,minBin,maxBin,nBin):
    treeBkg = {}
    fileBkg = {}
    for i, cat in enumerate(categories):
        bkgHists = {}
        for sample in bkg:
            fileBkg[sample], treeBkg[sample] = read_tree( inputDir + allSamples[sample][0] )
            if args.sys:
                for sys in ["jec","jer"]:
                    for dir in ["Up","Down"]:
                        fileBkg[sample+sys+dir] = read_tree(
                            inputDir + sys.Upper() + dir.lower() + "/" + allSamples[sample][0]
                        )
            bkgHists.update(analyze(
                treeBkg,sample,"",args.sys, args.pdf, args.variable,
                [args.variable, np.linspace(minBin,maxBin,nBin).tolist(), label],
                cat, args.year, args.verbose
            ))
            if i == len(categories) - 1:
                for sys in ["jec","jer"]:
                    for dir in ["Up","Down"]:
                        del treeBkg[sample+sys+dir]
                        del fileBkg[sample+sys+dir]
        if args.sys:
            for sample in hdamp:
                fileBkg[sample], treeBkg[sample] = read_tree( inputDir + allSamples[sample][0] )
                bkgHists.update(analyze(
                    treeBkg,sample,"",False,args.pdf,args.variable,
                    [args.variable, np.linspace(minBin,maxBin,nBin).tolist(), varList[varIndx,1]],
                    cat, args.year, args.verbose
                ))
                if i == len(categories) - 1:
                    del fileBkg[sample]
                    del treeBkg[sample]
            for sample in ue:
                fileBkg[sample], treeBkg[sample] = read_tree( inputDir + allSamples[sample][0] )
                bkgHists.update(analyze(
                    treeBkg,sample,"",False,args.pdf,args.variable,
                    [args.variable, np.linspace(minBin,maxBin,nBin).tolist(), label],
                    cat, args.year, args.verbose
                ))
                if i == len(categories) - 1:
                    del fileBkg[sample]
                    del treeBkg[sample]
        if not os.path.isdir("{}/bkg_hists/".format(dataset)):    
            os.system("mkdir {}/bkg_hists/".format(dataset))
        if not os.path.isdir("{}/bkg_hists/{}".format(dataset,args.variable)):
            os.system("mkdir {}/bkg_hists/{}/".format(dataset,args.variable))
        pickle.dump(bkgHists,open("{}/bkg_hists/{}/{}_{}.p".format(dataset,args.variable,args.variable,cat),"wb"))

def plot_step3(label,minBin,maxBin,nBin,categories,samples):
    print("Plotting {} as {}".format(args.variable,label))
    print("Using binning: ({},{},{})".format(minBin,maxBin,nBin))
    startTime = time.time()
    if samples.lower() == "sig":
        print("Plotting signal samples...")
        run_signal(categories,label,sig,minBin,maxBin,nBin)
        print("Finished plotting signal samples stored in {}/sig_hists/ in {:.2f} minutes.".format(
            dataset, ( time.time()-startTime ) / 60.
        ))
    elif samples.lower() == "bkg":
        print("Plotting background samples...")
        run_background(categories,label,bkg,hdamp,ue,minBin,maxBin,nBin)
        print("Finished plotting background samples stored in {}/bkg_hists/ in {:.2f} minutes.".format(
            dataset, ( time.time()-startTime ) / 60.
        ))
    elif samples.lower() == "data":
        print("Plotting data samples...")
        run_data(categories,label,data,minBin,maxBin,nBin)
        print("Finished plotting data samples stored in {}/data_hists/ in {:.2f} minutes.".format(
            dataset, ( time.time()-startTime ) / 60.
        ))

varTuple = varList[varIndx[0][0]]
plot_step3(varTuple[1],varTuple[2],varTuple[3],varTuple[4],categories,"bkg")
plot_step3(varTuple[1],varTuple[2],varTuple[3],varTuple[4],categories,"sig")
plot_step3(varTuple[1],varTuple[2],varTuple[3],varTuple[4],categories,"data")
