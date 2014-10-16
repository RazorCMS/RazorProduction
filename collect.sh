## this can be a soft link
cd $HOME/ntprod/

source RazorProduction/cert.sh

## run the task collection
./production.py --do collect $1
