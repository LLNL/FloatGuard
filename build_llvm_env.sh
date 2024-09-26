apt-get update -y
apt-get install -y apt-utils
DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
apt-get upgrade -y
apt-get install -y python3 python3-pip \
                    git \
                    wget \
                    build-essential \
                    cmake \
                    libboost-all-dev \
                    lsb-release \
                    software-properties-common

pip3 install pexpect
git clone https://github.com/ROCm/llvm-project/ /root/llvm-project
cd /root/llvm-project
git checkout tags/rocm-6.1.2

mkdir build
cd build
cmake -DLLVM_BUILD_EXAMPLES=1 -DCLANG_BUILD_EXAMPLES=1 -DLLVM_ENABLE_PROJECTS="clang;lld;lldb" -DCMAKE_INSTALL_PREFIX="" -DCMAKE_BUILD_TYPE="Release" -G "Unix Makefiles" ../llvm
make -j8
make install

rm -r /root/llvm-project