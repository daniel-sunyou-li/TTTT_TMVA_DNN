#!/bin/sh

eos_username=${1}
eos_folder=${2}
year=${3}
seed_filepath=${4}

# Enter environment
export SCRAM_ARCH=slc7_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsenv
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

# Copy and Unpack Resources
xrdcp -s root://cmseos.fnal.gov//store/user/$eos_username/CMSSW946.tgz .
tar -xf CMSSW946.tgz
rm CMSSW946.tgz

# Identify and Copy Signal and Background Samples

signal=""
bkgrnd=""
if [ $year = "2017" ]; then
	signal=`python -c 'import sys; sys.path.insert(0, "../TTTT_TMVA_DNN"); import varsList; print(" ".join(varsList.sig2017_0));'`
	bkgrnd=`python -c 'import sys; sys.path.insert(0, "../TTTT_TMVA_DNN"); import varsList; print(" ".join(varsList.bkg2017_0));'`
elif [ $year = "2018" ]; then
	signal=`python -c 'import sys; sys.path.insert(0, "../TTTT_TMVA_DNN"); import varsList; print(" ".join(varsList.sig2018_0));'`
	bkgrnd=`python -c 'import sys; sys.path.insert(0, "../TTTT_TMVA_DNN"); import varsList; print(" ".join(varsList.bkg2018_0));'`
fi

for sig in $signal:
do
	xrdcp -s root://cmseos.fnal.gov//store/user/$eos_username/$eos_folder/${sig://:} .
done
for bkg in $bkgrnd:
do
	xrdcp -s root://cmseos.fnal.gov//store/user/$eos_username/$eos_folder/${bkg://:} .
done

# Change to TTTT folder
cd ..
cd ./TTTT_TMVA_DNN/

python remote.py $year $seed_filepath
