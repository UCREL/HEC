# GPU Example

In this example we will show how to run a GPU job and find the amount of GPU and RAM memory required to run that job and different memory requirements for different parts of the code. Allowing you to know how a GPU job will scale when you increase the batch size (number of samples you are processing in one go) of your job and also how much memory is required to load your model. The libraries that will be used in this example are:

1. [pynvml](https://pypi.org/project/nvidia-ml-py3/) -- For GPU memory usage. Reports usage in Bytes.
2. [resource library](https://docs.python.org/3.7/library/resource.html) -- For RAM memory usage.
3. [time library](https://docs.python.org/3.7/library/time.html) -- For timing the script.

Further we also go over whether GPU memory usage can be estimated from RAM (answer is no) in the section [Estimating GPU memory through CPU and RAM](#estimating-gpu-memory-through-cpu-and-ram).

This example is similar to the other two examples [../resource_and_time_example/README.md](../resource_and_time_example/README.md) and [../scalene_example/README.md](../scalene_example/README.md) we are going to run the script [./gpu_stanza_tagging.py](./gpu_stanza_tagging.py) which takes 4 arguments:

1. A file which will be split into paragraphs of text, whereby the paragraphs will be batched and tagged using the [Stanza Named Entity Recognizer (NER)](https://stanfordnlp.github.io/stanza/ner.html).
2. A file to store the Named Entities found through tagging the file found in the first argument. This file will be `TSV` formatted with the following fields:

|paragraph_number|entity text|entity label|start character offset|end character offset|
|-|-|-|-|-|

3. The batch size.
4. A file path to a directory that will store the Stanza pre-trained models that the script downloads. 

When running the tagging script we will use throughout this example the book Alice in Wonderland as the first argument, of which this book can be found in `txt` format at [./alice-in-wonderland.txt](./alice-in-wonderland.txt).

The output from running the tagging script on Alice in Wonderland can be seen in the [./output.tsv](./output.tsv).

## Overview of the code

Here we will go over the main parts of the code in [./gpu_stanza_tagging.py](./gpu_stanza_tagging.py).

Lines 70-75 shown below, `nvmlInit()` allows us to start tracking the amount of GPU memory being used. `gpu_handle = nvmlDeviceGetHandleByIndex(0)` is a pointer that will be used to get information about GPU at index `0`, if you have access to only one GPU then it should always be accessible from index `0`. Each time you want information from a GPU you have to call `nvmlDeviceGetMemoryInfo` with the GPU handle of the GPU you want information about. So in the code below we get the amount of GPU memory being used from GPU at index `0` before we do any processing (this should return 0, if you are running this on your own machine the likelihood is that this will return > 0 for my machine it is around 1.3GB as it runs the Graphical User Interface):

``` python
# Allows us to sample statistics from the nvidia GPU
nvmlInit()
# Assuming we only have access to one GPU
gpu_handle = nvmlDeviceGetHandleByIndex(0)
gpu_info = nvmlDeviceGetMemoryInfo(gpu_handle)
gpu_memory_start = bytes_to_GB(gpu_info.used)
```

We then download the Stanza model to the directory given in argument 4 to the script. Then load the Stanza model specifying that we want to use the GPU and the batch size we want the tokenizer and NER models to process (always lookup the Stanza documentation for the different definitions of batch size processing for the Stanza models as some define a sample in a [batch as a word (POS model)](https://stanfordnlp.github.io/stanza/pos.html), [sentence](https://stanfordnlp.github.io/stanza/ner.html), or [text/paragraph](https://stanfordnlp.github.io/stanza/tokenize.html)). After loading the model we get the amount of GPU memory used for loading the model.

``` python
# Download the relevant stanza model if it has not already been downloaded.
stanza_processes = 'tokenize,ner'
stanza.download("en", dir=str(stanza_model_directory), 
                processors=stanza_processes)
# load the stanza model
nlp = stanza.Pipeline(lang='en', processors=stanza_processes, use_gpu=True,
                        tokenize_batch_size=batch_size,
                        ner_batch_size=batch_size,
                        dir=str(stanza_model_directory))

# GPU memory used for loading model
gpu_info = nvmlDeviceGetMemoryInfo(gpu_handle)
gpu_memory_before_processing = bytes_to_GB(gpu_info.used)
gpu_memory_for_model = gpu_memory_before_processing - gpu_memory_start
```

After loading the model we create an iterable from the text file (argument 1) so that we can process the text in batches of paragraphs. We keep track of the number of paragraphs processed and the time taken to process all paragraphs. Unlike the [resource library](https://docs.python.org/3.7/library/resource.html) library for RAM memory tracking we cannot request the peak amount of GPU memory used after the event. Therefore to find an estimate for this we sample every 50 paragraphs the amount of GPU memory used.

``` python
# Load data
paragraphs_to_process = yield_paragraphs(text_fp)

# Process data
paragraph_number = 0
processing_time: float = 0.0
gpu_memory_used_during_processing: List[int] = []
with output_fp.open('w+', newline='') as output_file:
    tsv_writer = csv.writer(output_file, delimiter='\t')
    start_time = time.perf_counter()
    for stanza_document in batch(paragraphs_to_process, nlp, batch_size=batch_size):
        for entity in stanza_document.ents:
            tsv_writer.writerow([paragraph_number, entity.text, 
                                    entity.type, 
                                    entity.start_char, 
                                    entity.end_char])
        paragraph_number += 1
        # Only sample the amount of memory used every N (N=50 in this case)
        # documents. The more we sample the better we map the amount 
        # of GPU memory being used, but can take longer especially with lots 
        # of documents/paragraphs. 
        if paragraph_number % 50 == 0:
            gpu_info = nvmlDeviceGetMemoryInfo(gpu_handle)
            gpu_memory_used = bytes_to_GB(gpu_info.used) - gpu_memory_before_processing
            gpu_memory_used_during_processing.append(gpu_memory_used)

    end_time = time.perf_counter()
    processing_time = end_time - start_time
```

We then log the amount of time it took to process the whole text and the mean time it took to process the a batch. These timings can be useful to know so that you can estimate larger jobs.

``` python
logger.info(f'Total time: {processing_time:.4f}s')

mean_batch_time = (processing_time / paragraph_number) * batch_size
logger.info(f'Mean batch time for batch size {batch_size}: {mean_batch_time:.4f}s')
logger.info(f'Total number of samples: {paragraph_number}')
```

Further we log: 

1. The total amount of memory the GPU has (e.g. the case on the HEC with the nvidia v100 GPU this should be 32GB).
2. The amount used before running the script (on the HEC this should be 0GB). 
3. The amount used for loading the model.
4. The peak amount of GPU memory used for a batch.
5. The total peak amount of GPU memory used for the script. This is the amount of memory used for loading the model + the peak amount from a batch.

Knowing these statistics at a more granular level allows you to know if you can increase the batch size and by how much to make full use of the GPU. The larger the batch size the faster the processing will be. Further it shows you how much GPU memory the model requires, which will be useful to report in a paper to allow others to know what computing infrastructure they require to run your model/code. 

``` python
logger.info(f"Total GPU memory: {bytes_to_GB(gpu_info.total):.4f}GB")
logger.info(f"Amount of GPU memory used before running script: {gpu_memory_start:.4f}GB")
logger.info(f"GPU memory used for loading model: {gpu_memory_for_model:.4f}GB")

logger.info('Peak GPU memory used for processing batch '
            f'{max(gpu_memory_used_during_processing):.4f}GB')
peak_gpu_memory = gpu_memory_before_processing + max(gpu_memory_used_during_processing)
peak_gpu_memory = peak_gpu_memory - gpu_memory_start
logger.info(f'Peak GPU memory used {peak_gpu_memory:.4f}GB')
```

Lastly we report the peak amount of RAM memory required to process this script (on my small experiments with this script, I have found the RAM memory usage to remain the same no matter the batch size or GPU memory usage). Reporting the amount of RAM required will also be useful to others wanting to run your code. Further `nvmlShutdown()` shuts down/stops the tracking of the GPU memory.

``` python
# Amount of RAM being used before script. (1024**2) converts it to GB from KB
ram_memory_end = getrusage(RUSAGE_SELF).ru_maxrss / (1024**2)
logger.info(f'Peak RAM memory used {ram_memory_end:.4f}GB')
nvmlShutdown()
```

Throughout the GPU memory reporting you would have seen a call to the function below. This function converts Bytes to GigaBytes as [pynvml](https://pypi.org/project/nvidia-ml-py3/) only reports in Bytes:

``` python
def bytes_to_GB(number_bytes: int) -> int:
    return number_bytes / (1024**3)
```

## Running the code

We now show how to run this code on the HEC and your own machine (we assume you have a nvidia GPU) using the Alice in Wonderland book as the 1st argument and [./output.tsv](./output.tsv) as the 2nd argument. The code will be ran twice with two different batch sizes **50** and **300**.

### Run on the HEC

python download_stanza.py $global_scratch/stanza_models

1. Transfer this directory to your home directory on the HEC: `scp -r ../gpu_example/ username@wayland.hec.lancaster.ac.uk:./`
2. Create the conda environment with the relevant python dependencies and pre-download the Stanza model. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the conda environment at `$global_scratch/py3.8-gpu-example`. To pre-download the stanza model the install.com script runs the following `python download_stanza.py $global_scratch/stanza_models`. This downloads the stanza model to the `$global_scratch/stanza_models` directory using the [./download_stanza.py](./download_stanza.py). The reason for pre-downloading the stanza model before using the main tagging script [./gpu_stanza_tagging.py](./gpu_stanza_tagging.py) is so that we don't waste the GPU node's time on downloading the stanza model.
3. We need to switch from the cpu cluster to the gpu cluster using the `switch-gpu` command.
4. We can now run the [./gpu_stanza_tagging.py](./gpu_stanza_tagging.py) by submitting the following job `qsub gpu_stanza_tagging.com`. This will load the pre-downloaded models from the `$global_scratch/stanza_models` directory and perform the two tagging tasks (one for batch size of 50 and the other batch size of 300).
5. You should be able to view the logging/output within the generated stdout file from running `gpu_stanza_tagging.com`, in my case this is the file called `gpu-stanza-tagging.o2650`. You can view the contents of the file with the `cat` command: `cat gpu-stanza-tagging.o2650`. **Note** Stanza also logs quite a lot of information, we are only interested in the log data that came from `__main__`.
6. To switch back to the CPU cluster you can run the `switch-cpu` command.

**Note** The [./gpu_stanza_tagging.com](./gpu_stanza_tagging.com) submits a GPU job to the HEC requesting 8GB of RAM, 2 CPUs, 1 GPU, and to run for a maximum of 10 minutes. Unlike the CPU jobs you have to specify a maximum time limit, hence the importance of knowing how long your job is going to run for. If your job runs for more than 10 minutes it is automatically stopped.

### Run on your own machine

We assume that you are running either Linux, or another Linux based system (Windows [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install-win10)). With regards to Mac at the moment then do not have any nvidia GPUs in their computer/machine lineup thus making them in-compatible for this python GPU code. Further we assume you have a [compatible nvidia GPU](https://developer.nvidia.com/cuda-gpus), I would recommend only installing via conda when using the GPU as it sets up the cuda tool kit which can be difficult to do yourself.

Using conda:

1. Install the required pips: `conda env create -n gpu-example --file ./environment.yaml`
2. Activate the new conda environment `conda activate gpu-example`
3. run `bash gpu_stanza_tagging.sh ./stanza_models`, whereby the first argument (`./stanza_models`) states which directory to download the stanza model too. 
4. The logging/output should be displayed in the terminal/console you are running this script from. **Note** Stanza also logs quite a lot of information, we are only interested in the log data that came from `__main__`.
5. If you want to remove this conda environment afterwards run; `conda deactivate && conda env remove -n gpu-example`

### Comparing results

**Note** These results came from running it on the HEC.

From the results below we can see that processing with a batch size of 300 is ~31% quicker and uses ~250% more GPU memory, but uses the same amount of RAM memory. Further it shows that the model uses 1.33 GB of GPU memory to load. Lastly if you increase your batch size by 50 expect to use 0.66 GB more GPU memory. These results show that if we wanted to we can easily increase the batch size to around 2270 ( (30/0.66) * 50 ~= 2270) while only taking up around 30 GB GPU memory of which the GPUs on the HEC have 32 GB of GPU memory.

``` bash
# Processing with a batch size of 50
2021-01-17 14:21:15,873 - __main__ - INFO - Total time: 8.6445s
2021-01-17 14:21:15,874 - __main__ - INFO - Mean batch time for batch size 50: 0.4906s
2021-01-17 14:21:15,874 - __main__ - INFO - Total number of samples: 881
2021-01-17 14:21:15,874 - __main__ - INFO - Total GPU memory: 31.7485GB
2021-01-17 14:21:15,874 - __main__ - INFO - Amount of GPU memory used before running script: 0.0001GB
2021-01-17 14:21:15,876 - __main__ - INFO - GPU memory used for loading model: 1.3270GB
2021-01-17 14:21:15,876 - __main__ - INFO - Peak GPU memory used for processing batch 0.6641GB
2021-01-17 14:21:15,876 - __main__ - INFO - Peak GPU memory used 1.9911GB
2021-01-17 14:21:15,876 - __main__ - INFO - Peak RAM memory used 2.4532GB
# Processing with a batch size of 300
2021-01-17 14:21:26,839 - __main__ - INFO - Total time: 5.9519s
2021-01-17 14:21:26,841 - __main__ - INFO - Mean batch time for batch size 300: 2.0267s
2021-01-17 14:21:26,841 - __main__ - INFO - Total number of samples: 881
2021-01-17 14:21:26,841 - __main__ - INFO - Total GPU memory: 31.7485GB
2021-01-17 14:21:26,841 - __main__ - INFO - Amount of GPU memory used before running script: 0.0001GB
2021-01-17 14:21:26,841 - __main__ - INFO - GPU memory used for loading model: 1.3270GB
2021-01-17 14:21:26,841 - __main__ - INFO - Peak GPU memory used for processing batch 5.7539GB
2021-01-17 14:21:26,841 - __main__ - INFO - Peak GPU memory used 7.0809GB
2021-01-17 14:21:26,841 - __main__ - INFO - Peak RAM memory used 2.4740GB
```

#### GPU information from the HEC

The log output from the HEC also contain the following GPU information after running a job on the GPU nodes:

``` bash
+------------------------------------------------------------------------------+
| GPU ID: 1                                                                    |
+====================================+=========================================+
|-----  Execution Stats  ------------+-----------------------------------------|
| Start Time                         | Sun Jan 17 14:20:55 2021                |
| End Time                           | Sun Jan 17 14:21:27 2021                |
| Total Execution Time (sec)         | 31.56                                   |
| No. of Processes                   | 1                                       |
+-----  Performance Stats  ----------+-----------------------------------------+
| Energy Consumed (Joules)           | 0                                       |
| Power Usage (Watts)                | Avg: 56.378, Max: 56.378, Min: 56.378   |
| Max GPU Memory Used (bytes)        | 2205155328                              |
| SM Clock (MHz)                     | Avg: 1380, Max: 1380, Min: 1380         |
| Memory Clock (MHz)                 | Avg: 877, Max: 877, Min: 877            |
| SM Utilization (%)                 | Avg: 39, Max: 39, Min: 39               |
| Memory Utilization (%)             | Avg: 7, Max: 7, Min: 7                  |
| PCIe Rx Bandwidth (megabytes)      | Avg: N/A, Max: N/A, Min: N/A            |
| PCIe Tx Bandwidth (megabytes)      | Avg: N/A, Max: N/A, Min: N/A            |
+-----  Event Stats  ----------------+-----------------------------------------+
| Single Bit ECC Errors              | 0                                       |
| Double Bit ECC Errors              | 0                                       |
| PCIe Replay Warnings               | 0                                       |
| Critical XID Errors                | 0                                       |
+-----  Slowdown Stats  -------------+-----------------------------------------+
| Due to - Power (%)                 | 0                                       |
|        - Thermal (%)               | 0                                       |
|        - Reliability (%)           | Not Supported                           |
|        - Board Limit (%)           | Not Supported                           |
|        - Low Utilization (%)       | Not Supported                           |
|        - Sync Boost (%)            | 0                                       |
+--  Compute Process Utilization  ---+-----------------------------------------+
| PID                                | 457520                                  |
|     Avg SM Utilization (%)         | 16                                      |
|     Avg Memory Utilization (%)     | 5                                       |
+-----  Overall Health  -------------+-----------------------------------------+
| Overall Health                     | Healthy                                 |
+------------------------------------+-----------------------------------------+
```

This information may not be completely correct as it states the `Max GPU Memory Used (bytes) : 2205155328 ` which is ~2.2 GB, of which I know this cannot be true for the script we have just ran.

## Estimating GPU memory through CPU and RAM

In case you might be wondering if you could estimate the GPU memory usage through the amount of RAM required to run the same model only using CPU, the short answer is **no**.

To test this we created a CPU only version of the tagging example above, which can be found here [./cpu_stanza_tagging.py](./cpu_stanza_tagging.py).

### CPU example on the HEC

Here we assume you have done steps 1 and 2 from [Run on the HEC section above](#run-on-the-hec). 

1. Assuming you are on the HEC and on the CPU cluster (`switch-cpu`). Run the following script [./cpu_stanza_tagging.sh](./cpu_stanza_tagging.sh) through submitting this job: `qsub cpu_stanza_tagging.com`
2. You should be able to view the logging/output within the generated stdout file from running `cpu_stanza_tagging.com`, in my case this is the file called `cpu-stanza-tagging.o6794329`. You can view the contents of the file with the `cat` command: `cat cpu-stanza-tagging.o6794329`. **Note** Stanza also logs quite a lot of information, we are only interested in the log data that came from `__main__`.

### CPU results

From the log file shown below, we can see that the CPU version of the script used far less RAM (1.01 GB) than the GPU version (2.47 GB). Further if we added the RAM and GPU memory required for the batch size of 50 for the GPU version of the code this would come to ~4.45 GB. Thus you cannot estimate the amount of GPU memory required from RAM required to run the CPU version.

``` bash
# Batch size of 50
2021-01-17 18:52:25,059 - __main__ - INFO - Total time: 140.8209s
2021-01-17 18:52:25,059 - __main__ - INFO - Mean batch time for batch size 50: 7.9921s
2021-01-17 18:52:25,059 - __main__ - INFO - Total number of samples: 881
2021-01-17 18:52:25,059 - __main__ - INFO - RAM memory used for loading model: 0.5035GB
2021-01-17 18:52:25,059 - __main__ - INFO - Peak RAM memory used 1.0178GB
# Batch size of 300
2021-01-17 18:54:20,086 - __main__ - INFO - Total time: 113.0176s
2021-01-17 18:54:20,086 - __main__ - INFO - Mean batch time for batch size 300: 38.4850s
2021-01-17 18:54:20,086 - __main__ - INFO - Total number of samples: 881
2021-01-17 18:54:20,086 - __main__ - INFO - RAM memory used for loading model: 0.5057GB
2021-01-17 18:54:20,086 - __main__ - INFO - Peak RAM memory used 3.8383GB
```