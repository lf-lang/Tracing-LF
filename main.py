#!/usr/bin/env python3
import os
import argparse
import os
import sys
import time
import visualiser



# Get the start time of the visualisation
start_time = time.time()


# Argparser to get the ctf trace directory and the yaml filepath
argparser = argparse.ArgumentParser()
argparser.add_argument("ctf", metavar="CTF", type=str,
                    help="Path to the CTF trace directory")
argparser.add_argument("yamlfile", type=str,
                    help="Path to the .yaml file")
argparser.add_argument("-i", "--include", type=str,
                    help="Regex to INCLUDE only certain reactors or reactions")
argparser.add_argument("-x", "--exclude", type=str,
                    help="Regex to EXCLUDE certain reactors or reactions")
argparser.add_argument("-p", "--plain", action='store_true',
                    help="Generates a trace view including the standard view")
argparser.add_argument("-l", "--logic", action='store_true',
                    help="Generates a trace view where the time axis contains lines denoting start and end logical times")
argparser.add_argument("-hv", "--holoviews", action='store_true',
                    help="Generates a STANDARD trace view using Holoviews. Designed for large traces, losing some functionality of standard visualisation")
argparser.add_argument("-hw", "--holoviews_worker", action='store_true',
                    help="Generates the WORKER TRACE view using Holoviews. Designed for large traces, losing some functionality of standard visualisation")
args = argparser.parse_args()


if not os.path.isdir(args.ctf):
    raise NotADirectoryError(args.ctf)

ctf_path = None
for root, dirs, files in os.walk(args.ctf):
    for f in files:
        if f == "metadata":
            if ctf_path is None:
                ctf_path = str(root)
            else:
                raise RuntimeError("%s is not a single trace (contains "
                                    "more than one metadata file!" %
                                    args.ctf)
if ctf_path is None:
    raise RuntimeError("%s is not a CTF trace (does not contain a metadata"
                        " file)" % args.ctf)





# Do the visualisation

# Include both logic lines and plain view
if args.plain and args.logic:
    vis = visualiser.visualisers(ctf_path, args.yamlfile, args.include, args.exclude, True, True)
    vis.bokeh_visualisation()

# Include plain view
elif args.plain:
    vis = visualiser.visualisers(ctf_path, args.yamlfile, args.include, args.exclude, True, False)
    vis.bokeh_visualisation()

# Include logic lines view 
elif args.logic:
    vis = visualiser.visualisers(ctf_path, args.yamlfile, args.include, args.exclude, False, True)
    vis.bokeh_visualisation()

# Do visualisation with holoviews
elif args.holoviews:
    vis = visualiser.visualisers(ctf_path, args.yamlfile, args.include, args.exclude, False, False)
    vis.holoviews_visualisation()

# Do visualisation with holoviews, showing the worker view
elif args.holoviews_worker:
    vis = visualiser.visualisers(ctf_path, args.yamlfile, args.include, args.exclude, False, False)
    vis.holoviews_worker_visualisation()

# Normal Visualisation
else:
    vis = visualiser.visualisers(ctf_path, args.yamlfile, args.include, args.exclude, False, False)
    vis.bokeh_visualisation()




print("\n VISUALISER TOTAL TIME: " + str(time.time() - start_time) + "\n")