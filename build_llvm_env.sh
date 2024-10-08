apt-get update -y
apt-get install -y apt-utils unzip dos2unix
DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
apt-get upgrade -y
apt-get install -y python3=3.10.6-1~22.04.1 python3-pip=22.0.2+dfsg-1ubuntu0.4 \
                    git=1:2.34.1-1ubuntu1.11 \
                    wget=1.21.2-2ubuntu1.1 \
                    build-essential=12.9ubuntu3 \
                    cmake=3.22.1-1ubuntu1.22.04.2 \
                    lsb-release=11.1.0ubuntu4 \
                    software-properties-common=0.99.22.9 \
                    rocm-llvm-dev=17.0.0.24193.60102-119~22.04

pip3 install pexpect==4.9.0