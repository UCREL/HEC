# Resource and Time example

This example shows how to use the [resource library](https://docs.python.org/3.7/library/resource.html) to measure peak memory usage and how to use the [time library](https://docs.python.org/3.7/library/time.html) to find the average time a batch will take to process.

In this example we have a script [./tagging.py](./tagging.py) which takes 3 command line arguments:

1. A file which will be split into paragraphs of text, whereby the paragraphs will be batched and tagged using a SpaCy Named Entity Recognizer (NER).
2. A file to store the Named Entities found through tagging the file found in the first argument. This file will be `TSV` formatted with the following fields:

|paragraph_number|entity text|entity label|start character offset|end character offset|
|-|-|-|-|-|

3. The batch size.

When running the tagging script we will use throughout this example the book Alice in Wonderland as the first argument, of which this book can be found in `txt` format at [./alice-in-wonderland.txt](./alice-in-wonderland.txt).

The output from running the tagging script on Alice in Wonderland can be seen in the [./output.tsv](./output.tsv).

## Overview of the code

Here we will go over the main parts of the code in [./tagging.py](./tagging.py) and where you need to add extra variables and logging calls to output peak memory usage, time, and data statistics.

Lines 61-65 shown below, load the SpaCy model with only the NER tagger enabled, followed by processing the 1st argument (Alice in Wonderland book) so that we have an iterable that yields paragraphs from the given file (the book). We then create another iterable that will group these yielding paragraphs into the correct size batches.

``` python
# Load model
nlp = spacy.load("en_core_web_sm", disable=[ "tagger", "parser"])
# Load data
paragraphs_to_process = yield_paragraphs(text_fp)
batches_to_process = spacy.util.minibatch(paragraphs_to_process, batch_size)
```

We then process these batches using the SpaCy NER model and write the relevant data to the 2nd argument ([./output.tsv](./output.tsv) in our case). While processing these batches we keep track of the number of batches (`number_batches`) and the time it took to process those batches (`batch_time`):

``` python
# Process data
paragraph_number = 0
number_batches = 0
batch_time: List[float] = []
with output_fp.open('w+', newline='') as output_file:
    tsv_writer = csv.writer(output_file, delimiter='\t')
    for batch in batches_to_process:
        number_batches += 1
        start_time = time.perf_counter()
        for spacy_doc in nlp.pipe(batch, batch_size=batch_size):
            for entity in spacy_doc.ents:
                    tsv_writer.writerow([paragraph_number, entity.text, 
                                          entity.label_, 
                                          entity.start_char, 
                                          entity.end_char])
            paragraph_number += 1
        end_time = time.perf_counter()
        batch_time.append(end_time - start_time)
```

After keeping track of batch times we can generate some useful statistics:

``` python
# logs to stdout
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

quickest_batch = f'{min(batch_time):0.4f}'
slowest_batch = f'{max(batch_time):0.4f}'
median_batch = f'{median(batch_time):0.4f}'
logger.info(f'Batch times:')
logger.info(f'Quickest batch: {quickest_batch}')
logger.info(f'Median: {median_batch}')
logger.info(f'Slowest: {slowest_batch}')

logger.info(f'Number of batches: {number_batches}')

median_processing_time = median(batch_time) / batch_size
logger.info(f'Median processing time per sample: {median_processing_time:0.4f}')
logger.info(f'Total number of samples: {paragraph_number}')
```

And using the [resource library](https://docs.python.org/3.7/library/resource.html) we can show the peak amount of memory used:

``` python
logger.info('Peak amount of memory used: '
            f'{getrusage(RUSAGE_SELF).ru_maxrss / 1000} MB')
```

## Running the code

We now show how to run this code on the HEC and your own machine using the Alice in Wonderland book as the 1st argument and [./output.tsv](./output.tsv) as the 2nd argument. The code will be ran twice as we have two different batch sizes **50** and **300**.

Lastly we show how the memory and time information is useful be comparing the outcomes of running the code over the two different batch sizes of 50 and 300.


### Run on the HEC

1. Transfer this directory to your home directory on the HEC: `scp -r ../resource_and_time_example/ username@wayland.hec.lancaster.ac.uk:./`
2. Create the conda environment with the relevant python dependencies and download the SpaCy English model. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the conda environment at `$global_scratch/py3.8-resource-time`
3. We can now run the [./tagging.sh](./tagging.sh) by submitting the following job `qsub tagging.com`
4. You should be able to view the logging/output within the generated stdout file from running `tagging.com`, in my case this is the file called `tagging.o6714707`. You can view the contents of the file with the `cat` command: `cat tagging.o6714707` 

### Run on your own machine

We assume that you have Python >= 3.6.1 and are running either Linux, Mac, or another Linux based system. 

Using Pip:

1. **(Optional)** You can create a conda environment first as a full python virtual environment before installing the pip requirements, rather than installing the pips to a virtualenv or directly to your systems python installation. To create a conda environment for this: `conda create -n resource-example python=3.8`
2. Install the required pips: `pip install -r requirements.txt`
3. Download the SpaCy NER model `python -m spacy download en_core_web_sm`
4. run `bash tagging.sh` 
5. The logging/output should be displayed in the terminal/console you are running this script from.
6. **(Optional)** to remove the conda environment afterwards run; `conda deactivate && conda env remove -n resource-example`

Using conda:

1. Install the required pips: `conda env create -n resource-example --file ./environment.yaml`
2. Activate the new conda environment `conda activate resource-example`
3. Download the SpaCy NER model `python -m spacy download en_core_web_sm`
4. run `bash tagging.sh`
5. The logging/output should be displayed in the terminal/console you are running this script from.
6. If you want to remove this conda environment afterwards run; `conda deactivate && conda env remove -n resource-example`

### Comparing results

**Note** These results came from running on my own Ubuntu machine, when using the HEC I got median processing time per sample of 0.0023 and 0.0022 for a batch size of 50 and 300 respectively.

From running this we get the following output for batch size 50:
``` bash
2021-01-13 08:52:18,833 - __main__ - INFO - Batch times:
2021-01-13 08:52:18,834 - __main__ - INFO - Quickest batch: 0.0600
2021-01-13 08:52:18,834 - __main__ - INFO - Median: 0.0900
2021-01-13 08:52:18,834 - __main__ - INFO - Slowest: 0.1630
2021-01-13 08:52:18,834 - __main__ - INFO - Number of batches: 18
2021-01-13 08:52:18,834 - __main__ - INFO - Median processing time per sample: 0.0018
2021-01-13 08:52:18,834 - __main__ - INFO - Total number of samples: 881
2021-01-13 08:52:18,834 - __main__ - INFO - Peak amount of memory used: 120.072 MB
```

And for batch size 300:
``` bash
2021-01-13 08:52:13,811 - __main__ - INFO - Batch times:
2021-01-13 08:52:13,811 - __main__ - INFO - Quickest batch: 0.4044
2021-01-13 08:52:13,811 - __main__ - INFO - Median: 0.4582
2021-01-13 08:52:13,811 - __main__ - INFO - Slowest: 0.7069
2021-01-13 08:52:13,811 - __main__ - INFO - Number of batches: 3
2021-01-13 08:52:13,811 - __main__ - INFO - Median processing time per sample: 0.0015
2021-01-13 08:52:13,811 - __main__ - INFO - Total number of samples: 881
2021-01-13 08:52:13,811 - __main__ - INFO - Peak amount of memory used: 283.088 MB
```

From the output it is clear to see that using a batch size of 300 uses more than double the amount of memory. However per paragraph (sample) it is 0.0003 seconds quicker on average. Thus over the 881 paragraphs using a batch size of 300 would on average be 0.2643 seconds quicker. That time difference is not much but if you were processing 1 million paragraphs using a batch size of 300 compared to 50 would be 5 minutes quicker. 

From these outputs it means we can estimate how long a job will take and how much memory to allocate if we had to process 1000 books if we assume that each book is of similar length to Alice in Wonderland, in this case for a batch size of 300, 1000 books will take around (881 (number paragraphs) * 1000 (number books) * 0.0015 (processing time per paragraph)) 1321.5 seconds with a peak memory usage of around 283MB. It is advised to add some extra memory and time to these estimates.



