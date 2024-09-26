wget http://www.cs.virginia.edu/~skadron/lava/Rodinia/Packages/rodinia_3.1.tar.bz2

tar -xvf rodinia_3.1.tar.bz2

rm rodinia_3.1.tar.bz2

rm -r rodinia_3.1/openmp rodinia_3.1/opencl rodinia_3.1/bin/
rm -r rodinia_3.1/cuda/b+tree rodinia_3.1/cuda/bfs rodinia_3.1/cuda/huffman rodinia_3.1/cuda/hybridsort 
rm -r rodinia_3.1/cuda/kmeans rodinia_3.1/cuda/leukocyte rodinia_3.1/cuda/mummergpu rodinia_3.1/cuda/pathfinder rodinia_3.1/cuda/cfd.tar
cp rodinia_3.1/data/cfd/* rodinia_3.1/cuda/cfd
cp rodinia_3.1/data/gaussian/* rodinia_3.1/cuda/gaussian
cp rodinia_3.1/data/heartwall/test.avi rodinia_3.1/data/heartwall/input.txt rodinia_3.1/cuda/heartwall
cp rodinia_3.1/data/hotspot/power_* rodinia_3.1/data/hotspot/temp_* rodinia_3.1/cuda/hotspot
cp rodinia_3.1/data/hotspot3D/power_* rodinia_3.1/data/hotspot3D/temp_* rodinia_3.1/cuda/hotspot3D
cp rodinia_3.1/data/lud/* rodinia_3.1/cuda/lud
cp rodinia_3.1/data/myocyte/*.txt rodinia_3.1/cuda/myocyte
cp rodinia_3.1/data/nn/*.db rodinia_3.1/data/nn/filelist.txt rodinia_3.1/cuda/nn
rm rodinia_3.1/cuda/hotspot3D/output.out
rm -r rodinia_3.1/data

patch -p0 < rodinia_patch.txt