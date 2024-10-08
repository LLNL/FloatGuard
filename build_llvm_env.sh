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
                    software-properties-common \
                    rocm-llvm-dev

pip3 install pexpect