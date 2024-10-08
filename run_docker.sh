docker container ls -a | grep 'hipec' &> /dev/null
if [ $? == 0 ]; then
    docker start hipec
    docker exec -it --user root hipec bash
else
    docker run -it -v "$PWD":/root/hipec --device /dev/kfd --device /dev/dri --security-opt seccomp=unconfined --name hipec ucdavisplse/hipec:latest
fi