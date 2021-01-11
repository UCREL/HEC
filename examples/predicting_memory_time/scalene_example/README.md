# Scalene example

This example shows how to use the [Scalene profiler](https://github.com/emeryberger/scalene). This example will run the profiler over the [./tagging.py](./tagging.py) with a batch size of 50 and 300 whereby the profiler output is saved to [./scalene_50.html](./scalene_50.html) and [./scalene_300.html](./scalene_300.html) respectively. The [./tagging.py](./tagging.py) script runs the SpaCy English small Named Entity Recognition (NER) model over the Alice in Wonderland text, which can be found at [./alice-in-wonderland.txt](./alice-in-wonderland.txt), and outputs the found entities to the [./output.tsv](./output.tsv) file.


The command to run `scalene` with these two batch sizes can be found in the [./scalene.sh](./scalene.sh) script of which this is shown below, we also run the profiler with the flag `--reduced-profile` (only shows lines of code that have an affect on CPU/memory) so that we can more easily compare the script using batch sizes of 50 and 300:

``` bash
#!/bin/bash

mkdir ./scalene_output
scalene --outfile ./scalene_output/scalene_50.html --html tagging.py alice-in-wonderland.txt output.tsv 50
scalene --outfile ./scalene_output/scalene_300.html --html tagging.py alice-in-wonderland.txt output.tsv 300

scalene --outfile ./scalene_output/scalene_reduced_50.html --html --reduced-profile tagging.py alice-in-wonderland.txt output.tsv 50
scalene --outfile ./scalene_output/scalene_reduced_300.html --html --reduced-profile tagging.py alice-in-wonderland.txt output.tsv 300
```

The profiler does not require any extra code to be added to your scripts, rather it is called as a program through the command line as shown above.

## To run on the HEC:

1. Transfer this directory to your home directory on the HEC: `scp -r ../scalene_example/ username@wayland.hec.lancaster.ac.uk:./`
2. Create the conda environment with the relevant python dependencies and download the SpaCy English model. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the conda environment at `$global_scratch/py3.8-scalene`
3. We can now run the [./scalene.sh](./scalene.sh) by submitting the following job `qsub scalene.com`
4. To get the scalene profile outputs into the current directory from the HEC: `scp -r username@wayland.hec.lancaster.ac.uk:./scalene_example/scalene_output .`

## Scalene output

As stated earlier it is easier to compare the scalene profiles when the `--reduced-profile` flag has been used. The first output shown below is when using the batch size of 50:
``` html
<!DOCTYPE html>
<head>
<meta charset="UTF-8">
<style>
.r1 {color: #000080}
.r2 {font-weight: bold}
.r3 {color: #008000; background-color: #f8f8f8; font-weight: bold}
.r4 {color: #000000; background-color: #f8f8f8}
.r5 {color: #800000; font-weight: bold}
.r6 {color: #0000ff}
body {
    color: #000000;
    background-color: #ffffff;
}
</style>
</head>
<html>
<body>
    <code>
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">                 Memory usage: <span class="r1">▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇</span> (max: 197.00MB)                 
                tagging.py: % of time = 100.00% out of  12.52s.                
       ╷       ╷        ╷     ╷       ╷      ╷              ╷       ╷          
 <span class="r2"> Line </span>│<span class="r2">Time % </span>│<span class="r2">Time %  </span>│<span class="r2">Sys  </span>│<span class="r2">Mem %  </span>│<span class="r2">Net   </span>│<span class="r2">Memory usage  </span>│<span class="r2">Copy   </span>│<span class="r2">         </span> 
       │<span class="r2">Python </span>│<span class="r2">native  </span>│<span class="r2">%    </span>│<span class="r2">Python </span>│<span class="r2">(MB)  </span>│<span class="r2">over time / % </span>│<span class="r2">(MB/s) </span>│<span class="r2">tagging… </span> 
╺━━━━━━┿━━━━━━━┿━━━━━━━━┿━━━━━┿━━━━━━━┿━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━━╸
   ... │       │        │     │       │      │              │       │          
     2 │       │        │     │       │   58 │▁▁▁▁▁▁        │       │<span class="r3">import</span><span class="r4">…</span>   
   ... │       │        │     │       │      │              │       │          
     6 │    8% │     1% │     │       │   -2 │▂▂▂▂▂▂▂▂ 59%  │     2 │<span class="r3">import</span><span class="r4">…</span>   
   ... │       │        │     │       │      │              │       │          
    27 │       │        │     │       │    8 │▁             │       │<span class="r4">    </span><span class="r3">wi…</span>   
   ... │       │        │     │       │      │              │       │          
    29 │       │        │     │   67% │    3 │▁▁▁           │       │<span class="r4">      …</span>   
   ... │       │        │     │       │      │              │       │          
    59 │   18% │     3% │  2% │   64% │   -3 │▁▁▁▁▁▁▁▁▁     │     3 │<span class="r4">    nl…</span>   
   ... │       │        │     │       │      │              │       │          
    67 │       │        │     │       │    8 │▁             │       │<span class="r4">    </span><span class="r3">wi…</span>   
   ... │       │        │     │       │      │              │       │          
    71 │<span class="r5">   68%</span> │<span class="r5">     2%</span> │ 42% │   90% │  103 │<span class="r5">▂▂▂▂▂▂▂</span>       │    71 │<span class="r4">      …</span>   
   ... │       │        │     │       │      │              │       │          
    73 │       │        │     │  100% │   -2 │▁▁▁▁          │       │<span class="r4">      …</span>   
   ... │       │        │     │       │      │              │       │          
       ╵       ╵        ╵     ╵       ╵      ╵              ╵       ╵          
generated by the <a href="https://github.com/emeryberger/scalene"><span class="r6">scalene</span></a> profiler                                               
</pre>
    </code>
</body>
</html>
```


And when using the batch size of 300:

``` html
<!DOCTYPE html>
<head>
<meta charset="UTF-8">
<style>
.r1 {color: #000080}
.r2 {font-weight: bold}
.r3 {color: #008000; background-color: #f8f8f8; font-weight: bold}
.r4 {color: #000000; background-color: #f8f8f8}
.r5 {color: #800000; font-weight: bold}
.r6 {color: #0000ff}
body {
    color: #000000;
    background-color: #ffffff;
}
</style>
</head>
<html>
<body>
    <code>
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">            Memory usage: <span class="r1">▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▇▇█▇▇▇▇▇▇▇</span> (max: 322.00MB)            
                tagging.py: % of time = 100.00% out of  11.23s.                
       ╷       ╷        ╷     ╷       ╷      ╷              ╷       ╷          
 <span class="r2"> Line </span>│<span class="r2">Time % </span>│<span class="r2">Time %  </span>│<span class="r2">Sys  </span>│<span class="r2">Mem %  </span>│<span class="r2">Net   </span>│<span class="r2">Memory usage  </span>│<span class="r2">Copy   </span>│<span class="r2">         </span> 
       │<span class="r2">Python </span>│<span class="r2">native  </span>│<span class="r2">%    </span>│<span class="r2">Python </span>│<span class="r2">(MB)  </span>│<span class="r2">over time / % </span>│<span class="r2">(MB/s) </span>│<span class="r2">tagging… </span> 
╺━━━━━━┿━━━━━━━┿━━━━━━━━┿━━━━━┿━━━━━━━┿━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━━╸
   ... │       │        │     │       │      │              │       │          
     2 │       │        │     │       │   12 │▁▁▁▁▁▁▁       │       │<span class="r3">import</span><span class="r4">…</span>   
   ... │       │        │     │       │      │              │       │          
     6 │    9% │     1% │     │       │   28 │▁▁▁▁▁▁▁ 65%   │     2 │<span class="r3">import</span><span class="r4">…</span>   
   ... │       │        │     │       │      │              │       │          
    27 │       │        │     │       │    8 │▁             │       │<span class="r4">    </span><span class="r3">wi…</span>   
   ... │       │        │     │       │      │              │       │          
    29 │       │        │     │  100% │    4 │▁▁▁▁          │       │<span class="r4">      …</span>   
   ... │       │        │     │       │      │              │       │          
    31 │       │        │     │  100% │    0 │▁▁            │       │<span class="r4">      …</span>   
   ... │       │        │     │       │      │              │       │          
    59 │   21% │     3% │  2% │   70% │   39 │▁▁▁▁▁▁▁       │     3 │<span class="r4">    nl…</span>   
   ... │       │        │     │       │      │              │       │          
    67 │       │        │     │       │    8 │▁             │       │<span class="r4">    </span><span class="r3">wi…</span>   
   ... │       │        │     │       │      │              │       │          
    71 │<span class="r5">   53%</span> │<span class="r5">    12%</span> │ 38% │   69% │  150 │<span class="r5">▂▂▂▂</span>          │    69 │<span class="r4">      …</span>   
   ... │       │        │     │       │      │              │       │          
    73 │       │        │     │       │   19 │▁▁▁▁▁▁▁▁      │       │<span class="r4">      …</span>   
   ... │       │        │     │       │      │              │       │          
       ╵       ╵        ╵     ╵       ╵      ╵              ╵       ╵          
generated by the <a href="https://github.com/emeryberger/scalene"><span class="r6">scalene</span></a> profiler                                               
</pre>
    </code>
</body>
</html>
```
