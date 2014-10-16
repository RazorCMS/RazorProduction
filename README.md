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
To be documented

Vizualisation of on-going production
--------------
Browse to http://cms-caltech-db.cern.ch/ from within cern network

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

