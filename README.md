EventProducer
=============

This package is used to centrally produced events for FCC-hh, HE-LHC at a center of mass of 100 and 27TeV respectively. Any other future collider can also be supported by this framework. 
In order to use it, please get in contact with clement.helsens@cern.ch as running this package requieres specific rights.


Table of contents
=================
  * [EventProducer](eventproducer)
  * [Table of contents](#table-of-contents)
  * [Clone and initialisation](#clone-and-initilisation)
  * [Generate LHE events from gridpacks](#generate-lhe-events-from-gridpacks)
  * [Generate FCCSW files from the LHE and decay with Pyhtia8](#generate-fccsw-files-from-the-lhe-and-decay-with-pyhtia8)
  * [Generate FCCSW files from Pythia8](#generate-fccsw-files-from-pythia8)

Clone and initialisation
========================

If you do not attempt to contribute to the repository, simply clone it:
```
git clone git@github.com:FCC-hh-framework/EventProducer.git
```

If you aim at contributing to the repository, you need to fork and then clone the forked repository:
```
git clone git@github.com:YOURGITUSERNAME/EventProducer.git
```

Then initialise:
```
source ./init.sh
```
Generate LHE files from gripacks
================================

To send jobs starting from a gridpack that does not exist but that you have produced, do the following:
   - place gridpack on eos 
     - for FCC ```/eos/experiment/fcc/hh/generation/gridpacks/```
     - for HELHC ```/eos/experiment/fcc/helhc/generation/gridpacks/```
   - if the gridpack is from Madgraph, name it ```mg_process```, if from powheg please name it ```pw_process```,
   - add to ```param_FCC.py``` or ```param_HELHC.py``` an entry corresponding to the gridpack name in the ```gridpacklist``` list, depending on the study.

If the gridpack already exists or has been properly added to the ```param```, then simply run:

```
python bin/run.py --FCC/HELHC --LHE --send --lsf -p <process> -n <nevents> -N <njobs> -q <queue>
```

example to send 10 jobs of 10 000 events of di-electron events with Mll> 2TeV using 1nh queue of lsf for HELHC:

```
python bin/run.py --HELHC --LHE --send --lsf -p mg_pp_ee_lo -n 10000 -N 10 -q 1nh
```


Generate FCCSW files from the LHE and decay with Pyhtia8
========================================================

1. if you want to let pythia decay without specifiying anything, you can use the default card, but if you have requested extra partons at matrix element, you might need to specify matching parameters to your pythia card
1. if you want to use a specific decay, make sure that the decay you want is in ```decaylist``` and ```branching_ratios``` of the ```param```
1. then create appropriate pythia8 card, by appending standard card with decay syntax if needed and add it to the proper directory, example:
```
/eos/experiment/fcc/hh/utils/pythiacards/pythia_pp_ttz_5f_znunu.cmd
```

1. Run jobs:

```
python bin/run.py --FCC/HELHC --reco --send --type lhep8 --lsf -p <process> -N <njobs> -q <queue> --version <version>
```

Example produce 10 jobs of FCC Delphes events of ttz decaying the Z to neutrinos. :

```
python bin/run.py --FCC --reco --send --lsf -p mg_pp_ttz_5f --type lhep8 -N 10 -q 8nh --version fcc_v02
``` 

Please note that the decay in pythia is optional, and that there is no need to specify the number of events to run on as it will by default run over all the events present in the LHE file

Generate FCCSW files from Pythia8
=================================

Pythia8 manual: http://home.thep.lu.se/~torbjorn/pythia81html/Welcome.html

1. Define process in pythialist in config/param.py
1. Write Pythia8 process card and put it in: /eos/experiment/fcc/hh/utils/pythiacards/

ex: p8_pp_Zprime_10TeV_ttbar.cmd

1. send jobs

python bin/sendJobs_FCCSW_P8.py -n 10 -e 10000 -p pp_Zprime_10TeV_ttbar -q 8nh -v fcc_v02


[]() Cleaning up
--------------------------

Scripts are used to check that the jobs have been properly processed.
For LHE
```
python common/jobchecker.py LHE
python common/cleanfailed.py LHE
```

For FCCSW events version 02
```
python common/jobchecker.py FCC_fcc_v02
python common/cleanfailed.py FCC_fcc_v02
```

