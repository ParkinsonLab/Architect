import os, sys
import subprocess, signal
import datetime

from myutils import *
from time import sleep

ENZDP_ROOT = os.path.abspath(sys.path[0])
ENZPRO_WD = os.path.join(ENZDP_ROOT, "source", "run")

class EnzDP(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.EnzProPerlScript = os.path.join(ENZPRO_WD, "EnzPro.pl")

    def __enter__(self):
        return self
    def __exit__(self, *kwargs):
        logging.info("exiting\n")
        pass

    def run(self, RES_directory=None):
        logging.info("Started.")
        subPID = ""
        try:
            # NN added the following line on Dec 11th 2018.
            if RES_directory is None:
                cwd = os.getcwd()
                RES_directory = cwd
            os.chdir(ENZPRO_WD) 
            # NN added the 4th argument on Dec 11th 2018.			
            command = ["perl" , self.EnzProPerlScript, self.cfg['FASTA_FILE'], str(self.cfg['THRESHOLD']), self.cfg['OUTPUT_FILE'], RES_directory] 
            popen = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setsid)
            subPID = popen.pid
            logging.info("Called perl with pid: [%s]" % subPID)
            logging.info("Command: %s" % command)
            lines_out = iter(popen.stdout.readline, '')
            for line in lines_out:
                if line.strip():
                    logging.info(line.rstrip())
        except:
            logging.critical("Running failed:\n"+traceback.format_exc())
            killProcess(subPID, "Killed process: ")
        finally:
            sleep(1)
            killProcess(subPID, "Finally killed process: ")
        logging.info("Stoped.")

if __name__ == "__main__":
    if len(sys.argv)<2:
        print "Usage: python %s full_path_proj_file" % sys.argv[0]
        print "Example: python %s %s/sample_proj.py" % (sys.argv[0], ENZDP_ROOT)
        exit(1)

    PROJ_FILE = sys.argv[1]
    if len(sys.argv) == 3:
        RES_directory = sys.argv[2]
    else:
        RES_directory = None
    initLog(PROJ_FILE+".log")
    #initLog(ENZDP_ROOT+"%s.log"%(datetime.datetime.now().strftime("%Y%m%d")))
    #initLog("/home/entri/aaa.log")
    if not os.path.isfile(PROJ_FILE):
        logging.critical("project file is not a file [%s]"%PROJ_FILE)
        sys.stderr.write("ERROR: project file is not a file [%s]\n"%PROJ_FILE)
        exit(1)
    else:
        logging.info("found project file")

    cfg = getConfig(PROJ_FILE)

    with EnzDP(cfg) as enzdpRunner:
        enzdpRunner.run(RES_directory)

