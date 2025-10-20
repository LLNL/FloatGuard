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
