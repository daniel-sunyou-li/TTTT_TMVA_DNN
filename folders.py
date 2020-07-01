import jobtracker
from argparse import ArgumentParser
import os.path

parser = ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="Display detailed logs.")
parser.add_argument("-c", "--compact", action="store_true", help="Compact the specified folders into spec files only.")
parser.add_argument("-i", "--import-data", default=None, help="Create a spec file by scanning output files using variable list file (or \"all\").")
parser.add_argument("folders", nargs="*", default=[], help="Condor log folders to process.")
args = parser.parse_args()

jobtracker.LOG = args.verbose
if args.folders == []:
    folders = [os.path.join(os.getcwd(), d) for d in os.listdir(os.getcwd()) if d.startswith("condor_log")]
else:
    folders = [f for f in args.folders if os.path.exists(f)]

if args.compact:
    print "Compacting folders..."
    for folder in folders:
        jf = jobtracker.JobFolder(folder)
        jf.compact_folder()
        print("Compacted {}.".format(folder))
    print "Done."
elif args.import_data != None:
    print "Importing data from folders..."
    varlist = []
    if args.import_data.lower() == "all":
        print "Default variable list will be used."
        varlist = [v[0] for v in __import__("varsList").varList["DNN"]]
    else:
        print("Reading variable list from {}.".format(args.import_data))
        with open(args.import_data, "r") as vlf:
            for line in vlf.readlines():
                if line != "":
                    varlist.append(line.rstrip().strip())
    for folder in folders:
        jf = jobtracker.JobFolder(folder)
        if jf.jobs != None:
            print("{} already has a spec file!".format(folder))
            choice = raw_input("Overwrite? (y/N) ")
            if not "y" in choice.lower():
                print "Skipping."
                continue
        print("Importing {}.".format(folder))
        jf.import_folder(varlist)
    print "Done."
else:
    print "Job Status Information"
    print

    # Display statistics for each folder.
    for folder in folders:
        print("FOLDER: {}".format(folder))
        jf = jobtracker.JobFolder(folder)
        if jf.jobs == None:
            print "This folder has not been imported yet. Run script with -i"
            continue
        stats = jf.get_stats()
        if jobtracker.LOG:
            # Show per-variable stats
            print("{:<3} {:<40} {:<6}".format("#", "Variable Name", "Count"))
            for i, var in enumerate(sorted(stats["variable_counts"].keys())):
                print("{:<3} {:<40} {:<6}".format(str(i)+".", var, stats["variable_counts"][var]))
            print
            failed = jf.get_resubmit_list()
            if len(failed) > 0:
                print "Failed Jobs:"
                for job in failed:
                    print " - " + job.name
        # Cumulative stats
        print("Finished condor jobs: {} / {}, {:.2f}%".format(
            stats["finished_jobs"], stats["jobs"], 100. * float(stats["finished_jobs"]) / float(stats["jobs"])
            )
        )
        print("Failed condor jobs: {} / {}, {:.2f}%".format(
            stats["failed_jobs"], stats["jobs"], 100. * float(stats["failed_jobs"]) / float(stats["jobs"])
            )
        )
        print("Submitted {} seeds".format(stats["seeds"]))
        print
