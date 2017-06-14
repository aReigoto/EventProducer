#python bin/sendJobs_FCCSW_P8.py -n 1 -p pp_Zprime_5TeV_ll -e 10000


import glob, os, sys,subprocess,cPickle
import commands
import time
import random
import json

import EventProducer.config.param as para
import EventProducer.common.dicwriter_FCC as dicr
import EventProducer.common.isreading as isr

eosbase='/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'

outdict=dicr.dicwriter(para.fcc_dic)
readdic=isr.isreading(para.readfcc_dic, para.fcc_dic)

#__________________________________________________________
def getCommandOutput(command):
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return {"stdout":stdout, "stderr":stderr, "returncode":p.returncode}

#__________________________________________________________
def SubmitToBatch(cmd,nbtrials):
    submissionStatus=0
    for i in range(nbtrials):            
        outputCMD = getCommandOutput(cmd)
        stderr=outputCMD["stderr"].split('\n')

        for line in stderr :
            if line=="":
                print "------------GOOD SUB"
                submissionStatus=1
                break
            else:
                print "++++++++++++ERROR submitting, will retry"
                print "error: ",stderr
                print "Trial : "+str(i)+" / "+str(nbtrials)
                time.sleep(10)
                break
            
        if submissionStatus==1:
            jobid=outputCMD["stdout"].split()[1].replace("<","").replace(">","")
            return 1,jobid
        
        if i==nbtrials-1:
            print "failed sumbmitting after: "+str(nbtrials)+" trials, will exit"
            return 0,0


#__________________________________________________________
def eosexist(myfile):
    cmd='%s ls %s'%(eosbase,myfile)
    p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    p.wait()
    if len(p.stderr.readline())==0:
        return True
    else: 
        return False


#__________________________________________________________
if __name__=="__main__":
    Dir = os.getcwd()
    
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option ('-n','--njobs', help='Number of jobs to submit',
                       dest='njobs',
                       default='10000')

    parser.add_option ('-e', '--events',  help='Number of event per job. default is 1000',
                       dest='events',
                       default='1000')

    parser.add_option ('-m', '--mode',  help='Running mode [batch, local]. Default is batch',
                       dest='mode',
                       default='batch')

    parser.add_option ('-p', '--process',  help='process, example pp_Zprime_3TeV_eemumu. This is the name that is entered as a key in the dictionnary, and should match an existing card in eos /eos/fcc/hh/pythiacards/',
                       dest='process',
                       default='')

    parser.add_option ('-q', '--queue',  help='lxbatch queue, default 8nh',
                       dest='queue',
                       default='8nh')

    parser.add_option('-t','--test',
                      action='store_true', dest='test', default=False,
                      help='do not send to batch nor write to the dictonary')

    parser.add_option ('-v', '--version',  help='version of the delphes card to use, options are: fcc_v01, cms',
                       dest='version',
                       default='fcc_v01')

    (options, args) = parser.parse_args()
    njobs      = int(options.njobs)
    events     = int(options.events)
    mode       = options.mode
    process    = options.process
    queue      = options.queue
    test       = options.test
    version    = options.version
    rundir = os.getcwd()
    nbjobsSub=0


    if version not in ['fcc_v01', 'cms']:
        print 'version of the cards should be: fcc_v01, cms'
        sys.exit(3)

    delphescards_mmr = '%s%s/%s'%(para.delphescards_dir,version,para.delphescard_mmr)
    if eosexist(delphescards_mmr)==False:
        print 'delphes card does not exist: ',delphescard_mmr
        sys.exit(3)

    delphescards_mr = '%s%s/%s'%(para.delphescards_dir,version,para.delphescard_mr)
    if eosexist(delphescards_mr)==False:
        print 'delphes card does not exist: ',delphescard_mr
        sys.exit(3)

    delphescards_base = '%s%s/%s'%(para.delphescards_dir,version,para.delphescard_base)
    if eosexist(delphescards_base)==False:
        print 'delphes card does not exist: ',delphescard_base
        sys.exit(3)

    fccconfig = '%s%s'%(para.fccconfig_dir,para.fccconfig)
    if eosexist(fccconfig)==False:
        print 'fcc config file does not exist: ',fccconfig
        sys.exit(3)

    if version not in para.fcc_dic:
        print 'mismatch between version of fcc dic in param ===%s=== and version requested by user ===%s==='%(para.fcc_dic,version)

    readdic.backup('sendJobs_FCCSW_P8')
    readdic.reading()

    print '======================================',process
    pythiacard='%spythia_%s.cmd'%(para.pythiacards_dir,process)
    if eosexist(pythiacard)==False:
        print 'pythia card does not exist: ',pythiacard
        readdic.comparedics()
        readdic.finalize()
        sys.exit(3)

    i=0
    njobstmp=njobs
    ################# continue if job already exist and process if not
    while i<njobstmp:
        if outdict.jobexits(sample=process,jobid=i): 
            print 'job i ',i,'  exists    njobs ',njobs
            i+=1
            njobstmp+=1
            continue
        else:
            print 'job does not exists: ',i


        logdir=Dir+"/BatchOutputs/%s/%s/"%(version,process)
        os.system("mkdir -p %s"%logdir)
        frunname = 'job%i.sh'%(i)
        frun = open(logdir+'/'+frunname, 'w')
        commands.getstatusoutput('chmod 777 %s/%s'%(logdir,frunname))
        frun.write('#!/bin/bash\n')
        frun.write('unset LD_LIBRARY_PATH\n')
        frun.write('unset PYTHONHOME\n')
        frun.write('unset PYTHONPATH\n')
        frun.write('source %s\n'%(para.stack))
        frun.write('mkdir job%i_%s\n'%(i,process))
        frun.write('cd job%i_%s\n'%(i,process))
        frun.write('export EOS_MGM_URL=\"root://eospublic.cern.ch\"\n')
        frun.write('source /afs/cern.ch/project/eos/installation/client/etc/setup.sh\n')
        frun.write('%s mkdir %s%s/%s\n'%(eosbase,para.delphes_dir,version,process))
        frun.write('%s cp %s .\n'%(eosbase,delphescards_base))
        if 'fcc' in version:
            frun.write('%s cp %s .\n'%(eosbase,delphescards_mmr))
            frun.write('%s cp %s .\n'%(eosbase,delphescards_mr))
        frun.write('%s cp %s config.py \n'%(eosbase,fccconfig))
        frun.write('%s cp %s card.cmd\n'%(eosbase,pythiacard))           
        frun.write('%s/run fccrun.py config.py --delphescard=card.tcl --inputfile=card.cmd --outputfile=events%i.root --nevents=%i\n'%(para.fccsw,i,events))
        frun.write('%s cp events%i.root %s%s/%s/events%i.root\n'%(eosbase,i,para.delphes_dir,version,process,i))
        frun.write('cd ..\n')
        frun.write('rm -rf job%i_%s\n'%(i,process))

        if mode=='batch':
            cmdBatch="bsub -M 2000000 -R \"rusage[pool=2000]\" -q %s -cwd%s %s" %(queue, logdir,logdir+'/'+frunname)
            batchid=-1
            if test==False:
                job,batchid=SubmitToBatch(cmdBatch,10)
                nbjobsSub+=job
                outdict.addjob(sample=process,jobid=i,queue=queue,nevents=events,status='submitted',log='%s/LSFJOB_%i'%(logdir,int(batchid)),out='%s%s/%s/events%i.root'%(para.delphes_dir,version,process,i),batchid=batchid,script='%s/%s'%(logdir,frunname),inputlhe='Pythia8',plots='none')
        elif mode=='local':
            os.system('./tmp/%s'%frunname)

        else: 
            print 'unknow running mode: %s'%(mode)
        i+=1

    print 'succesfully sent %i  jobs'%nbjobsSub
    outdict.write()
    readdic.comparedics()
    readdic.finalize()


    
