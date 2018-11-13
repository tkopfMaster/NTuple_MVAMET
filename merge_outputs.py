import ROOT as r
import os
from glob import glob
from XRootD import client
from XRootD.client.flags import DirListFlags, OpenFlags, MkDirFlags, QueryCode
from multiprocessing import Pool
import argparse

parser = argparse.ArgumentParser(description='Small script to merge artus outputs from local or xrootd resources using multiprocessing.')
parser.add_argument('--mode', default='local',help='mode, that defines how to access the files. Supported: local, xrootd. Default: local')
parser.add_argument('--server',default='root://cmsxrootd-kit.gridka.de:1094/',help='xrootd server to access your files. Only used in xrootd mode. Default: root://cmsxrootd-kit.gridka.de:1094/')
parser.add_argument('--main_directory',default='/storage/gridka-nrg/',help='directory path on the machine or server to the "user" directory. Default: /storage/gridka-nrg/')
### Listing local and xrootd paths known ###
# local accsess to NRG: /storage/gridka-nrg/
# pnfs path to NRG: /pnfs/gridka.de/cms/disk-only/store/user/
### ------------------------------------ ###
parser.add_argument('--sample_directory', help='directory path to the artus outputs directory from the username on, e.g. "/aakhmets/artusjobs_Data_and_MC_2017_test_12_10_2017/". This option is required to be specified.',required=True)
parser.add_argument('--work_directory', help='directory path to place, where the merged output should be stored. This path should exist. The last directory name of the sample directory, e.g. "artusjobs_Data_and_MC_2017_test_12_10_2017" is appended to the work directory. This option is required to be specified.',required=True)
parser.add_argument("--parallel", type=int, default=1, help='Number of cores used for multiprocessing. Default: 1')
parser.add_argument("--replace", nargs='+', default=None, help='Nicks specified for replacement. Default: None')

args = parser.parse_args()

mode = args.mode
server = args.server
main_directory = args.main_directory.strip("/")
sample_directory = args.sample_directory.strip("/")
work_directory = args.work_directory.strip("/")
parallel = args.parallel
suffix = "_v2"

aim_path =  os.path.join("/",work_directory,os.path.basename(sample_directory))
input_directory = os.path.join("/",main_directory,sample_directory)

hadd_cmds = []


def execute(cmd):
    os.system(cmd)

if not args.replace:
    print "CREATING",aim_path,"if not already existent"
    os.system("mkdir -p "+aim_path)
    print "REMOVING old files in",aim_path
    os.system("rm -rf "+os.path.join(aim_path,"*"))

if mode == "local":
    subdirectories = [ d for d in os.listdir(input_directory) if os.path.isdir(os.path.join(input_directory,d))]

    for sd in subdirectories:
        if args.replace:
            contained = False
            for nick in args.replace:
                if nick in sd:
                    contained = True
            if not contained:
                continue
        input_files = glob(os.path.join(input_directory,sd,"*.root"))
        dataset_aim_path = os.path.join(aim_path,sd)
        merged_file_path = os.path.join(dataset_aim_path,sd+".root")
        if args.replace:
            os.system("rm -rf %s"%dataset_aim_path)
        print sd," has files:",len(input_files)
        hadd_cmd = "mkdir " + dataset_aim_path +  ";\nhadd " + merged_file_path + " " + " ".join(input_files)
        with open("%s.sh"%sd,"w") as f:
            f.write(hadd_cmd)
        hadd_cmds.append("source ./%s.sh"%sd)

elif mode == "xrootd":
    myclient = client.FileSystem(server)

    status, listing = myclient.dirlist(input_directory, DirListFlags.STAT)
    dataset_dirs = [ entry.name for entry in listing if ".gz" not in entry.name]
    
    for sd in dataset_dirs:
        if args.replace:
            contained = False
            for nick in args.replace:
                if nick in sd:
                    contained = True
            if not contained:
                continue
        dataset_dir = os.path.join(input_directory,sd)
        s, dataset_listing = myclient.dirlist(dataset_dir, DirListFlags.STAT)
        input_files = [os.path.join(server,dataset_dir.lstrip("/"),entry.name) for entry in dataset_listing if ".root" in entry.name]
        print sd," has files:",len(input_files)
        dataset_aim_path = os.path.join(aim_path,sd)
        merged_file_path = os.path.join(dataset_aim_path,sd+".root")
        if args.replace:
            os.system("rm -rf %s"%dataset_aim_path)
        hadd_cmd = "mkdir " + dataset_aim_path +  ";\nhadd " + merged_file_path + " " + " ".join(input_files)
        with open("%s.sh"%sd,"w") as f:
            f.write(hadd_cmd)
        hadd_cmds.append("source ./%s.sh"%sd)

else:
    print "Undefined file access mode. Please choose 'local' or 'xrootd'. Exiting script."
    exit(1)

p = Pool(parallel)
p.map(execute, hadd_cmds)
os.system('rm *MINIAOD*.sh; rm *USER*.sh')
