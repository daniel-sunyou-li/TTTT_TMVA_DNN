#!/bin/sh

str_xbitset=${1}
eosDir=${2}
eosUserName=${3}
year=${4}

source /cvmfs/cms.cern.ch/cmsset_default.sh

xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/CMSSW946.tgz .
tar -xf CMSSW946.tgz
rm CMSSW946.tgz

cd ./CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN

SIG=""
BKG=""
if [ $year = "2017" ]; then
    SIG=`python -c 'import sys; sys.path.insert(0, "../TTTT_TMVA_DNN"); import varsList; print(" ".join(varsList.sig2017_0));'`
    BKG=`python -c 'import sys; sys.path.insert(0, "../TTTT_TMVA_DNN"); import varsList; print(" ".join(varsList.bkg2017_0));'`
elif [ $year = "2018" ]; then
     SIG=`python -c 'import sys; sys.path.insert(0, "../TTTT_TMVA_DNN"); import varsList; print(" ".join(varsList.sig2018_0));'`
     BKG=`python -c 'import sys; sys.path.insert(0, "../TTTT_TMVA_DNN"); import varsList; print(" ".join(varsList.bkg2018_0));'`
fi

for sig in $SIG:
do
  xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/${sig//:} .
done
for bkg in $BKG:
do
  xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/${bkg//:} .
done

cd ..

export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

cd ./TTTT_TMVA_DNN/

python TMVAClassification_VariableImportance.py -s $str_xbitset -w lpc -y $year
