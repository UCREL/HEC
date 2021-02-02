# Custom software installation

Here we assume that you have read the [file storage introduction](../README.md#file-storage) from the main [README](../README.md). Also that you have read the [Job submission/monitoring](../README.md#job-submissionmonitoring) section from the main README.

In this tutorial we show how you can install your own Python environment given the `anaconda3/wmlce` module available within the module list on the HEC. The `anaconda3/wmlce` module is chosen here as the base module as it:

* Contains the most up-to-date version of `Conda` out of all of the `anaconda3` modules available on the HEC. For reference as of writing this it runs Conda version 4.8.2 which came out on the 24/01/2020.

## Table of contents

1. [How Conda creates an environment](#how-conda-creates-an-environment)
2. [Conda environment file](#conda-environment-file)
3. [Description of the install script](#description-of-the-install-script)
    1. [Example](#example)
4. [Conda and Pip cache management](#conda-and-pip-cache-management)
    1. [Pip cache removal](#pip-cache-removal)
5. [Updating existing Conda Environments](#updating-existing-conda-environments)

## How Conda creates an environment

When you are creating your own Python environment with Conda you are in affect creating an area on disk space (from now on called the **Python environment folder**) that contains executable programs, which in this case are mainly the Python program and all of it's dependencies e.g. pip and system dependencies. In general we recommend saving this to the `Storage` space as some environment folders can be large e.g. 5.5GB. Therefore if you save it to your `Home` it will quickly fill your 10GB of space, and if you save it to `Scratch` it could be removed that night as some of the installation files last modified time could be much older than 1 month.

## Conda environment file

The Python environment that Conda creates is determined by the dependencies specified within an `environment` YAML file, details of how to create one can be found on the [Conda manual page.](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually)

We recommend that if you have any pip packages to install that are not available as Conda packages to install the pips as a separate command (this is shown/explained in more detail in the [Description of the install script](#description-of-the-install-script) section below) e.g.

``` bash
source activate $conda_save_location # activate your newly created Conda environment
pip install -r conda-requirements.txt
```

If you do add the pip package installation process to the `environment` YAML file, [as shown in the Conda guide](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually), we found this can take up to 9 times slower e.g. with the installation process in the [./example/example_install.com](./example/example_install.com) it could take 35-45 minutes to install instead of 5 minutes.

## Description of the install script

**Note** instead of creating a batch job you can install the Conda/Python environment using the Login node, but here we show how to install it via a batch job.

The best way to create your own Python environment on the HEC is by making it a batch job in itself, for a detailed overview on how to submit jobs to the HEC see this [guide](https://answers.lancaster.ac.uk/display/ISS/Submitting+jobs+on+the+HEC). The general outline for the batch job can be seen in the [./install.com](./install.com) script whereby line 15 needs updating with where you want to save on disk the Python environment folder. 

The other lines of note are lines 10-12:

``` bash
export CONDA_ENVS_PATH=$global_storage/conda/envs
export CONDA_PKGS_DIRS=$global_storage/conda/pkgs
export PIP_CACHE_DIR=$global_storage/conda/pip
```

This specifies where Conda and Pip will save it cache files too. This will makes installation a lot quicker if you install multiple different Conda environments. However this comes at the cost that this `$global_storage/conda` directory can get fairly large e.g. GBs of space. See the [Conda and Pip cache management section to manage the size of this directory.](#conda-and-pip-cache-management)

Line 22 creates the Conda environment at `$conda_save_location` with the conda packages specified at `./environment.yaml` installed (the `command time` allows us to time this command, this is not needed, but useful to know.):

``` bash
command time -v conda-env create -p $conda_save_location --file ./environment.yaml
```

Lines 24-28 will activate the newly created Conda environment and install the pip packages specified in the `conda-requirements.txt` file. If the newly created Conda environment could not be activated then it will run the `echo` command/message. 

``` bash
if source activate $conda_save_location; then
    command time -v pip install -r conda-requirements.txt
else
    echo "Could not activate the conda environment at $conda_save_location"
fi
```

You may have noticed that this script runs on a single core CPU node (serial queue) with 4GB of RAM. This was chosen as the task of installation is not computationally expensive but does require some memory/RAM for the installation process to be successful. The name of the job is `conda-local` this can be changed, if wanted to, to whatever you want it to be:

``` bash
#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-local
```

### Example

In this example we show how to create a custom Python environment whereby it will have the following:

1. Python version 3.8
2. [PyTorch](https://pytorch.org/) latest version for GPU running CUDA tool kit version 10.2
3. [Joey NMT](https://github.com/joeynmt/joeynmt) version 1.0

The YAML environment file ([./example/environment.yaml](./example/environment.yaml)) can seen below:

``` yaml
channels:
  - pytorch
  - defaults
dependencies:
  - python=3.8
  - pip
  - pytorch
  - cudatoolkit=10.2
```

In the YAML environment file are all of the Conda packages required. `conda` packages and are installed from the `conda` packages found in the specified `conda channels`. As you can see we have two `channels` of which the order they are specified does determine priority of which in this case the `pytorch` channel takes priority over `defaults` the reason for this is due to `pytorch conda` dependency being in both channels and we want the one from the `pytorch` channel over the `default` channel.

As [Joey NMT](https://github.com/joeynmt/joeynmt) is only available as a Pip package we will install this through `pip` and the requirements file can be seen at [./example/conda-requirements.txt](./example/conda-requirements.txt) and below:

``` txt
joeynmt==1.0.0
```

To create this Python environment and save it to `$global_storage/py3.8-gpu-joeynmt` perform the following steps:

1. Copy the `./example` directory to your `Home` space: `scp -r example/ username@wayland.hec.lancaster.ac.uk:./`. `./` on a remote server is short hand for your home directory.
2. Login to the HEC: `ssh username@wayland.hec.lancaster.ac.uk`
3. Go to the example folder: `cd example`
4. Run the job: `qsub example_install.com`
5. Wait some time, mine took 10 minutes to run (this can be as quick as 3 minutes), to monitor the job you can use the [`qstat` command](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC). Sometimes you may have to wait some time before the job starts if the HEC is busy.
6. You can find how long it took to run by `cat` the error file, in my case this was `cat conda-local.e6170308`. This error file should have two times ("Elapsed (wall clock) time") as we have two `time` commands, the first for Conda package installation and the second for Pip package installation.
7. To check if it has successfully installed everything you can check the stdout file, in my case this was `cat conda-local.o6170308`.
8. To test if everything has worked you should see the directory `py3.8-gpu-joeynmt` in `$global_storage` e.g. `ls $global_storage`. Additionally if you run `module add anaconda3/wmlce` then `source activate $global_storage/py3.8-gpu-joeynmt` then `python --version` should be version 3.8 and you should be able to run without error the following `python -c "import joeynmt; print(joeynmt)"`
9. Run `source deactivate`

The `source activate $global_storage/py3.8-gpu-joeynmt` tells conda that you want to use the custom Conda environment at `$global_storage/py3.8-gpu-joeynmt`. `source deactivate` tells conda to stop using that custom environment.

Once you have finished with this custom python environnement it can be easily removed by:

``` bash
rm -r $global_storage/py3.8-gpu-joeynmt
``` 

This can take a bit of time to complete e.g. a minute or two. Therefore I have created a batch processing script which will submit a serial job to the HEC to remove a directory, where the directory to be removed is the first argument to this [./remove_directory.sh](./remove_directory.sh) shell script. Example usage to remove the `$global_storage/py3.8-gpu-joeynmt` directory is:

**NOTE: the backslash/escape on the dollar sign (\$)**
``` bash
bash remove_directory.sh \$global_storage/py3.8-gpu-joeynmt
``` 

The remove_directory.sh script is quite simple it creates a file `./removal.com` that has the submission code to remove the given directory. This `./removal.com` file is submitted through `qsub` and then removed. Code shown below:

``` bash
echo -e "#$ -S /bin/bash\n#$ -q serial\n#$ -N conda-removal\nsource /etc/profile\nrm -r $1" > ./removal.com
qsub ./removal.com
rm ./removal.com
```

## Conda and Pip cache management

As stated earlier caching Conda and Pip files makes installing new Conda environments that share similar/same Conda and Pip packages much faster to install. However they can take up GBs of space. In this section we assume that the Conda and Pip files are cached to the following directory: `$global_storage/conda`. To determine how much space the cache is taking up you can run: `du -csh $global_storage/conda`. To know how much of this is taken up by Pip only packages, not Conda, you can run `du -csh $global_storage/conda/pip`.

**NOTE** The conda cache shares files with conda environments therefore if you remove conda cache manually e.g. `rm -r $global_storage/conda` then any current conda environments you have installed with this cache are unlikely to work. This is why the `conda clean` tool needs to be used.

If you find that the Conda cache to be too full, you can remove parts of the cache that Conda knows is not being used by running the following [./conda_clean.com](./conda_clean.com) submission script:

``` bash
#$ -S /bin/bash
#$ -q serial
#$ -N conda-cache-removal

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$global_storage/conda/envs
export CONDA_PKGS_DIRS=$global_storage/conda/pkgs

conda clean -y -a
```

The submission script uses `conda cache`. If you use a difference Conda cache directory then lines 8 and 9 need to be changed.

After running this script through `qsub ./conda_clean.com` you may find the cache to be the same size or little change. This could be due to all of the cache files still being using by your existing Conda environment if this is the case then the only way to clean the cache further is by removal of those conda environments that you are not using.

### Pip cache removal

Pip on the other hand caches files but does not share them with conda environments, but rather copies the files thus to clean the Pip cache you can just run `rm -r $global_storage/conda/pip`. This can also be run as a submission script e.g. the [./remove_pip_cache.com](./remove_pip_cache.com) which is shown below:

``` bash
#$ -S /bin/bash
#$ -q serial
#$ -N remove-pip-cache

source /etc/profile
rm -r $global_storage/conda/pip
```

## Updating existing Conda Environments

If you want to update an existing Conda environment, it is best to delete the existing Conda environment and re-installing all of the Conda and Python pip packages. This is to ensure that all of the dependencies work within the Conda environment.