import jobtracker as jt
from argparse import ArgumentParser
from multiprocessing import Process, Lock, Value
from subprocess import check_output
from time import sleep
from sys import exit as sys_exit
from correlation import generate_uncorrelated_seeds
from base64 import b64encode
import os
import varsList

# Condor job submission template
CONDOR_TEMPLATE = """universe = vanilla
Executable = %(RUNDIR)s/remote.sh
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
request_memory = 3.5 GB
request_cpus = 2
image_size = 3.5 GB
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(eos_username)s %(eos_folder)s %(year)s %(seed_vars)s
Queue 1"""

parser = ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="Display detailed logs.")
parser.add_argument("-r", "--resubmit", action="store_true", help="Resubmit failed jobs from the specified folders.")
parser.add_argument("-p", "--processes", default="2", help="The number of processes used to [re]submit jobs.")
parser.add_argument("-y", "--year", required=True, help="The dataset year to use data from. Valid: 2017 or 2018.")
parser.add_argument("-n", "--seeds", default="500", help="The number of seeds to submit (only in submit mode).")
parser.add_argument("-c", "--correlation", default="80", help="The correlation cutoff percentage.")
parser.add_argument("-l", "--var-list", default="all", help="The variables to use when generating seeds.")
parser.add_argument("--test", action="store_true", help="Only submit one job to test submission mechanics.")
parser.add_argument("--include-unstarted", action="store_true", help="Include unstarted jobs in the resubmit list.")
parser.add_argument("folders", nargs="*", default=[], help="Condor log folders to [re]submit to.")
args = parser.parse_args()

# Parse command line arguments
# -v
jt.LOG = args.verbose

# [ folders ]
folders = []
if args.folders == []:
    if args.resubmit:
        folders = [os.path.join(os.getcwd(), d) for d in os.listdir(os.getcwd()) if d.startswith("condor_log")]
    else:
        folders = ["default"]
else:
    folders = args.folders

# -r
resubmit = args.resubmit

# -p
processes = int(args.processes)

# -y
year = args.year
if year != "2017" and year != "2018":
    raise ValueError("Invaid year selected: {}. Year must be 2017 or 2018.".format(year))

# -n
num_seeds = int(args.seeds)
if resubmit and num_seeds != 500:
    print "Number of Seeds argument ignored in resubmit mode."

# -c
correlation = int(args.correlation)

# -l
variables = None
if not resubmit:
    variables = []
    if args.var_list.lower() == "all":
        variables = [v[0] for v in varsList.varList["DNN"]]
    else:
        print("Reading variable list from {}.".format(args.var_list))
        with open(args.var_list, "r") as vlf:
            for line in vlf.readlines():
                if line != "":
                    variables.append(line.rstrip().strip())

# --ignore-unstarted
include_unstarted = args.include_unstarted

# Get information from varsList
eos_input_folder = varsList.inputDirEOS2018 if year == "2018" else varsList.inputDirEOS2017

eos_username = varsList.eosUserName

print("{}ubmitting{} jobs to LPC servers using {} data with {}% correlation cutoff. Signing in to EOS as {}.".format(
    "Res" if resubmit else "S",
    "" if resubmit else " " + str(num_seeds) + " seeds of",
    year,
    correlation,
    eos_username))

#Check VOMS
def check_voms():
    # Returns True if the VOMS proxy is already running
    print "Checking VOMS"
    try:
        output = check_output("voms-proxy-info", shell=True)
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
        output = check_output("voms-proxy-init --voms cms", shell=True)
        if "failure" in output:
            print "Incorrect password entered. Try again."
            voms_init()
        print "VOMS initialized"

voms_init()

# Track Progress
info_lock = Lock()
submitted_jobs = Value("i", 0)
submitted_seeds = Value("i", 0)

# Submit a single job to Condor
def submit_job(job):
    # encode the job's seed
    seed_vars = b64encode(",".join([v for v, s in (job.seed if job.subseed == None else job.subseed).states.iteritems() if s]))
    
    # Create a job file
    run_dir = os.getcwd()
    with open(job.path, "w") as f:
        f.write(CONDOR_TEMPLATE%{
            "RUNDIR": run_dir,
            "FILENAME": job.name,
            "seed_vars": seed_vars,
            "eos_folder": eos_input_folder,
            "eos_username": eos_username,
            "year": year
            })
    os.chdir(job.folder)

    output = None
    try:
        output = check_output("condor_submit {}".format(job.path), shell=True)
    except:
        pass

    info_lock.acquire()
    if output != None and output.find("submitted") != -1:
        i = output.find("Submitting job(s).") + 19
        ns_jobs = int(output[i:output.find("job(s)", i)])

        i = output.find("to cluster ") + 11
        cluster = output[i:output.find(".", i)]

        i = output.find("jobs to ") + 8
        sched = output[i:output.find("\n", i)]

        submitted_jobs.value += ns_jobs
        if job.subseed == None:
            submitted_seeds.value += 1
        if resubmit:
            print("{} jobs (+{}) submitted to cluster {} by {}.\r".format(submitted_jobs.value, ns_jobs, cluster, sched)),
        else:
            print("{} jobs (+{}) submitted to cluster {} by {}, {} out of {} seeds submitted.\r".format(submitted_jobs.value, ns_jobs, cluster, sched, submitted_seeds.value, num_seeds)),
    else:
        print "[WARN] Job submission failed. Will retry at end."
        print
        info_lock.release()
        sys_exit(1)
    info_lock.release()
    os.chdir(run_dir)

# Split jobs among processes
def submit_joblist(job_list):
    failed_jobs = []
    procs = []
    j = 0
    while j < len(job_list):
        if len(procs) < processes:
            # Start a new process for this job
            p = Process(target=submit_job, args=(job_list[j],))
            p.start()
            procs.append((p, job_list[j]))
            j += 1
        # Clean up old job
        for p in procs:
            if not p[0].is_alive():
                if p[0].exitcode == 1:
                    failed_jobs.append(p[1])
                procs.remove(p)
                break
        sleep(0.25)
    # Wait for remaining processes to finish
    for p in procs:
        p[0].join()
        if p[0].exitcode == 1:
            failed_jobs.append(p[1])

    print

    if len(failed_jobs) > 0:
        print("{} jobs failed to submit.".format(len(failed_jobs)))
        choice = raw_input ("Retry? (Y/n) ")
        if "n" in choice:
            print "Done."
            return
        print "Retrying failed submissions."
        submit_joblist(failed_jobs)
        

# Run in Resubmit mode
def resubmit_jobs():
    job_list = []
    print "Searching for jobs to resubmit."
    for folder in folders:
        print(" - {}".format(folder))
        jf = jt.JobFolder(folder)
        job_list.extend(jf.get_resubmit_list())
        if include_unstarted:
            unstarted = jf.unstarted_jobs
            if len(unstarted) > 0:
                print("   Found {} unstarted jobs".format(len(unstarted)))
                job_list.extend(unstarted)
    print("Found {} jobs to resubmit.".format(len(job_list)))
    submit_joblist(job_list)

    print "Done."

# Run in Submit mode
def submit_new_jobs():
    jf = jt.JobFolder.create(folders[0])
    print("Submitting new jobs into folder: {}".format(jf.path))
    seeds = generate_uncorrelated_seeds(num_seeds, variables, correlation, year)

    print "Generating jobs."
    if jf.jobs == None:
        jf.jobs = []
    job_list = []
    for seed in seeds:
        seed_num = int(seed.binary, base=2)
        seed_job_name = "Keras_" + str(len(variables)) + "vars_Seed_" + str(seed_num)
        job_list.append(jt.Job(jf.path,
                               seed_job_name,
                               seed,
                               None))

        for i, var in enumerate(seed.variables):
            if seed.states[var]:
                subseed_num = seed_num & ~(1 << i)
                subseed = jt.Seed.from_binary("{:0{}b}".format(subseed_num, len(variables)), variables)
                job_list.append(jt.Job(jf.path,
                                       seed_job_name + "_Subseed_" + str(subseed_num),
                                       seed,
                                       subseed))
            

    # Eliminate all but one job in test mode
    if args.test:
        job_list = [job_list[0]]

    jf.jobs.extend(job_list)
    jf._save_jtd()
    print("{} jobs generated and saved.".format(len(job_list)))

    print "Submitting jobs."
    submit_joblist(job_list)

    print "Done."

# Run
if resubmit:
    resubmit_jobs()
else:
    submit_new_jobs()
