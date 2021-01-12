# HEC

Resources on how to use the [High End Computing (HEC) cluster at Lancaster University](https://answers.lancaster.ac.uk/display/ISS/High+End+Computing+%28HEC%29+help). To get access to the HEC, [follow this guidance](https://answers.lancaster.ac.uk/display/ISS/Get+access+to+the+HEC), this guidance at the time of writing mainly states that you need to ask your PI/supervisor to apply for an account for you. Once you have an account you can login via SSH e.g. `ssh username@wayland.hec.lancaster.ac.uk` for more details on how to login (e.g. login for Windows users) see this [guidance](https://answers.lancaster.ac.uk/display/ISS/Logging+in+to+the+HEC).

## Table of contents

1. [Brief overview of the HEC resources](#brief-overview-of-the-hec-resources)
    1. [Computational resources](#computational-resources)
    2. [File storage](#file-storage)
        1. [Scratch storage how to make the most of it](#scratch-storage-how-to-make-the-most-of-it)
        2. [Transferring files](#transferring-files)
        3. [Luna](#luna)
2. [Job submission/monitoring](#job-submissionmonitoring)
3. [Software installation](#software-installation)
4. [Presentations about the HEC](#presentations-about-the-hec)
5. [HEC cheat sheet](#hec-cheat-sheet)

## Brief overview of the HEC resources

### Computational resources

The HEC consists of: 

1. Login node -> The computer you login to. This is relatively slow (due to the number of users on the HEC) and should not be used for any computationally expensive tasks e.g. running a model or installing software. Should mainly be used for monitoring and assigning jobs to other nodes/computers on the HEC. Can also be used to modify files e.g. remove files.
2. CPU based nodes -> At least 445 of which at least 300 are single core nodes with around 4 to 8GB of memory. [Various 16 core nodes with either 64 or 128GB of memory. Various 40 core nodes with 192GB of memory.](https://answers.lancaster.ac.uk/display/ISS/Requesting+specific+node+types+for+jobs+on+the+HEC)
3. [GPU nodes](https://answers.lancaster.ac.uk/display/ISS/Using+GPUs+on+the+HEC) -> 2 nodes, whereby each node consists of 3 Nvidia V100 32GB GPUs, 32 CPU cores, and 192GB of memory. 

### File storage

| Name | Size | Backup | Life of storage | Environment Variable |
|------|------|--------|-----------------|----------------------|
| Home | 10GB | Nightly | Permanent | `$HOME` |
| Storage | 100GB | No | Permanent | `$global_storage` |
| Scratch | 10TB | No | Deleted after 4 weeks | `global_scratch` |
| Temporary | Unlimited | No | Only exists when job is running | `$TMPDIR` |

**Note**: `$TMPDIR` environment variable only exists when the job is running e.g. you have submitted a job to a node on a cluster.

To check the amount of storage used run `gpfsquota`

For a more detailed guide on the file storage of the [HEC see the relevant help page.](https://answers.lancaster.ac.uk/display/ISS/Using+Filestore+on+the+HEC).

#### Scratch storage how to make the most of it

The 10TB of scratch area is really useful. However files will be deleted end of day **if last modified time is 4 weeks old** (this point is really important as a lot of files you may have downloaded will likely have a last modified time of more than 4 weeks). Therefore when using the scratch make sure to update the last modified time if you want the files to be kept. To do this you can run the [./update_dir.sh](./update_dir.sh) script. This script takes one argument the file directory which you would like to update all last modified time for all files in that directory and all sub directories to the time and date of `now`. Example:

``` bash
bash update_dir.sh ./presentations
```

That would change the last modified date and time for all files in `./presentations` to `now`. **This should be fine to run on the login node.**

#### Transferring files

For Linux users this can be done through [`scp`](https://linux.die.net/man/1/scp) e.g.:

```
scp -r /PATH/TO/DIRECTORY/TO/TRANSFER username@wayland.hec.lancaster.ac.uk:/DIRECTORY/TO/TRANSFER/TO
```

For Windows users see the Lancaster [help page.](https://answers.lancaster.ac.uk/display/ISS/Transferring+files+to+the+HEC+from+a+Windows+PC)


#### Luna

(None of this sub-section has been tested yet)

A detailed guide on how to transfer files between Luna and the HEC can be found in this [help page.](https://answers.lancaster.ac.uk/display/ISS/Transferring+files+to+the+HEC+from+luna+or+other+smb-compliant+services) A bit of an extension to that help guide is provided here. As it uses the `smbclient` command of which this would likely require a password it maybe of use to create an authentication file in the following format:

```
username = <value>
password = <value>
```

This file can then be used like so:

```
smbclient -D py/gondor -A /PATH/TO/AUTHENTICATION/FILE //luna/fst
```

**By default the `smbclient` only encrypts the login credentials, to encrypt the entire payload add the `-e` flag like so:**

```
smbclient -D py/gondor -A /PATH/TO/AUTHENTICATION/FILE -e //luna/fst
```

## Job submission/monitoring

The HEC help guide on [submitting jobs](https://answers.lancaster.ac.uk/display/ISS/Submitting+jobs+on+the+HEC) and [monitoring jobs](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC) is very good and very detailed, thus please read these before reading the next sections. The only addon to HEC help guide that is provided in the README is the cheat sheet of HEC commands which can be found in the [HEC cheat sheet section](#hec-cheat-sheet).

## Software installation

The HEC has a lot of pre-installed software packages, however as software packages can conflict with each other these software packages are contained into different environment modules. Each environment module contains a different set of software e.g. some contain Python while others do not. For a detailed guide on how to use these environment modules please read the detailed [help page.](https://answers.lancaster.ac.uk/display/ISS/Using+environment+modules+on+the+HEC) From now on we assume that you know about the `module` command and what it does from the information within the help page link just given.

### Custom software installation

Even though the HEC provides a lot of different environment setups as shown from the `module avail`, if you want to install a specific software package it is not clear how this can be done. Here we show how to create a custom [Conda](https://docs.conda.io/en/latest/) setup. Conda is a "Package, dependency and environment management for any language—Python, R, Ruby, Lua, Scala, Java, JavaScript, C/ C++, FORTRAN, and more." according to the Conda website. Therefore even though this guide is going to be **Python** specific it should be possible to adapt this to other programming languages. The custom software installation guide can be found at [./install_packages](./install_packages).

## Job submission examples

In this section we will have multiple different examples of how to submit jobs to the HEC, each example will cover a slightly different edge case whether that is an edge case of the HEC or the example itself e.g. inference/tagging data compared to training a machine learning model. Some examples may build upon the previous examples and all examples assume that you understand the [custom software installation process](#custom-software-installation).

1. Predicting the required amount of memory and compute time. This will show case
2. Predicting the compute time (this is mainly useful for GPU specific jobs).
3. Predicting the required amount of GPU memory.


## Presentations about the HEC

1. A presentation briefly describing the HEC resources, access to the HEC, file store on the HEC, installing software, and training a PyTorch model on the GPU. [PDF](./presentations/26_11_20/NLP%20Group%2026_11_20.pdf) and [PowerPoint](./presentations/26_11_20/NLP%20Group%2026_11_20.pptx) presentation, and the video associated to this presentation can be found [here](https://web.microsoftstream.com/video/e510670c-2bce-4cdd-8abf-95631fccdc5f) but is only accessible to Lancaster University staff/students. This was presented at the NLP group on the 26th of November.

## HEC cheat sheet
