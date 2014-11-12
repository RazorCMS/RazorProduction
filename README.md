RazorProducion
==============

Command line tools to manage production through crab3

One-time directory setup
--------------
Create and go to a working directory, preferebly accessible from afs:

     mkdir $HOME/scratch0/prod_dir/
     cd $HOME/scratch0/prod_dir/
     git clone https://github.com/RazorCMS/RazorProduction.git
     source RazorProduction/cert.sh
     ln -s RazorProduction/production.py 

Each-session setup

     cd $HOME/scratch0/prod_dir/
     source RazorProduction/cert.sh

Campaign setup
--------------
See at the bottom

Vizualisation of on-going production
--------------
Browse to https://cms-caltech-db.cern.ch/ from within cern network
Restricted acces to "razor-cms" e-group.

Specifying specific tasks
--------------
For any action in list, collect, create, submit, reset (list used for the example below).
For everyone task

     ./production.py --do list --arg @all

For a specific campaign 

     ./production.py --do list --label leopard --version 1 --arg @all

For a given task index

     ./production.py --do list --arg 1

For a given status

     ./production.py --do list --arg %new

For a given keyword

     ./production.py --do list --arg QCD
 
For a given status, user and index/keyword

     ./production.py --do list --arg index%status@user

Listing current tasks
--------------
For your task

     ./production.py --do list

Installing production
--------------
In order to retrive the proper software setup for the production

     ./production.py --do install

Pushing production through
--------------
Each taks need to go through several steps
new -> create -> submit -> collect -> done

Create the tasks : making a crab config

     ./production.py --do create

Submitting the task

     ./production.py --do submit

Collecting status and resubmitting if necessary, or closing the task

     ./production.py --do collect

N.B. ./production.py --do collect --unlimited will do create and submit automatically, meaning that you would just have to install the production (--do install) and set that pusher (collect.sh --unlimited) to push everything that gets assigned to you through to completion.


Installing the pusher in cron
--------------
Link the working directory to $HOME/ntprod

     ln -s $HOME/scratch0/prod_dir/ $HOME/ntprod

Install the collector script in cron to every 4 hours

     echo "30 */4 * * * lxplus.cern.ch $HOME/ntprod/RazorProduction/collect.sh" | acrontab

Or install the unlimeted collector script in cron

     echo "30 */4 * * * lxplus.cern.ch $HOME/ntprod/RazorProduction/collect.sh --unlimited" | acrontab


One-time certificate setup
--------------
In the following file on afs, put your grid password $HOME/private/$USER.txt, and the stricter read access both unix and afs.

Campaign setup
--------------
To create a new production setup
     ./setup.py --label testProd --version 1 + mandatory paramters

The mandatory parameters are better provided by the ./setup.py --help, but some are listed here
   * --installation is a command line to install the production software
   * --setup is a command line to set oneself into the production software
   * --admins is a coma separated list of username as admins

The optional parameters are better liste by the ./setup.py --help, but some are listed here
   * --dataset is a coma separated list of dataset to be processed in input
   * --outsite is the site for crab3 output (defaults to caltech T2)
   * --outpath is the directory path into which to put the crab3 output
   * --participants is a coma separated list of username to take actions in the production

To update any existing member
     ./setup.py --label testProd --version 1 -u --outpath

To update and add to any existing member
     ./setup.py --label testProd --version 1 -u -a --participants someone

Once ready for starting (the list of dataset can be updated later on and at any moment), one can start the production, making it the main current one (the one listed by default)
     ./production.py --do start --label testProd --version 1

The last stared production is de-facto the default argument to --label/--version to ./production.py.

To assign task to registered participants, do one of (note that the assignment is random at the moment, with no consideration on the sample sizes)
     ./production.py --do assign
     ./production.py --do assign --arg [coma separated list of username]
