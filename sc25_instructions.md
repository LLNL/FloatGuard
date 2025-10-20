# Live Demo 1: Detecting FP Exceptions Manually

1. Compile sample program

```
cd samples/div0
make
```

2. Run ROCgdb with the sample program; no exceptions

```
rocgdb div0
(when you are inside ROCgdb) r
```

3. Use “b [kernel name]” to add breakpoints, then run the program again

```
b kernel_int # or other kernels in div0.cpp
r
```

4. When program is stopped at breakpoint, change mode register value

```
p $mode=0x5F2F0
c
```

5. Exception occurs

# Live Demo 2/3 - Running FloatGuard on Sample & Benchmarks

1. Go to [sample/benchmark] directory

```
cd samples/div0
```
   
3. Run the tool while inside the directory

```  
python3 [FloatGuard dir]/gdb_script/time_measure.py
```

5. Inspect results in the results/ directory
