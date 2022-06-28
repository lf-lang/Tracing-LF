# Tracing-LF

Project aiming to analyse Lingua-Franca programs (with a current focus on the C++ target) in order to find possible optimisations. 

Makes use of the Bokeh Library (https://docs.bokeh.org/en/latest/index.html) to generate a visualisation of the trace

## Running the visualisation 

1. Steps 1-3 must be completed from the C++ tracing guide (https://github.com/lf-lang/lingua-franca/wiki/Tracing#TracingInCpp)
2. ```lfc``` (lingua-franca compiler) must be on your PATH
3. Make sure to install ```bokeh``` and ```regex``` for your python version 
4. Modify the target declaration of your Lingua Franca program to enable tracing and exporting of the yaml file:
```
target Cpp {
    tracing: true,
    export-to-yaml: true
};
```
5. Change your current working directory to ```SchedulingLF/scripts/``` 
6. Run ```record_trace.sh /path/to/lingua-franca/program/``` 
7. Open the produced .html file



## Options
```-hv```

Holoviews visualisation. Tailored to large programs, losing some features of regular visualisation

```-hw```

Holoviews visualisation from WORKER perspective

```-p```

Adds an additional plain view 

```-l```

Adds a view of only physical executions, with vertical lines denoting start and end of logical times

```-i``` / ```-e```

(i - include, e - exclude)

Used to filter reactions included in the visualisation. Pass some regex string as argument to filter
