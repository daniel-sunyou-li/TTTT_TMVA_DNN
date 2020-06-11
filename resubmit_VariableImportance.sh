#!/bin/sh

host="LPC"
year="2017"
condor_folder="condor_log"

while getopts ":h:y:f:" opt; do
    case $opt in
        h)
            host=$OPTARG
            ;;
        y)
            year=$OPTARG
            ;;
        f)
            condor_folder=$OPTARG
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument"
            exit 1
            ;;
    esac
done

#Check valid year
if [ $year != "2017" ] && [ $year != "2018" ]; then
    echo "Invalid year: $year"
    exit 1
fi

#Make hostname lowercase
host=`echo "$host" | tr '[:upper:]' '[:lower:]'`

#Verify before submit
echo "Continue resubmitting from $condor_folder using $year data on $host servers?"
read -p "Yes/No: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Usage: -h (server) -y (year) -s (n. seeds) -c (corr. cut)" 
    exit 1
fi

echo "Submitting."

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

if [ $host == 'brux' ]; then
  python ./BRUX/VariableImportanceBRUX_resubmit.py $year $condor_folder # running on BRUX clusters
elif [ $host == 'lpc' ]; then
  python ./LPC/VariableImportanceLPC_resubmit.py $year $condor_folder  # running on LPC clusters, use this if input variables > 20
else
  echo Invalid or No Option Used. Submit as "./resubmit_VariableImportance.sh -h (BRUX or LPC) -y (year) -f (condor folder)"
fi
