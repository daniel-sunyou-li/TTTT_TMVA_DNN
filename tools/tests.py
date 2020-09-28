import jobtracker
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("test", default="subseed_count", help="The test to run.")
parser.add_argument("parameters", nargs="*", default=[], help="Arguments to the test.")
args = parser.parse_args()

jobtracker.LOG = True

#TESTS
def subseed_count(path):
    print("Counting subseeds per seed and variable in file: {}".format(path))
    jf = jobtracker.JobFolder(path)
    stats = jf.get_stats()
    print("Seeds: {}".format(stats["seeds"]))
    ss_dict = {}
    for job in jf.jobs:
        if job.subseed != None:
            s = int(job.seed.binary, base=2)
            if not s in ss_dict:
                ss_dict[s] = set()
            ss_dict[s].add(int(job.subseed.binary, base=2))
            
    for seed_j in jf.seed_jobs:
        s = int(seed_j.seed.binary, base=2)
        print("  {}: {} subseeds".format(s, len(ss_dict[s])))
    print("Seed Variables: {}".format(len(jf.variables)))
    ss_vars = {}
    for job in jf.jobs:
        if job.subseed != None:
            for var in job.subseed.variables:
                if not var in ss_vars:
                    ss_vars[var] = 1
                else:
                    ss_vars[var] += 1
    print("Subseed Variables: {}".format(len(ss_vars.keys())))
    for var in set(jf.variables).union(set(ss_vars.keys())):
        print("  {}: {} seeds, {} subseeds".format(var, stats["variable_counts"][var], ss_vars[var]))
    print
    

if args.test == "subseed_count":
    for f in args.parameters:
        subseed_count(f)
