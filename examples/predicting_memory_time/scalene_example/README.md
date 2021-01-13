# Scalene example

**Note** only use a profiler like Scalene when debugging/testing your code and not when you want to run your code on the full task as the profiler will slow your code down and also should not be needed.

For those that have read the example of how to use the resource and time libraries at [../resource_and_time_example/README.md](./resource_and_time_example/README.md), the [./tagging.py](./tagging.py) python script performs the same function but does not contain the timing or resource code that is logged as we are demonstrating the scalene profiler in this example. 

This example shows how to use the [Scalene profiler](https://github.com/emeryberger/scalene). This example will run the profiler over the [./tagging.py](./tagging.py) with a batch size of 50 and 300 whereby the profiler output is saved to [./scalene_output/scalene_50.txt](./scalene_output/scalene_50.txt) and [./scalene_output/scalene_300.txt](./scalene_output/scalene_300.txt) respectively. The [./tagging.py](./tagging.py) script runs the SpaCy English small Named Entity Recognition (NER) model over the Alice in Wonderland text, which can be found at [./alice-in-wonderland.txt](./alice-in-wonderland.txt), and outputs the found entities to the [./output.tsv](./output.tsv) file.


The command to run `scalene` with these two batch sizes can be found in the [./scalene.sh](./scalene.sh) script of which this is shown below, we also run the profiler with the flag `--reduced-profile` (only shows lines of code that have an affect on CPU/memory) so that we can more easily compare the script using batch sizes of 50 and 300:

``` bash
#!/bin/bash

mkdir ./scalene_output
scalene --outfile ./scalene_output/scalene_50.txt  tagging.py alice-in-wonderland.txt output.tsv 50
scalene --outfile ./scalene_output/scalene_300.txt  tagging.py alice-in-wonderland.txt output.tsv 300

scalene --outfile ./scalene_output/scalene_reduced_50.txt  --reduced-profile tagging.py alice-in-wonderland.txt output.tsv 50
scalene --outfile ./scalene_output/scalene_reduced_300.txt  --reduced-profile tagging.py alice-in-wonderland.txt output.tsv 300
```

The profiler does not require any extra code to be added to your scripts, rather it is called as a program through the command line as shown above.

## To run on the HEC:

1. Transfer this directory to your home directory on the HEC: `scp -r ../scalene_example/ username@wayland.hec.lancaster.ac.uk:./`
2. Create the conda environment with the relevant python dependencies and download the SpaCy English model. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the conda environment at `$global_scratch/py3.8-scalene`
3. We can now run the [./scalene.sh](./scalene.sh) by submitting the following job `qsub scalene.com`
4. You should be able to view the outputs from `scalene` in the `scalene_output` directory e.g. to see the output from batch size 50 without the `reduced-profile`: `cat ./scalene_output/scalene_50.txt`
5. To get the scalene profile outputs into the current directory from the HEC, assuming you are in this directory on your own computer: `scp -r username@wayland.hec.lancaster.ac.uk:./scalene_example/scalene_output .`

## To run on your own computer

We assume that you have Python >= 3.6.1 and are running either Linux, Mac, or another Linux based system. 

Using Pip:

1. **(Optional)** You can create a conda environment first as a full python virtual environment before installing the pip requirements, rather than installing the pips to a virtualenv or directly to your systems python installation. To create a conda environment for this: `conda create -n scalene-example python=3.8`
2. Install the required pips: `pip install -r requirements.txt`
3. Download the SpaCy NER model `python -m spacy download en_core_web_sm`
4. run `bash scalene.sh` 
5. **(Optional)** to remove the conda environment afterwards run; `conda deactivate && conda env remove -n scalene-example`

Using conda:

1. Install the required pips: `conda env create -n scalene-example --file ./environment.yaml`
2. Activate the new conda environment `conda activate scalene-example`
3. Download the SpaCy NER model `python -m spacy download en_core_web_sm`
4. run `bash scalene.sh`
5. If you want to remove this conda environment afterwards run; `conda deactivate && conda env remove -n scalene-example`

## Scalene output

As stated earlier it is easier to compare the scalene profiles when the `--reduced-profile` flag has been used. The first output shown below is when using the batch size of 50:
``` python
           Memory usage: ▆▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇█▇▇ (max: 150.00MB)            
                tagging.py: % of time = 100.00% out of  11.47s.                
       ╷       ╷        ╷     ╷       ╷      ╷              ╷       ╷          
  Line │Time % │Time %  │Sys  │Mem %  │Net   │Memory usage  │Copy   │          
       │Python │native  │%    │Python │(MB)  │over time / % │(MB/s) │tagging…  
╺━━━━━━┿━━━━━━━┿━━━━━━━━┿━━━━━┿━━━━━━━┿━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━━╸
   ... │       │        │     │       │      │              │       │          
     2 │       │        │     │   51% │    0 │▁▁▁▁▁▁        │       │import…   
   ... │       │        │     │       │      │              │       │          
     6 │    6% │     1% │     │       │   22 │▁▁▁▁▁▁ 60%    │     2 │import…   
   ... │       │        │     │       │      │              │       │          
    27 │       │        │     │  100% │    8 │▁             │       │    wi…   
   ... │       │        │     │       │      │              │       │          
    29 │       │        │     │  100% │   -1 │▁▁▁           │       │      …   
   ... │       │        │     │       │      │              │       │          
    31 │       │        │     │  100% │    1 │▁             │       │      …   
   ... │       │        │     │       │      │              │       │          
    45 │       │        │     │  100% │    1 │▁             │       │    pa…   
   ... │       │        │     │       │      │              │       │          
    59 │   14% │     2% │     │   71% │   51 │▁▁▁▁▁▁▁▁▁     │     3 │    nl…   
   ... │       │        │     │       │      │              │       │          
    67 │       │        │     │  100% │    8 │▁             │       │    wi…   
   ... │       │        │     │       │      │              │       │          
    71 │   73% │     3% │ 37% │   88% │   47 │▂▂▂▂          │    77 │      …   
   ... │       │        │     │       │      │              │       │          
    73 │       │        │     │  100% │    1 │▁▁▁           │       │      …   
   ... │       │        │     │       │      │              │       │          
       ╵       ╵        ╵     ╵       ╵      ╵              ╵       ╵          
```


And when using the batch size of 300:

``` python
             Memory usage: ▃▄▄▄▄▄▄▄▄▅▅▅▅▅▅▅▅▅▅▅▅▅▄ (max: 344.00MB)             
                tagging.py: % of time = 100.00% out of   9.20s.                
       ╷       ╷        ╷     ╷       ╷      ╷              ╷       ╷          
  Line │Time % │Time %  │Sys  │Mem %  │Net   │Memory usage  │Copy   │          
       │Python │native  │%    │Python │(MB)  │over time / % │(MB/s) │tagging…  
╺━━━━━━┿━━━━━━━┿━━━━━━━━┿━━━━━┿━━━━━━━┿━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━━╸
   ... │       │        │     │       │      │              │       │          
     2 │       │        │     │       │   10 │▁▁▁▁▁▁        │       │import…   
   ... │       │        │     │       │      │              │       │          
     6 │    8% │     2% │     │       │   45 │▁▁▁▁▁▁▁ 65%   │     3 │import…   
   ... │       │        │     │       │      │              │       │          
    27 │       │        │     │  100% │    8 │▁             │       │    wi…   
   ... │       │        │     │       │      │              │       │          
    31 │       │        │     │  100% │   -9 │▁▁▁▁          │       │      …   
   ... │       │        │     │       │      │              │       │          
    33 │       │        │     │  100% │    1 │▁             │       │      …   
   ... │       │        │     │       │      │              │       │          
    59 │   19% │     2% │  2% │   69% │   20 │▁▁▁▁▁▁▁▁▁     │     4 │    nl…   
   ... │       │        │     │       │      │              │       │          
    67 │       │        │     │       │    5 │▁             │       │    wi…   
   ... │       │        │     │       │      │              │       │          
    71 │   59% │     9% │ 35% │   65% │  101 │▁▁▁▁          │    87 │      …   
    72 │       │        │     │  100% │    0 │▁▁            │       │      …   
    73 │       │        │     │  100% │    2 │▁▁            │       │      …   
   ... │       │        │     │       │      │              │       │          
       ╵       ╵        ╵     ╵       ╵      ╵              ╵       ╵          
```

The code snippets show that for the batch size of 300 more memory is used in total (344MB compared to 150MB) which is expected as we are processing more text in one go. Further we can see that the majority of the time is spent on processing the data (line 71). Loading the SpaCy model (line 59) from the *Net (MB)* column uses between 20MB and 51MB and up to 21% (19% + 2% coming from the output of batch size 300) of the time running the code.

You will notice that in both of these the code snippet at the end of each line either does not exist or has been cut off. I don't know why this happens when the output has come the HEC but I know that if I run this code on my own Ubuntu and Mac machine I do not have this problem and the output should look like this:

``` python
                                                                     Memory usage: ▅▄▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅▅ (max: 206.00MB)                                                                      
                                                                      tagging.py: % of time = 100.00% out of   6.65s.                                                                       
       ╷       ╷        ╷     ╷       ╷      ╷              ╷       ╷                                                                                                                       
  Line │Time % │Time %  │Sys  │Mem %  │Net   │Memory usage  │Copy   │                                                                                                                       
       │Python │native  │%    │Python │(MB)  │over time / % │(MB/s) │tagging.py                                                                                                             
╺━━━━━━┿━━━━━━━┿━━━━━━━━┿━━━━━┿━━━━━━━┿━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸
   ... │       │        │     │       │      │              │       │                                                                                                                       
     6 │    8% │    11% │     │   98% │   48 │▁▁▁▁▁▁        │     5 │import spacy                                                                                                           
   ... │       │        │     │       │      │              │       │                                                                                                                       
    29 │       │        │     │  100% │    6 │▁▁▁▁▁▁        │       │        for line in _file:                                                                                             
    30 │       │        │     │  100% │    1 │▁             │       │            if line.strip():                                                                                           
   ... │       │        │     │       │      │              │       │                                                                                                                       
    59 │   18% │     2% │  1% │   98% │   51 │▁▁▁▁▁▁        │     4 │    nlp = spacy.load("en_core_web_sm", disable=[ "tagger", "parser"])                                                  
   ... │       │        │     │       │      │              │       │                                                                                                                       
    71 │   60% │     1% │ 21% │   88% │    4 │▄▄▄▄ 79%      │   133 │            for spacy_doc in nlp.pipe(batch, batch_size=batch_size):                                                   
    72 │       │        │     │  100% │    0 │▁▁            │       │                for entity in spacy_doc.ents:                                                                          
    73 │       │        │     │  100% │    2 │▁▁            │       │                        tsv_writer.writerow([paragraph_number, entity.text,                                            
   ... │       │        │     │       │      │              │       │                                                                                                                       
    76 │       │        │     │  100% │    0 │▁▁            │       │                                             entity.end_char])                                                         
   ... │       │        │     │       │      │              │       │                                                                                                                       
       ╵       ╵        ╵     ╵       ╵      ╵              ╵       ╵                                                                                                                       
```
