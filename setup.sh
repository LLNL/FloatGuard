# NPB-GPU
apt update
apt install -y unzip

cd ~/hipec/benchmarks
git clone https://github.com/GMAP/NPB-GPU
cd NPB-GPU
git checkout f65e28b349bd08594bf94fa22c090c4d70e90ccb
git apply ../NPB-GPU-patch.txt

# PolyBench-ACC
cd ~/hipec/benchmarks
wget https://github.com/cavazos-lab/PolyBench-ACC/archive/refs/tags/v0.1.zip
unzip v0.1.zip
rm v0.1.zip
cd PolyBench-ACC-0.1
rm -r HMPP/ OpenACC/ OpenCL/ OpenMP/
cd ..
patch -p0 < PolyBench-patch.txt

# Rodinia

cd ~/hipec/benchmarks
source setup_rodinia.sh

cd ~/hipec