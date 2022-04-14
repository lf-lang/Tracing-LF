# Tracing-LF

Project aiming to analyse Lingua-Franca programs (with a current focus on the C++ target) in order to find possible optimisations. 

Makes use of the Bokeh Library (https://docs.bokeh.org/en/latest/index.html) to generate a visualisation of the trace

## Running the visualisation (Fix in progress, not currently available!)

1. Steps 1-3 must be completed from the C++ tracing guide (https://github.com/lf-lang/lingua-franca/wiki/Tracing#TracingInCpp)
2. ```lfc``` (lingua-franca compiler) must be on your PATH
3. Make sure to install ```bokeh``` and '```regex``` for your python version 
4. Modify the target declaration of your Lingua Franca program to enable tracing and export the yaml file:
```
target Cpp {
    tracing: true,
    export-to-yaml: true
};
```
5. Change your current working directory to ```SchedulingLF/scripts/``` 
6. Run the ```record_trace.sh``` script
7. Open the produced .html file
