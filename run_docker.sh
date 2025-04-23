docker container ls -a | grep 'FloatGuard' &> /dev/null
if [ $? == 0 ]; then
    docker start FloatGuard
    docker exec -it --user root FloatGuard bash
else
    docker run -it -v "$PWD":/root/FloatGuard --device /dev/kfd --device /dev/dri/renderD128 --security-opt seccomp=unconfined --name FloatGuard ucdavisplse/floatguard:latest
fi