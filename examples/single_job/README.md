# Single job example

In this example we show how you can submit a job to the HEC which only uses one single CPU on a node on the HEC. This is all detailed in the job submission script (typically these use the `.com` file extension), [./tagging.com](./tagging.com). The explanation of the parameters of that script is best explained on the HEC documentation within the `batch jobs` section under sub-section `example of a batch job script` found [here](https://answers.lancaster.ac.uk/display/ISS/Submitting+jobs+on+the+HEC). This tagging script uses about 120 MB of memory hence why we do not need to specify the `#$ -l h_vmem` flag/parameter in [./tagging.com](./tagging.com).

This example will show how to tag the Alice in Wonderland text, which can be found at [./alice-in-wonderland.txt](./alice-in-wonderland.txt), with Named Entities using the SpaCy Named Entity Recognizer (NER). To do so we can use the [./tagging.py](./tagging.py) python script which takes 3 arguments:

1. A file which will be split into paragraphs of text, whereby the paragraphs will be batched and tagged using a SpaCy Named Entity Recognizer (NER).
2. A file to store the Named Entities found through tagging the file found in the first argument. This file will be `TSV` formatted with the following fields:

|paragraph_number|entity text|entity label|start character offset|end character offset|
|-|-|-|-|-|

3. The batch size. This states the number of paragraphs that the NER model will process at once. The larger the batch size the more RAM required but the faster the model will process the whole text.

Given this script we can process the Alice in Wonderland text and extract all Named Entities by simply running the Python script as follows:

```
python tagging.py ./alice-in-wonderland.txt ./output.tsv 50
```

Whereby the Named Entities will be saved to `./output.tsv`. To run this script on the HEC we will have to install the relevant Python dependencies, which is explained next. 

The rest of this tutorial is laid out as follows:

1. Explain any differences to the standard installation process.
2. How to run the script on the HEC.

## Installation

Before running this script we will need to crate a custom Conda environment so that we have a Python environment that has SpaCy installed. For details on creating your own custom Conda/Python environment see the [installation tutorial](../../install_packages/README.md). For this task we also need the SpaCy English pre-trained NER model, to do so we download this in the installation submission script, [./install.com](./install.com), on line 17-18:

``` bash
source activate $HOME/py3.8-single-job
python -m spacy download en_core_web_sm
```

The first line activates our new Conda environment and the second line uses the SpaCy module to download the small English pre-trained models. These SpaCy models are saved by default within the Conda environment as they are a Python pip package, thus when you delete the Conda environment you will delete these downloaded English pre-trained models.

## Run on the HEC

**Note**: If you do not want to create/save the Conda environment to your `$HOME` storage space (maybe due to space/storage restrictions), you could instead save it to the larger `$global_storage` space. This can be done simply by changing `$HOME` to `$global_storage`.

1. Transfer this directory to your home directory on the HEC: `scp -r ../single_job/ username@wayland.hec.lancaster.ac.uk:./`
2. Login to the HEC `ssh username@wayland.hec.lancaster.ac.uk` and go to the single job directory: `cd single_job` 
3. Create the conda environment with the relevant python dependencies and download the SpaCy English model. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the Conda environment at `$HOME/py3.8-single-job`. This may take some time e.g. 5 minutes, to monitor the progress of the job use `qstat`, see the [HEC monitoring page for more details on the command.](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC)
4. We can now run the [./tagging.py](./tagging.py) script by submitting the following job `qsub tagging.com`

The [./tagging.com](./tagging.com) submission script first adds the `anaconda3/wmlce` module so that we have Conda installed on the compute node we are using, then activates our custom Conda/Python environment `source activate $HOME/py3.8-single-job`, and lastly runs the [./tagging.py](./tagging.py) script `python tagging.py ./alice-in-wonderland.txt ./output.tsv 50`

``` bash
source /etc/profile
module add anaconda3/wmlce
source activate $HOME/py3.8-single-job

python tagging.py ./alice-in-wonderland.txt ./output.tsv 50
```
5. After the tagging script has finished running, the Named Entities found in the text will be outputted into the `output.tsv` file. 
6. **Optional**: As you have limited space in your home directory you may want to delete the Conda environment created from this job. To do so `cd $HOME` and `rm -r py3.8-single-job` or `rm -r $HOME/py3.8-single-job`
7. **Optional**: You may want to transfer the results of extracting the Named Entities to your home/local computer, to do so open a terminal on your home computer, change to the directory you want the Named Entities file to be saved too and `scp username@wayland.hec.lancaster.ac.uk:./single_job/output.tsv .` 

