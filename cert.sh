## setup a cannocial location for a proxy
export X509_USER_PROXY=$HOME/cert/voms_proxy.cert

## make sure the protection is right 
#chmod 700 $HOME/cert/voms_proxy.cert

## create a long lived proxy in the designated location
cat $HOME/private/$USER.txt | voms-proxy-init -voms cms --valid 48:00 -pwstdin

## make sure the protection is right 
#chmod 400 $HOME/cert/voms_proxy.cert
