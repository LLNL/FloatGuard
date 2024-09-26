FROM rocm/dev-ubuntu-22.04:6.1.2
USER root

LABEL maintainer="wjmiao@ucdavis.edu"

WORKDIR /root/

COPY build_llvm_env.sh /root/

RUN /root/build_llvm_env.sh
