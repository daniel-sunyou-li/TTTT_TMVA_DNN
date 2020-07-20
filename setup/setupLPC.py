#!/usr/bin/env python

# this will take a while since it has to copy files from BRUX to FNAL and then split the files and finally copy them to EOS

import os, sys, getpass, pexpect, argparse
from subprocess import check_output
from subprocess import call as sys_call
sys.path.insert(0, "../TTTT_TMVA_DNN")
import varsList

# set-up the working area
lpcHomeDir = os.path.expanduser("~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/")
brux_pwd = None

# Run CERN

#Check VOMS
def check_voms():
    # Returns True if the VOMS proxy is already running
    print "Checking VOMS"
    try:
        output = check_output("voms-proxy-info", shell=True)
        print output.rfind("timeleft")
        print output[output.rfind(": ")+2:]
        if output.rfind("timeleft") > -1:
            if int(output[output.rfind(": ")+2:].replace(":", "")) > 0:
                print "[OK ] VOMS found"
                return True
        return False
    except:
        return False
    
def voms_init():
    #Initialize the VOMS proxy if it is not already running
    if not check_voms():
        print "Initializing VOMS"
        output = check_output("voms-proxy-init --rfc --voms cms", shell=True)
        if "failure" in output:
            print "Incorrect password entered. Try again."
            voms_init()
        print "VOMS initialized"
        
def compile_splitter():
    # compile the sample splitting c++ script
    if "splitROOT.out" in os.listdir(os.getcwd() + "/Tools/"):
        sys_call("rm {}/Tools/splitROOT.out".format(os.getcwd()), shell=True)
    print "[   ] Compiling splitROOT.cpp..."
    if sys_call("g++ `root-config --cflags` `root-config --libs` -o ./Tools/splitROOT.out ./Tools/splitROOT.cpp", shell=True) == 0:
        print "[OK ] Compiled splitROOT.CPP"
    else:
        print "[ERR] Compiling splitROOT.cpp failed!"
        sys.exit(1)
    
# transfer files from BRUX to LPC
# will need to input BRUX password

def brux_auth():
    global brux_pwd
    #Get BRUX password
    print "Password for " + varsList.bruxUserName + "@brux.hep.brown.edu"
    if brux_pwd == None:
        brux_pwd = getpass.getpass("Password: ")

def download_samples(years = ["2017", "2018"]):
    #Transfer the samples from the BRUX server
    #Returns True if all were downloaded successfully
    brux_auth()
    print "[   ] Transferring samples from BRUX for years: " + str(years)
    
    # setup parameters that will differ between 2017 and 2018 samples
    step2Sample  = None
    inputDirBRUX = None
    inpu9tDirLPC = None
    inputDirEOS  = None
    samples      = None
    samples_0    = None

    for year in years:
        if year == "2017":
            step2Sample  = varsList.step2Sample2017
            inputDirBRUX = varsList.inputDirBRUX2017
            inputDirLPC  = varsList.inputDirLPC2017
            inputDirEOS  = varsList.inputDirEOS2017
            samples      = varsList.sig2017 + varsList.bkg2017
            samples_0    = varsList.sig2017_0 + varsList.bkg2017_0
        elif year == "2018":
            step2Sample  = varsList.step2Sample2018
            inputDirBRUX = varsList.inputDirBRUX2018
            inputDirLPC  = varsList.inputDirLPC2018
            inputDirEOS  = varsList.inputDirEOS2018
            samples      = varsList.sig2018 + varsList.bkg2018
            samples_0    = varsList.sig2018_0 + varsList.bkg2018_0
        
        # output sample origin and destination when running setup
        if step2Sample not in os.listdir(lpcHomeDir):
            sys_call("mkdir {}{}".format(lpcHomeDir,step2Sample), shell=True)
        print("[   ] Transferring files from {} to {}...".format(
            varsList.bruxUserName + "@brux.hep.brown.edu:" + inputDirBRUX,
            lpcHomeDir + step2Sample
        ))

        for sample in samples:
            if sample not in os.listdir("{}{}".format(lpcHomeDir,step2Sample)):
                print("[   ] Transferring {}...".format(sample))
                child = pexpect.spawn("scp -r {}@brux.hep.brown.edu:{}{} {}{}".format(
                        varsList.bruxUserName,
                        inputDirBRUX,
                        sample,
            	        lpcHomeDir,
                        step2Sample
                        ))
                opt = 1
                while opt == 1:
                    # Handle both the password prompt and the connection prompt.
                    opt = child.expect([varsList.bruxUserName + "@brux.hep.brown.edu's password: ",
                                        "Are you sure you want to continue connecting (yes/no)? "])
                    if opt == 1:
                        # Confirm connection
                        child.sendline("yes")
                # Send password
                child.sendline(brux_pwd)
                
                child.interact()
                print "[OK ] Done."
            else:
                print("[OK ] {} has been transferred. Proceeding to next sample...".format(sample))
        
        if check_samples(samples, lpcHomeDir + step2Sample) == False:
            return False
    
    print "[OK ] All samples downloaded"
    return True
        
def check_samples(expect, dir):
    #Check if all the expected samples are in the directory
    for sample in expect:
        if sample not in os.listdir(dir):
            print("[ERR] {} was not transferred properly. Please resubmit this script.".format(sample))
            return False
    return True

def split_root(years = ["2017", "2018"]):
    # run the root file splitting script
    for year in years:
        print("[   ] Splitting {} ROOT files...".format(year))
        d = lpcHomeDir + (varsList.step2Sample2017 if year == "2017" else varsList.step2Sample2018)
        for sample in (varsList.sig2017 + varsList.bkg2017 if year == "2017" else varsList.sig2018 + varsList.bkg2018):
            if sys_call("./Tools/splitROOT.out {} {} {} {}".format(
                d,                           # location of sample to split
                d,                           # destination of split sample(s)
                sample,                      # sample to split
                3                            # number of files to split into
                ), shell=True) == 1:
                print "[ERR] Splitting " + sample + " failed!"
    print "[OK ] Finished splitting ROOT files"
    
def eos_transfer(years = ["2017", "2018"]):
    #Transfer data to EOS
    for year in years:
        d = (varsList.step2Sample2017 if year == "2017" else varsList.step2Sample2018)
        #Make EOS dir
        sys_call("eosmkdir root://cmseos.fnal.gov//store/user/{}".format(varsList.eosUserName + "/" + d + "/"), shell=True)
        
        # transfer one of the split samples to EOS
        print "[   ] Transferring to EOS..."
        if sys_call("xrdcp {}*split0.root root://cmseos.fnal.gov//store/user/{}".format(
                     "./" + d + "/",
                     varsList.eosUserName + "/" + d + "/"
                  ), shell=True) == 1:
            print "[ERR] EOS transfer of split ROOT file failed!"
            sys.exit(1)
        print("[OK ] EOS transfer complete")

def create_tar():
    # tar the CMSSW framework
    if "CMSSW946.tgz" in os.listdir(lpcHomeDir):
        print("[   ] Deleting existing CMSSW946.tgz...")
        sys_call("rm {}{}".format(lpcHomeDir, "CMSSW946.tgz"), shell=True)
    print "[   ] Creating TAR file"
    if sys_call("tar -C ~/nobackup/ -zcvf CMSSW946.tgz --exclude=\'{}\' --exclude=\'{}\' --exclude=\'{}\' --exclude=\'{}\' --exclude=\'{}\' --exclude=\'{}\' {}".format(
            "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/" + varsList.step2Sample2017,
            "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/" + varsList.step2Sample2018,
            "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/condor_log*",
            "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/dataset_*",
            "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/CMSSW946.tgz",
            "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/.git/*",
            "CMSSW_9_4_6_patch1/"
        ), shell=True) == 1:
        print "[ERR] Creating TAR file failed!"
        sys.exit(1)
    print("[   ] Transferring CMSSW946.tgz to EOS...")
    if sys_call("xrdcp -f CMSSW946.tgz root://cmseos.fnal.gov//store/user/{}".format(varsList.eosUserName), shell=True) == 1:
        print "[ERR] EOS trandfer of TAR file failed!"
        sys.exit(1)
    print("[OK ] EOS transfer complete")

##def create_result_dirs():    
##    # create TMVA DNN training result directories
##    if "condor_log" not in os.listdir("./"):
##        os.system("mkdir {}condor_log".format(lpcHomeDir))
##    if "dataset" not in os.listdir("./"):
##        os.system("mkdir {}dataset".format(lpcHomeDir))
##        os.system("mkdir {}dataset/weights".format(lpcHomeDir))
# To be replaced by new condor log manager

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--compile", action="store_true", help="Compile the splitRoot binary")
parser.add_argument("-d", "--download-samples", action="store_true", help="Only download the samples for BRUX")
parser.add_argument("-s", "--split-root", action="store_true", help="Split the ROOT files")
parser.add_argument("-e", "--eos-upload", action="store_true", help="Upload split files to EOS")
parser.add_argument("-t", "--tar-upload", action="store_true", help="Create TAR file and upload to EOS")
parser.add_argument("years", nargs="*", default=["2017", "2018"], help="Years to work with, from 2017 or 2018")

if __name__ == "__main__":
    args = parser.parse_args()
    
    for year in args.years:
        if year != "2017" and year != "2018":
            print("[ERR] Invalid year: " + year)
            sys.exit(1)
    
    voms_init()
    partial = False
    if args.compile:
        partial = True
        compile_splitter()
    if args.download_samples:
        partial = True
        download_samples(args.years)
    if args.split_root:
        partial = True
        split_root(args.years)
    if args.eos_upload:
        partial = True
        eos_transfer(args.years)
    if args.tar_upload:
        partial = True
        create_tar()
        
    if not partial:
        print "Running whole setup script..."
        compile_splitter()
        download_samples(args.years)
        split_root(args.years)
        eos_transfer(args.years)
        create_tar()
    
    print "Done."        
