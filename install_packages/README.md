# Custom software installation

Here we assume that you have read the [file storage introduction](../README.md#file-storage) and [scratch storage how to make the most of it sub-section](../README.md#scratch-storage-how-to-make-the-most-of-it) from the main [README](../README.md). Also that you have read the [Job submission/monitoring](../README.md#job-submissionmonitoring) section from the main README.

In this tutorial we show how you can install your own Python environment given the `anaconda3/wmlce` module available within the module list on the HEC. The `anaconda3/wmlce` module is chosen here as the base module as it:

* Contains the most up-to-date version of `Conda` out of all of the `anaconda3` modules available on the HEC. For reference as of writing this it runs Conda version 4.8.2 which came out on the 24/01/2020.

## How Conda creates an environment

When you are creating your own Python environment with Conda you are in affect creating an area on disk space (from now on called the **Python environment folder**) that contains executable programs, which in this case are mainly the Python program and all of it's dependencies e.g. pip and system dependencies. In general we recommend saving this to the `Scratch` space as some environment folders can be large e.g. 4.9GB.

## Conda environment file

The Python environment that Conda creates is determined by the dependencies specified within an `environment` YAML file, details of how to create one can be found on the [Conda manual page.](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually)

## Description of the install script

The best way to create your own Python environment on the HEC is by making it a batch job in itself, for a detailed overview on how to submit jobs to the HEC see this [guide](https://answers.lancaster.ac.uk/display/ISS/Submitting+jobs+on+the+HEC). The general outline for the batch job can be seen in the [./install.com](./install.com) script whereby lines 14 and 20 need updating with where you want to save on disk the Python environment folder and the location of the `environment` YAML file. 

You may have noticed that this script runs on a single core CPU node with 4GB of RAM. This was chosen as this is the most common node on the HEC and 4GB of RAM is the most RAM you can request before having to request a more specialist CPU node (you do not have to ask for this specialist node unless it is more than 8GB I believe) of which there will be fewer of these nodes available on the HEC. However by requesting 4GB of RAM it may be sitting in the job queue for a bit of time when the HEC is busy as jobs with less requested RAM will take more priority for a small period of time.

The name of the job is `conda-local` this can be changed, if wanted too, to whatever you want it to be.

The `CONDA_ENVS_PATH` and `CONDA_PKGS_DIRS` are set to a directory within `$TMPDIR` as by default Conda would use your `Home` file space to save these files to, this is not needed as we are specifying where we want to save the Python environment folder to through the `-p` flag on line 20:

``` bash
time -v conda-env create -p $conda_save_location --file CHANGE-$HOME/environment.yaml
```

The last few lines of the [./install.com](./install.com) script:

```bash
find $conda_save_location -print | while read filename; do
	touch -h "$filename"
done
```

This ensures that any files in the Python environment folder that has been created last modified time is `now` so that if you have saved it to the `Scratch` file space they have 4 weeks before they are deleted, unless of course you update the last modified time again in the future.

## Example

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
  - pip:
    - joeynmt==1.0.0
```

All of the dependencies that not `pip` dependencies e.g. `python` and `pytorch` are `conda` packages and are installed from the `conda` packages found in the specified `conda channels`. As you can see we have two `channels` of which the order they are specified does determine priority of which in this case the `pytorch` channel takes priority over `defaults` the reason for this is due to `pytorch conda` dependency being in both channels and we want the one from the `pytorch` channel over the `default` channel.

To create this Python environment and save it to `$global_scratch/py3.8-gpu-joeynmt` perform the following steps:

1. Copy the `./example` directory to your `Home` space: `scp -r example/ username@wayland.hec.lancaster.ac.uk:./`. `./` on a remote server is short hand for your home directory.
2. Login to the HEC: `ssh username@wayland.hec.lancaster.ac.uk`
3. Go to the example folder: `cd example`
4. Run the job: `qsub example_install.com`
5. Wait some time, mine took 3 minutes and 33 seconds to run, to monitor the job you can use the [`qstat` command](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC). Sometimes you may have to wait some time before the job starts if the HEC is busy.
6. You can find how long it took to run by `cat` the error file in my case this was `cat conda-local.e6170308`
7. To test if everything has worked you should see the directory `py3.8-gpu-joeynmt` in `$global_scratch` e.g. `ls $global_scratch`. Additionally if you run `module add anaconda3/wmlce` then `source activate $global_scratch/py3.8-gpu-joeynmt` then `python --version` should be version 3.8 and you should be able to run without error the following `python -c "import joeynmt; print(joeynmt)"`
8. Run `source deactivate`

The `source activate $global_scratch/py3.8-gpu-joeynmt` tells conda that you want to use custom environment at `$global_scratch/py3.8-gpu-joeynmt`. `source deactivate` tells conda to stop using that custom environment.

Once you have finished with this custom python environnement it can be easily removed by:

``` bash
rm -r $global_scratch/py3.8-gpu-joeynmt
``` 

This can take a bit of time to complete e.g. a minute or two.

