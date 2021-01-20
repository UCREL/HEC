# Multiple similar jobs example

**Note** before reading this I would recommend reading this [HEC guide as it explains it a lot better.](https://answers.lancaster.ac.uk/display/ISS/Submitting+multiple+similar+jobs+on+the+HEC) This is an extended NLP example of that guide on creating an `array job`. In essence an `array job` is a single job that contains multiple tasks whereby each task is run on a different node in the HEC.

In this example we are going to tag all of the files/books in the directory [./files](./files) with Named Entities using the [**Stanza** Named Entity Recognizer (NER)](https://stanfordnlp.github.io/stanza/ner.html).

1. [./files/files_1](./files/files_1) directory contains 2 books authored by Jane Austen, downloaded from [Project Gutenberg](https://www.gutenberg.org/ebooks/author/68)
2. [./files/files_2](./files/files_2) directory contains 2 books authored by Arthur Conan Doyle, downloaded from [Project Gutenberg](https://www.gutenberg.org/ebooks/author/69)


We are going to use a similar tagging python script as the [single job example](../single_job), [./tagging.py](./tagging.py), which takes four arguments:

1. A file which will be split into paragraphs of text, whereby the paragraphs will be batched and tagged using the Stanza Named Entity Recognizer (NER).
2. A file to store the Named Entities found through tagging the file found in the first argument. This file will be `TSV` formatted with the following fields:

|paragraph_number|entity text|entity label|start character offset|end character offset|
|-|-|-|-|-|

3. The batch size. This states the number of paragraphs that the NER model will process at once. The larger the batch size the more RAM required but the faster the model will process the whole text.
4. A file path to a directory that will store the Stanza pre-trained models that the script downloads.

There are two ways we could create a submission script to the HEC (in all of these examples we assume the Stanza pre-trained models are stored at `$global_storage/stanza_models`):

1. We use one node on the HEC and get that one node to process all of the files in the file folder ([./files](./files)), in essence this is the approach used in the [single job example](../single_job). The code below comes from the [./single_tagging.com](./single_tagging.com) submission script.

``` bash
source /etc/profile
module add anaconda3/wmlce
source activate $HOME/py3.8-multiple-similar-job

mkdir -p ./output_files
for folder_number in `seq 1 2`; do
    mkdir -p ./output_files/files_$folder_number
    for file_number in `seq 0 1`; do
        python tagging.py ./files/files_$folder_number/$file_number.txt ./output_files/files_$folder_number/$file_number.tsv 50 $global_storage/stanza_models
    done
done
```

2. We can submit each file folder to a different node on the HEC thus meaning that while one node is tagging one folder of files another is processing the other folder of files. This therefore makes the processing, in this case, twice as fast as we have two nodes processing the files rather than one. *If the HEC does not have enough free nodes it will queue the second folder of files until a node is free.* The code below comes from the [./tagging.com](./tagging.com) submission script.
``` bash
#$ -t 1-2:1

source /etc/profile
module add anaconda3/wmlce
source activate $HOME/py3.8-multiple-similar-job

mkdir -p ./output_files
mkdir -p ./output_files/files_$SGE_TASK_ID

for file_number in `seq 0 1`; do
    python tagging.py ./files/files_$SGE_TASK_ID/$file_number.txt ./output_files/files_$SGE_TASK_ID/$file_number.tsv 50 $global_storage/stanza_models
done
```

In this bash script we are using 2 nodes, or more correctly we are submitting two tasks to the HEC in the hope of having two nodes at the same time. These two tasks are stated through the `#$ -t 1-2:1` whereby it states the tasks are represented as task 1 and 2 (1-2:1 means create a sequence of tasks starting at 1 ending at 2 with an increment of 1). These task indexes/ids are represented through the environment variable `$SGE_TASK_ID`. We then create an `output_files` folder and within that folder each task will have their own output folder `./output_files/files_$SGE_TASK_ID`. Lastly each task will then tag the files in their representative task index folder and output to their own output folder. This is the reason why the files directory where named `./files/file_1` and `./files/file_2` as it makes setting up this way of processing easier. It is also the reason why the book/files are named `0-1`.txt as it makes processing them easier as we can set up the processing as a for loop in the script above.

In this example we are going to use the second way to process this data as it is the quicker way of tagging the data.

**You might be wondering why we do not use a node/task per file/book**, the reason for this is that tagging one book/file is a relatively quick task (less than 5 minutes) and it states on the HEC guide that quick/short jobs should be avoided as it is an inefficient use of the HEC. Thus it is better to batch the processing of these books/files hence why each node/task is processing 2 books each rather than just one. In reality depending on how many books/files you need to process you would have a batch of more than 2 books, but I wanted to keep this example as short in processing time as possible for environmental and learning reasons. For more details on this see [the managing short jobs section on the HEC guide.](https://answers.lancaster.ac.uk/display/ISS/Submitting+multiple+similar+jobs+on+the+HEC)

**Note** that the `#$ -t 1-2:1` task index sequence has to start at an index equal to or greater than 1. It cannot start at index 0. For example `#$ -t 0-4:2` is not valid as the index sequence would start at 0.

The rest of this tutorial is laid out as follows:

1. Explain any differences to the standard installation process.
2. How to run the script on the HEC.

## Installation

Before running this script we will need to crate a custom Conda environment so that we have a Python environment that has stanza installed. For details on creating your own custom Conda/Python environment see the [installation tutorial](../../install_packages). For this task we also need the Stanza English pre-trained NER model, to do so we download this in the installation submission script, [./install.com](./install.com), on line 17-18:

``` bash
source activate $HOME/py3.8-multiple-similar-job
python ./download_stanza.py $global_storage/stanza_models
```

The first line activates our new Conda environment and the second line runs the [./download_stanza.py](./download_stanza.py) python script whereby the first argument states the directory to save the Stanza models too. In this case we save them to the `$global_storage/stanza_models` directory.

## Run on the HEC

**Note**: If you do not want to create/save the Conda environment to your `$HOME` storage space (maybe due to space/storage restrictions), you could instead save it to the larger `$global_storage` space. This can be done simply by changing `$HOME` to `$global_storage`.

1. Transfer this directory to your home directory on the HEC: `scp -r ../multiple_similar_jobs/ username@wayland.hec.lancaster.ac.uk:./`
2. Login to the HEC `ssh username@wayland.hec.lancaster.ac.uk` and go to the single job directory: `cd multiple_similar_jobs` 
3. Create the conda environment with the relevant python dependencies and download the Stanza English NER model. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the Conda environment at `$HOME/py3.8-multiple-similar-job`. This may take some time e.g. 5 minutes, to monitor the progress of the job use `qstat`, see the [HEC monitoring page for more details on the command.](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC)
4. We can now run the [./tagging.py](./tagging.py) script by submitting the following job `qsub tagging.com`. The main points of the [./tagging.com](./tagging.com) were explained above. 
5. If you run the `qstat` command you should see that you have two tasks submitted e.g.:
``` bash
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID 
-----------------------------------------------------------------------------------------------------------------
6841142 0.50000 multiple-s moorea       r     01/20/2021 08:02:48 serial@comp16-21.private.dns.z     1 1
6841142 0.50000 multiple-s moorea       r     01/20/2021 08:02:48 serial@comp16-16.private.dns.z     1 2
```

At the start of the job you may see the following from qstat:

``` bash
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID 
-----------------------------------------------------------------------------------------------------------------
6841142 0.00000 multiple-s moorea       qw    01/20/2021 08:02:44                                    1 1,2
```
But the HEC knows it is an array job as it shows tasks indexes in `ja-task-id` and eventually it will be splits into two tasks.

6. After the tagging script has finished running (takes around 28 minutes to run the longest task see step 7 below), the Named Entities found in each book/file will be outputted into the `./output_files` folder. Additionally as we are running multiple tasks each task has its own standard error and output file e.g. in my case the standard output file for task 1 was `multiple-similar-job.o6841142.1` and for task 2 was `multiple-similar-job.o6841142.2`. The files are named through `job name`.`job ID`.`task ID`.
7. If you would like to know some run time statistics, like total time each task took you can use the `qacct` command ([see the HEC pages for more details on this command](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC)) e.g. for me to get these statistics for the first task I would run `qacct -j 6841278 -t 1` and for the second task `qacct -j 6841278 -t 2`. The longest run time `ru_wallclock` was task 1 with a total run time of `1657` seconds which is around 28 minutes. You may notice that it states the max memory/RAM used (`maxvmem` in the report `qacct` creates) to be close to 1 GB, from my experience it still requires a memory allocations of 3 GB as it would appear that parts of the Stanza model require large amounts of memory for a very short period of time which the memory monitor appears not to pick up on.
7. **Optional**: As you have limited space in your home directory you may want to delete the Conda environment created from this job. To do so `cd $HOME` and `rm -r py3.8-multiple-similar-job` or `rm -r $HOME/py3.8-multiple-similar-job`
8. **Optional**: As you have 100 GB space in your `$global_storage` directory you may want to delete the downloaded stanza models. To do so `cd $global_storage` and `rm -r stanza_models`
8. **Optional**: You may want to transfer the results of extracting the Named Entities to your home/local computer, to do so open a terminal on your home computer, change to the directory you want the Named Entities folder to be saved too and `scp -r username@wayland.hec.lancaster.ac.uk:./multiple_similar_jobs/output_files .` 

Just as a comparison I have ran the [./single_tagging.com](./single_tagging.com) script on the HEC which only uses one node, and it takes 49 minutes compared to 28 minutes that the [./tagging.com](./tagging.com). This shows the benefit of making using of multiple nodes on the HEC compared to just using one node.

