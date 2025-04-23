#EXEs=$(find Samples/ -type f -executable) # find all executable paths
MAKEFILES=$(find ./ -name "Makefile") # find all executable paths
for mkfile in ${MAKEFILES}
do
        mk=${mkfile##*/} # get the name of executable [[Bash -- get the last substring for a separator]]
        size=${#mk} #[[Bash -- get the length of a string]]
        dir=${mkfile::(-$size+0)} #[[Bash -- get the specific substring]]
        cd $dir;
        echo "in ${dir}....." 
        #(time eval ${PRELOAD_FLAG} "./${run}") >stdout.txt 2>stderr.txt
        rm -rf counts*.txt *gpufpx* stdout* stderr* *.sh
        make clean 
	cd -;
done
