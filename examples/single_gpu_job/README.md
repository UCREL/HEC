# Single GPU job example

This example demonstrates how to submit a job to one of the HEC's GPU nodes, whereby the example is using SpaCy to tag Alice in Wonderland for Named Entities where the SpaCy model will use the GPU. The example used is similar to the CPU version of this example [../single_job](../single_job). The Alice in Wonderland text can be found at [./alice-in-wonderland.txt](./alice-in-wonderland.txt) and the script that will be used to tag it is [./tagging.py](./tagging.py), a python script which takes 4 arguments:

1. A file which will be split into paragraphs of text, whereby the paragraphs will be batched and tagged using a SpaCy Named Entity Recognizer (NER).
2. A file to store the Named Entities found through tagging the file found in the first argument. This file will be `TSV` formatted with the following fields:

|paragraph_number|entity text|entity label|start character offset|end character offset|
|-|-|-|-|-|

3. The batch size. This states the number of paragraphs that the NER model will process at once. The larger the batch size the more RAM required but the faster the model will process the whole text.
4. `--gpu` flag. This states whether SpaCy should use the GPU or not. (This argument did not exist in the [../single_job](../single_job) example for CPU).

Given this script we can process the Alice in Wonderland text and extract all Named Entities by simply running the Python script as follows:

``` bash
python tagging.py ./alice-in-wonderland.txt ./output.tsv 50 --gpu
```

Whereby the Named Entities will be saved to `./output.tsv`.

The rest of this tutorial is laid out as follows:

1. Main difference between CPU and GPU job
2. Explain any differences to the standard installation process.
2. How to run the script on the HEC.

## Main difference between CPU and GPU job

Below are the HEC submission settings. [For a detailed guide on the HEC GPU submission settings see the HEC GPU page](https://answers.lancaster.ac.uk/display/ISS/Using+GPUs+on+the+HEC). In our GPU submission script, [./tagging.com](./tagging.com) we have the following settings:

``` bash
#$ -q short
#$ -l ngpus=1
#$ -l ncpus=2
#$ -l h_vmem=8G
#$ -l h_rt=00:05:00
```

* `#$ -q short` -- states we want to use the `short` GPU queue. Remember from the [main README Computational resources section](../../README.md#computational-resources) the GPU nodes have 3 queues `short`, `medium`, and `long`. Each of those queues allow for varying amounts of computational time 12 hours, 48 hours, and 7 days respectively. As this job should take minutes to run we only need the `short` queue. For further details on [GPU queues see the HEC documentation](https://answers.lancaster.ac.uk/display/ISS/Using+GPUs+on+the+HEC).
* `#$ -l ngpus=1` -- number of GPUs on a node we would like to use, in this case it is 1. The maximum this can be at the moment is 3 as the most GPUs per node currently is 3.
* `#$ -l ncpus=2` -- number of CPUs on a node we would like to use, in this case it is 2. The maximum this can be at the moment is 32.
* `#$ -l h_vmem=8G` -- amount of RAM/memory on a node we would like to use, in this case it is 8 GB. The maximum this can be at the moment is 192 GB.
* `#$ -l h_rt=00:05:00` -- **how long the job will run for**, in this case it is 5 minutes. The maximum this can be, as it is submitted to the `short` queue, is 12 hours e.g. 12:00:00. Like a lot of these settings the more you request the longer you may have to wait for your job to be submitted. **NOTE** if your job runs longer than the time you have specified the job will be automatically terminated.

Another detail is that when you want to submit a GPU job you need to switch to the GPU cluster on the terminal through the command:

``` bash
switch-gpu
```

To go back to the CPU cluster:

``` bash
switch-cpu
```

## Installation

Before running this script we will need to create a custom Conda environment so that we have a Python environment that has SpaCy installed. For details on creating your own custom Conda/Python environment see the [installation tutorial](../../install_packages). For this task we also need the SpaCy English pre-trained NER model, to do so we download this in the installation submission script, [./install.com](./install.com), on line 20:

``` bash
python -m spacy download en_core_web_sm
```

Use the SpaCy module to download the small English pre-trained models. These SpaCy models are saved by default within the Conda environment as they are a Python pip package.

**Note** when using SpaCy in GPU mode it requires the `cudatoolkit` installed hence why in the [./environment.yaml](./environment.yaml) file the `cudatoolkit=10.2` package is specified.

## Run on the HEC

1. Transfer this directory to your home directory on the HEC: `scp -r ../single_gpu_job/ username@wayland.hec.lancaster.ac.uk:./`
2. Login to the HEC `ssh username@wayland.hec.lancaster.ac.uk` and go to the single job directory: `cd single_gpu_job` 
3. Create the Conda environment with the relevant python dependencies and download the SpaCy English model. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the Conda environment at `$global_storage/conda_environments/py3.8-single-job`. This may take some time e.g. 1-5 minutes, to monitor the progress of the job use `qstat`, see the [HEC monitoring page for more details on the command.](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC)
4. Switch to the GPU cluster: `switch-gpu`
5. We can now run the [./tagging.py](./tagging.py) script by submitting the following job `qsub tagging.com`
6. We no longer need to use the GPU cluster so we can if we want switch back to the CPU cluster: `switch-cpu`
7. After the tagging script has finished running, the Named Entities found in the text will be outputted into the `output.tsv` file.
8. We should be able to see how long it took to process (this does not include the time to load the model) by outputting the stdout file e.g. in my case this would be: `cat single-gpu-job.o2938` which states it took: `Total processing time: 12.7449s`. Further it shows that Alice in wonderland has `881` paragraphs which results in `18` batches.
9. **Optional**: As you have limited space in your storage directory you may want to delete the Conda environment created from this job. To do so `rm -r $global_storage/conda_environments/py3.8-single-job`. Further as we cached the Conda packages you may want to clean the Conda cache directory, to do so follow the directions at [../../install_packages/README.md#Conda and Pip cache management](../../install_packages/README.md#conda-and-pip-cache-management).
10. **Optional**: You may want to transfer the results of extracting the Named Entities to your home/local computer, to do so open a terminal on your home computer, change to the directory you want the Named Entities file to be saved too and `scp username@wayland.hec.lancaster.ac.uk:./single_gpu_job/output.tsv .` 

We also ran this script but without GPU (no `--gpu` flag) on a CPU node by running the python script as follows:

``` bash
python tagging.py ./alice-in-wonderland.txt ./output.tsv 50
```

The full CPU version of the submission script can be found at [./cpu_tagging.com](./cpu_tagging.com), we found that the CPU version is much quicker 1.8 seconds compared to the GPU 12 seconds. The GPU is best suited to models that have more parameters, the SpaCy small model that we used here does not have many parameters I believe, if you use the medium or large model you would probably get more gains with the GPU compared to CPU. Further we only used a small batch size for both CPU and GPU, when using a batch size of 1000 the CPU and GPU ran in `1.1079` and `0.6495` seconds respectively (for CPU tagging as we are using a larger batch size we need to allocate more memory so I used 8 GB by putting `#$ -l h_vmem=8G` in the [./cpu_tagging.com](./cpu_tagging.com) script).

For more details on amount of RAM and GPU memory that you should request for see the [Hints and Tools for monitoring your **Python** jobs section in the main README.](../../README.md#hints-and-tools-for-monitoring-your-python-jobs)

