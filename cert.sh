## get scram and all
source /afs/cern.ch/cms/cmsset_default.sh

## get the sso cookie
cern-get-sso-cookie -u https://cms-caltech-db.cern.ch -o ~/private/ct-cookie.txt --krb

## setup a cannocial location for a proxy
export X509_USER_PROXY=$HOME/cert/voms_proxy.cert

## make sure the protection is right 
#chmod 700 $HOME/cert/voms_proxy.cert

## create a long lived proxy in the designated location
cat $HOME/private/$USER.txt | voms-proxy-init -voms cms --valid 48:00 -pwstdin

## make sure the protection is right 
#chmod 400 $HOME/cert/voms_proxy.cert
