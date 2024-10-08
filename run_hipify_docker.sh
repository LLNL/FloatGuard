docker container ls -a | grep 'hipify' &> /dev/null
if [ $? == 0 ]; then
    docker start hipify
    docker exec -it --user root hipify bash
else
    docker run -it -v "$PWD":/root/FloatGuard --device=/dev/kfd --device=/dev/dri --security-opt seccomp=unconfined --name hipify doloresmiao/gpu-testing:clang16-cuda12.0
fi