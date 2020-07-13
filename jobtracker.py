from os import listdir, getcwd
from datetime import datetime
from random import randint
from shutil import rmtree
import os.path
import pickle

LOG = True
def log(s):
    if LOG:
        print s

class Seed(object):
    def __init__(self, variables):
        self.variables = variables
        self.states = {}

        for var in self.variables:
            self.states[var] = False

    def include(self, var):
        # Include a variable in this seed
        if var in self.states:
            self.states[var] = True

    def exclude(self, var):
        # Exclude a variable from this seed
        if var in self.states:
            self.states[var] = False

    def includes(self, var):
        # Check if a variable is included in this seed
        return var in self.states and self.states[var]

    def __len__(self):
        return len(self.variables)

    @property
    def binary(self):
        # Get a binary representation of the seed
        return "".join([("1" if self.states[var] else "0") for var in self.variables])

    @staticmethod
    def from_binary(bitstring, variables):
        # Generate a seed given a bitstring and variables
        seed = Seed(variables)
        for i, c in enumerate(bitstring):
            if c == "1":
                seed.include(variables[i])
            else:
                seed.exclude(variables[i])
        
        if seed.binary != bitstring:
            print "Provided : " + bitstring
            print "Generated: " + seed.binary
            for i, c in enumerate(seed.binary):
                if c != bitstring[i]:
                    print "    " + variables[i]
            raise ValueError("Mismatching bitstrings!")
        return seed

    @staticmethod
    def random(variables):
        # Generate a random seed given variables
        rss = "{:0{}b}".format(randint(0, int("1" * len(variables), 2)), len(variables))
        return Seed.from_binary(rss, variables)


class Job(object):
    def __init__(self, folder, name, seed, subseed):
        self.folder = folder
        self.name = name
        self.seed = seed
        self.subseed = subseed

        self.finished = False

        self.roc_integral = -1

    @property
    def path(self):
        # The full path to the job file
        if self.folder != None:
            return os.path.join(self.folder, self.name + ".job")
        else:
            return None

    @property
    def has_logfile(self):
        return self.folder == None or os.path.exists(os.path.join(self.folder, self.name + ".log"))

    @property
    def has_result(self):
        return self.finished and self.roc_integral != -1

    def check_finished(self):
        if self.has_result:
            return True
        
        if self.folder != None and os.path.exists(self.path):
            log_path = os.path.join(self.folder, self.name + ".log")
            out_path = os.path.join(self.folder, self.name + ".out")
            
            if os.path.exists(log_path):
                # Read the .log file and determine current state of job
                with open(log_path, "r") as f:
                    for line in f.readlines():
                        if "005 (" in line or "009 (" in line: 
                            self.finished = True
                        elif "006 (" in line or "000 (" in line or "001 (" in line:
                            self.finished = False

                if self.finished:
                    if os.path.exists(out_path):
                        with open(out_path, "r") as f:
                            for line in f.readlines():
                                if "ROC-integral" in line:
                                    # Final calculation appears.
                                    self.roc_integral = float(line[line.find(" ")+1:])
                                    break
                    else:
                        self.roc_integral = -1
            else:
                self.finished = True
                self.roc_integral = -1

        return self.finished

class JobFolder(object):
    def __init__(self, path="condor_log"):
        # Initialize a condor folder object
        if path.endswith("/"):
            path = path.rstrip("/")
        self.path = os.path.join(getcwd(), path) if os.path.exists(os.path.join(getcwd(), path)) else path
        self.jobs = None
        if path.endswith(".jtd"):
            # The folder has been compacted
            self.compacted = True
            self._load()
        else:
            self.compacted = False
            self._load()

    def _load(self):
        # Load the data for this folder from the spec file or from the file list
        log("Loading job spec for " + self.path)
        if self.compacted:
            log("   Is spec file.")
            try:
                self._read_jtd()
            except:
                log("   Spec file corrupted!")
        elif os.path.exists(os.path.join(self.path, "jobs.jtd")):
            log("   Found spec file.")
            try:
                self._read_jtd()
            except:
                log("   Spec file corrupted!")
        else:
            log("   Spec file not found! Use the import_folder function.")

    def _read_jtd(self):
        # Read the jobs spec file
        with open(os.path.join(self.path, "jobs.jtd") if not self.compacted else self.path, "rb") as f:
            self.jobs = pickle.load(f)

    def _save_jtd(self):
        # Save the jobs spec file
        with open(os.path.join(self.path, "jobs.jtd") if not self.compacted else self.path, "wb") as f:
            pickle.dump(self.jobs, f, protocol=pickle.HIGHEST_PROTOCOL)

    def import_folder(self, variables):
        # Reads jobs from the raw files in an existing condor log folder, given variables used.
        if self.compacted:
            log("Cannot import, already compacted!")
            return
        
        # Read jobs from the file list
        self.jobs = []

        # Find all files and all jobs
        flist = listdir(self.path)
        jobfiles = sorted([f.rstrip(".job") for f in flist if f.endswith(".job")], key=len)
        
        log("Found {} jobs, scanning and importing.".format(len(jobfiles)))
        seeds = {}
        for name in jobfiles:
            if not "Subseed" in name:
                seed_n = long(name[name.find("Seed_")+5:])
                seeds[seed_n] = Seed.from_binary("{:0{}b}".format(seed_n, len(variables)), variables)
                self.jobs.append(Job(self.path,
                                     name,
                                     seeds[seed_n],
                                     None))
                
        log("Found {} seed jobs.".format(len(seeds.keys())))
        
        for name in jobfiles:
            if not "Subseed" in name:
                continue
            seed_n = long(name[name.find("Seed_")+5:name.find("_", name.find("Seed_")+5)])
            subseed_n = long(name[name.rfind("_")+1:])
            
            self.jobs.append(Job(self.path,
                                 name,
                                 seeds[seed_n],
                                 Seed.from_binary("{:0{}b}".format(subseed_n, len(variables)), variables)))

        self._save_jtd()
        self.check()
        log("Import finished. Spec file saved.")

    def compact_folder(self, dest="default"):
        # Compact the folder, removing logs and keeping only .jtd
        if self.compacted:
            log("Already compacted!")
            return
        if len([j for j in self.jobs if not j.finished]) > 0:
            log("Unable to compact! Contains unfinished jobs!")
            return
        if dest == "default":
            dest = os.path.join(os.getcwd(), self.path[self.path.rfind("/")+1:] + ".jtd")

        # Perform compaction
        self.compacted = True
        old_path = self.path
        self.path = dest
        for job in self.jobs:
            job.folder = None
        self._save_jtd()
        log("Compacted {} into spec file {}.".format(old_path, self.path))

        # Delete old directory
        rmtree(old_path)
        log("Removed old job folder.")
            
    def check(self, subset=None):
        # Check the status of each job
        if self.compacted:
            return
        log("Checking" + (" subset of {}".format(len(subset)) if subset != None else "") + " job statuses in {}".format(self.path))
        if subset == None:
            subset = self.jobs
        for job in subset:
            job.check_finished()
        if len(subset) > 1:
            self._save_jtd()

    def __len__(self):
        # The number of jobs in this folder
        return len(self.jobs) if self.jobs != None else -1

    @property
    def seed_jobs(self):
        # The seed jobs in this folder
        return [j for j in self.jobs if j.subseed == None]

    def subseed_jobs(self, seed):
        # The subseed jobs for a given seed
        return [j for j in self.jobs if (j.subseed != None and j.seed.binary == seed.binary)]

    @property
    def variables(self):
        # The variables used across all jobs
        variables = set()
        for job in self.jobs:
            for var in job.seed.variables:
                if not var in variables:
                    variables.add(var)
        return list(variables)

    def variable_jobs(self, var):
        # Get the jobs which contained a given variable
        return [j for j in self.jobs if (var in j.seed.states)]

    @property
    def result_jobs(self):
        # The jobs which successfully computed a ROC-Integral
        self.check([j for j in self.jobs if not j.has_result])
        return [j for j in self.jobs if j.has_result]

    @property
    def unstarted_jobs(self):
        # The jobs which do not yet have a .out file
        return [j for j in self.jobs if not j.has_logfile]

    def get_resubmit_list(self):
        # Get the jobs which need to be resubmitted.
        self.check([j for j in self.jobs if (not j.has_result)])
        return [j for j in self.jobs if (j.finished and j.roc_integral == -1)]

    def get_variable_counts(self):
        # Get a dict containing the number of times each variable was tested
        counts = {}
        for var in self.variables:
            counts[var] = len([j for j in self.variable_jobs(var) if (j.subseed == None and j.seed.includes(var))])
        return counts

    def get_stats(self):
        # Return info about the folder
        return {
            "jobs": len(self),
            "finished_jobs": len(self.result_jobs),
            "failed_jobs": len(self.get_resubmit_list()),
            "unstarted_jobs": len(self.unstarted_jobs),
            "seeds": len(self.seed_jobs),
            "variable_counts": self.get_variable_counts()
            }

    @staticmethod
    def create(self, name="default"):
        # Create a new condor log folder
        if name == "default":
            name = "condor_log_" + datetime.now().strftime("%d.%b.%Y")
        if not os.path.exists(os.path.join(os.getcwd(), name)):
            os.mkdir(os.path.join(os.getcwd(), name))
        return JobFolder(name)    
