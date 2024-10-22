# NPB-GPU
cd benchmarks
git clone https://github.com/GMAP/NPB-GPU
cd NPB-GPU
git checkout f65e28b349bd08594bf94fa22c090c4d70e90ccb
git apply ../NPB-GPU-patch.txt
cd ..

read -p "Press enter to continue"

# PolyBench-ACC
wget https://github.com/cavazos-lab/PolyBench-ACC/archive/refs/tags/v0.1.zip
unzip v0.1.zip
rm v0.1.zip
cd PolyBench-ACC-0.1
rm -r HMPP/ OpenACC/ OpenCL/ OpenMP/
cd ..
patch -p0 < PolyBench-patch.txt

read -p "Press enter to continue"

# Rodinia

sh setup_rodinia.sh

cd ..