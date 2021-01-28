# Multiple similar GPU jobs example

**Note** I would recommend reading the [../single_gpu_job](../single_gpu_job) example to understand running a GPU job and reading the [../multiple_similar_jobs](../multiple_similar_jobs) to understand running what the HEC describe as an [array job](https://answers.lancaster.ac.uk/display/ISS/Submitting+multiple+similar+jobs+on+the+HEC). In this example we are combining these two examples by running a GPU array job.

In this example we are going to tag all of the files/books in the directory [./files](./files) with Named Entities using the [**Stanza** Named Entity Recognizer (NER)](https://stanfordnlp.github.io/stanza/ner.html).

1. [./files/files_1](./files/files_1) directory contains 2 books authored by Jane Austen, downloaded from [Project Gutenberg](https://www.gutenberg.org/ebooks/author/68)
2. [./files/files_2](./files/files_2) directory contains 2 books authored by Arthur Conan Doyle, downloaded from [Project Gutenberg](https://www.gutenberg.org/ebooks/author/69)


We are going to use a similar tagging python script as the other tagging examples, [./tagging.py](./tagging.py), which takes four arguments:

1. A file which will be split into paragraphs of text, whereby the paragraphs will be batched and tagged using the Stanza Named Entity Recognizer (NER).
2. A file to store the Named Entities found through tagging the file found in the first argument. This file will be `TSV` formatted with the following fields:

|paragraph_number|entity text|entity label|start character offset|end character offset|
|-|-|-|-|-|

3. The batch size. This states the number of paragraphs that the NER model will process at once. The larger the batch size the more GPU memory required but the faster the model will process the whole text ([see the GPU example in the Hints and Tools for monitoring your Python jobs section](../hints_tools_for_python_monitoring/gpu_example) for more details).
4. A file path to a directory that will store the Stanza pre-trained models that the script downloads.

Using this [./tagging.py](./tagging.py) python script we create an array job submission script, [./tagging.com](./tagging.com). This script will submit two tasks one that will process all of the files in directory [./files/files_1](./files/files_1) and the other to process all files in directory [./files/files_2](./files/files_2). Thus if the HEC has the resources available it will assign two GPU nodes at the same time, one to process [./files/files_1](./files/files_1) and the other to process [./files/files_2](./files/files_2).

**NOTE on `h_rt` setting in the submission script for GPU nodes:** The requested submission time flag/setting `#$ -l h_rt=` is per task. So in our case as we have two tasks, for tagging two directories, the time specified is per directory. Therefore if it takes approximately 2 minutes to tag a directory then we can set `#$ -l h_rt=` = `00:02:00`. In our case we actually set this to five minutes just in case and as it is an example we don't want it to fail. You can find out if your job was terminated due to running out of submission time through the `qacct` command, if the report from the `qacct` command has an exit status like `exit_status 137 (Killed)` then it ran out of time. A good exit status is `0`.

The rest of this tutorial is laid out as follows:

1. Explain any differences to the standard installation process.
2. How to run the script on the HEC.

## Installation

Before running this script we will need to crate a custom Conda environment so that we have a Python environment that has Stanza installed. For details on creating your own custom Conda/Python environment see the [installation tutorial](../../install_packages). As we are using the GPU we need the GPU version of [PyTorch](https://pytorch.org/) installed rather than the CPU version which will come with Stanza. Therefore in the [./environment.yaml](./environment.yaml) we have stated that we want PyTorch and the `cudatoolkit` packages installed.

For this task we also need the Stanza English pre-trained NER model, to do so we download this in the installation submission script, [./install.com](./install.com), on line 20, whereby the stanza models will be saved/downloaded to the directory `$global_storage/stanza_models` using the [./download_stanza.py](./download_stanza.py) python script:

``` bash
python ./download_stanza.py $global_storage/stanza_models
```

## Run on the HEC

1. Transfer this directory to your home directory on the HEC: `scp -r ../multiple_similar_gpu_jobs/ username@wayland.hec.lancaster.ac.uk:./`
2. Login to the HEC `ssh username@wayland.hec.lancaster.ac.uk` and go to the directory: `cd multiple_similar_gpu_jobs` 
3. Create the Conda environment with the relevant python dependencies and download the Stanza English NER model. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the Conda environment at `$global_storage/conda_environments/py3.8-multiple-similar-gpu-job`. This may take some time e.g. 10 minutes or so, to monitor the progress of the job use `qstat`, see the [HEC monitoring page for more details on the command.](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC)
4. Switch to the GPU cluster: `switch-gpu`
5. We can now run the [./tagging.py](./tagging.py) script by submitting the following job `qsub tagging.com`. If you run the `qstat` command you should see that you have two tasks submitted e.g.:

``` bash
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID 
-----------------------------------------------------------------------------------------------------------------
   2952 1.05000 multiple-g moorea       r     01/28/2021 12:21:59 gpu@gpu01.private.dns.zone         1 1
   2952 0.80000 multiple-g moorea       r     01/28/2021 12:21:59 gpu@gpu02.private.dns.zone         1 2
```

6. After the tagging script has finished running (takes around 1-2 minutes to run), the Named Entities found in each book/file will be outputted into the `./output_files` folder. Additionally as we are running multiple tasks each task has its own standard error and output file e.g. in my case the standard output file for task 1 was `multiple-gpu-job.o2952.1` and for task 2 was `multiple-gpu-job.o2952.2`. The files are named through `job name`.`job ID`.`task ID`.
7. If you would like to know some run time statistics, like total time each task took you can use the `qacct` command ([see the HEC pages for more details on this command](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC)) e.g. for me to get these statistics for the first task I would run `qacct -j 2952 -t 1` and for the second task `qacct -j 2952 -t 2`. The longest run time `ru_wallclock` was task 1 with a total run time of `77` seconds which is around 1-2 minutes. **NOTE** You have to be on the correct cluster e.g. if you do `qacct` for a CPU job you have to be on the CPU cluster `switch-cpu` and if you ran a GPU job you have to be on the GPU cluster `switch-gpu`
8. **Optional** As we have finished with the GPU cluster we can go back to the CPU cluster: `switch-cpu`
9. **Optional**: As you have limited space in your `$global_storage` directory you may want to delete the Conda environment created from this job. To do so `rm -r $global_storage/conda_environments/py3.8-multiple-similar-gpu-job`. Further as we cached the Conda packages you may want to clean the Conda cache directory, to do so follow the directions at [../../install_packages/README.md#Conda and Pip cache management](../../install_packages/README.md#conda-and-pip-cache-management).
10. **Optional**: As you have 100 GB space in your `$global_storage` directory you may want to delete the downloaded stanza models. To do so `rm -r $global_storage/stanza_models`
11. **Optional**: You may want to transfer the results of extracting the Named Entities to your home/local computer, to do so open a terminal on your home computer, change to the directory you want the Named Entities folder to be saved too and `scp -r username@wayland.hec.lancaster.ac.uk:./multiple_similar_gpu_jobs/output_files .` 

For more details on amount of RAM and GPU memory that you should request for see the [Hints and Tools for monitoring your **Python** jobs section in the main README.](../../README.md#hints-and-tools-for-monitoring-your-python-jobs)

**Note** how much quicker it was to run Stanza on the GPU compared to the [CPU example](../multiple_similar_jobs). The GPU took using two nodes 1-2 minutes, compared to the CPU using two nodes which took 28 minutes.
