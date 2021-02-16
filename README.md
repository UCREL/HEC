# HEC

Resources on how to use the [High End Computing (HEC) cluster at Lancaster University](https://answers.lancaster.ac.uk/display/ISS/High+End+Computing+%28HEC%29+help). To get access to the HEC, [follow this guidance](https://answers.lancaster.ac.uk/display/ISS/Get+access+to+the+HEC), this guidance at the time of writing mainly states that you need to ask your PI/supervisor to apply for an account for you. Once you have an account you can login via SSH e.g. `ssh username@wayland.hec.lancaster.ac.uk` for more details on how to login (e.g. login for Windows users) see this [guidance](https://answers.lancaster.ac.uk/display/ISS/Logging+in+to+the+HEC).

If you have any problem with the examples, have a look at the [Problems that have arisen section](#problems-that-have-arisen) to see if the problem has occurred before, if that does not solve your problem please submit an issue on this Github page.

**If you found this HEC guide useful** in that it allowed you to use the HEC for experiments that have contributed towards a paper, your thesis, or any other type of report please could you comment on the following [issue (Found the HEC guide useful)](https://github.com/apmoore1/HEC/issues/1). The reason why collecting this information is important is so that we can show empirically why these guides are useful.

## Table of contents

1. [Brief overview of the HEC resources](#brief-overview-of-the-hec-resources)
    1. [Computational resources](#computational-resources)
    2. [File storage](#file-storage)
        1. [Scratch storage](#scratch-storage)
        2. [Transferring files](#transferring-files)
        3. [Luna](#luna)
2. [Job submission/monitoring](#job-submissionmonitoring)
3. [Software installation](#software-installation)
    1. [Custom software installation](#custom-software-installation)
4. [Hints and Tools for monitoring your **Python** jobs](#hints-and-tools-for-monitoring-your-python-jobs)
5. [Job submission examples](#job-submission-examples)
6. [Presentations about the HEC](#presentations-about-the-hec)
7. [HEC cheat sheet](#hec-cheat-sheet)
8. [External Resources/Guides](#external-resourcesguides)
    1. [GPU resources](#gpu-resources)
9. [Problems that have arisen](#problems-that-have-arisen)
10. [Acknowledgements](#acknowledgements)

## Brief overview of the HEC resources

### Computational resources

The HEC consists of: 

1. Login node -> The computer you login to. This is relatively slow (due to the number of users on the HEC) and should not be used for any computationally expensive tasks e.g. running a model or installing software. Should mainly be used for monitoring and assigning jobs to other nodes/computers on the HEC. Can also be used to modify files e.g. remove files.
2. CPU based nodes -> [Various 16 core nodes with either 64 or 128GB of memory. Various 40 core nodes with 192GB of memory.](https://answers.lancaster.ac.uk/display/ISS/Requesting+specific+node+types+for+jobs+on+the+HEC). When submitting a job for the parallel or serial queue you can see the detailed availability of compute nodes using `qslots -v`. When submitting a job (for either the parallel or serial queue) you can request the maximum amount of memory available from a node e.g. 192GB for the 40 core nodes, but you will have to wait for one of those nodes to be available. [In total the HEC has at least 9,900 cores and 50 TB of memory.](https://answers.lancaster.ac.uk/display/ISS/High+End+Computing+%28HEC%29+help)
3. [GPU nodes](https://answers.lancaster.ac.uk/display/ISS/Using+GPUs+on+the+HEC) -> 8 nodes, whereby each node consists of 3 Nvidia V100 32GB GPUs, 32 CPU cores, and 192GB of memory. Unlike the CPU based nodes the GPU nodes are time limited in that you can only run a task up to a maximum time limit. These time limits vary on the queue you submit your job too, further some of these queues limit you to the number of GPUs you can request, the table below summarises this information:

| GPU Queue Name | Time Limit | Max number of GPUs per User |
|----------------|------------|-----------------------------|
| short          | 12 hours   |  Unlimited                  |
| medium         | 48 hours   |  6                          |
| long           | 7 days     | 2                           |

**Note** unlimited here would mean 24 as there are currently 8 GPU nodes each with 3 GPUs.

**Note** using the old/historic queue name `gpu` would submit your job to the `short` queue.

**Note** for more details on [GPU queues see the HEC documentation](https://answers.lancaster.ac.uk/display/ISS/Using+GPUs+on+the+HEC).

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

#### Scratch storage

The 10TB of scratch area is really useful. However files will be deleted end of day **if last modified time is 4 weeks old** (this point is really important as a lot of files you may have downloaded will likely have a last modified time of more than 4 weeks).

#### Transferring files

For Linux users this can be done through [`scp`](https://linux.die.net/man/1/scp) e.g.:

```
scp -r /PATH/TO/DIRECTORY/TO/TRANSFER username@wayland.hec.lancaster.ac.uk:/DIRECTORY/TO/TRANSFER/TO
```

For Windows users see the Lancaster [help page.](https://answers.lancaster.ac.uk/display/ISS/Transferring+files+to+the+HEC+from+a+Windows+PC)


#### Luna

(None of this sub-section has been tested yet)

A detailed guide on how to transfer files between Luna and the HEC can be found in this [help page.](https://answers.lancaster.ac.uk/display/ISS/Transferring+files+to+the+HEC+from+luna+or+other+smb-compliant+services) A bit of an extension to that help guide is provided here, to connect to Luna it uses the [smbclient command](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)

**By default the `smbclient` only encrypts the login credentials, to encrypt the entire payload add the `-e` flag like so:**

```
smbclient -k -e -D py/gondor //luna/fst
```

The `-k` flag here uses the kerberos ticket system, which removes the need for entering your username and password each time you run the `smbclient` command. The ticket is generated when you login and expiries after 24 hours. To generate a new ticket run the `knit` command to create a new ticket. [See the HEC pages for more details (section `Using kerberos tickets`).](https://answers.lancaster.ac.uk/display/ISS/Transferring+files+to+the+HEC+from+luna+or+other+smb-compliant+services)

## Job submission/monitoring

The HEC help guide on [submitting jobs](https://answers.lancaster.ac.uk/display/ISS/Submitting+jobs+on+the+HEC) and [monitoring jobs](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC) is very good and very detailed, thus please read these before reading the next sections. In this README we also include a cheat sheet of HEC commands which can be found in the [HEC cheat sheet section](#hec-cheat-sheet).

**Note** When running jobs on the HEC you can use relative paths to files within the same directory as your submission script.

## Software installation

The HEC has a lot of pre-installed software packages, however as software packages can conflict with each other these software packages are contained into different environment modules. Each environment module contains a different set of software e.g. some contain Python while others do not. For a detailed guide on how to use these environment modules please read the detailed [help page.](https://answers.lancaster.ac.uk/display/ISS/Using+environment+modules+on+the+HEC) From now on we assume that you know about the `module` command and what it does from the information within the help page link just given.

The HEC recommends requesting any software (including Conda environments) that you would like to use on the HEC, that does not already exist, by submitting a request or report via [https://helpcentre.lancaster.ac.uk](https://helpcentre.lancaster.ac.uk). If the software you requested for cannot be installed then please see the [custom software installation sub-section below.](#custom-software-installation) 

### Custom software installation

Here we show how to create a custom [Conda](https://docs.conda.io/en/latest/) setup. Conda is a "Package, dependency and environment management for any language—Python, R, Ruby, Lua, Scala, Java, JavaScript, C/ C++, FORTRAN, and more." according to the Conda website. Therefore even though this guide is going to be **Python** specific it should be possible to adapt this to other programming languages. The custom software installation guide can be found at [./install_packages](./install_packages).

## Hints and Tools for monitoring your **Python** jobs 

The main point of this section is to provide you with the tools and knowledge of understanding where the main cause of increasing memory, CPU time, and GPU memory is likely to come from in your code that you submit as a job on the HEC. The [monitoring tools that the HEC provide](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC) are still useful but are more coarse grained but non-language specific. These guides show how you can work out how much memory is required to process a batch of data for tagging/inference and the time it would take.

The hints and tools section can be found at [./examples/hints_tools_for_python_monitoring](./examples/hints_tools_for_python_monitoring) and it covers tools with examples on monitoring RAM, CPU time, and GPU memory use in detail.

## Job submission examples

In this section we will have multiple different examples of how to submit jobs to the HEC, each example will cover a slightly different edge case whether that is an edge case of the HEC or the example itself e.g. inference/tagging data compared to training a machine learning model. All examples assume that you understand the [custom software installation process](#custom-software-installation).

1. Running a single job -- [./examples/single_job](./examples/single_job), this example shows how to tag Alice in Wonderland book with Named Entities using SpaCy.
2. Running multiple similar jobs -- [./examples/multiple_similar_jobs](./examples/multiple_similar_jobs), similar to example 1 above, but tagging multiple books with named entities **using Stanza and more than one node on the HEC for processing at the same time**. This is an NLP example of what the [HEC documentation calls an array job, of which this link sends you to the HECs great example of an array job.](https://answers.lancaster.ac.uk/display/ISS/Submitting+multiple+similar+jobs+on+the+HEC) This makes tagging lots of files a lot quicker as more than one node can be processing files at the same time.
3. Running a single job of the GPU nodes -- [./examples/single_gpu_job](./examples/single_gpu_job), same as example 1 above but using the GPU node instead of a CPU node.
4. Running multiple similar jobs using GPU nodes -- [./examples/multiple_similar_gpu_jobs](./examples/multiple_similar_gpu_jobs), same as example 2 above but using the GPU nodes instead of the CPU nodes.

## Presentations about the HEC

1. **Archive only** A presentation briefly describing the HEC resources, access to the HEC, file store on the HEC, installing software, and training a PyTorch model on the GPU. [PDF](./presentations/26_11_20/NLP%20Group%2026_11_20.pdf) and [PowerPoint](./presentations/26_11_20/NLP%20Group%2026_11_20.pptx) presentation, and the video associated to this presentation can be found [here](https://web.microsoftstream.com/video/e510670c-2bce-4cdd-8abf-95631fccdc5f) but is only accessible to Lancaster University staff/students. This was presented at the NLP group on the 26th of November.
2. An updated and more correct version of the 1st presentation has been created that better reflects the current code base/documentation and the HEC. The presentation does not include training a PyTorch model on the GPU but rather tagging data using the GPU instead. [PowerPoint](./presentations/updated_26_11_20/NLP_Group_26_11_20.pptx) and [PDF](./presentations/updated_26_11_20/NLP_Group_26_11_20.pdf) versions of the presentation, no video presentation has been made.

## HEC cheat sheet

See [./HEC_cheat_sheet.md](./HEC_cheat_sheet.md) for the cheat sheet.


## External Resources/Guides

Here is a list of external resources that might be of use.

### GPU resources

1. [William Falcon 7 tips to maximize PyTorch performance.](https://towardsdatascience.com/7-tips-for-squeezing-maximum-performance-from-pytorch-ca4a40951259)

## Problems that have arisen

1. If you are running an install script and your are installing a Conda environment to a directory whereby an existing Conda environment exists, you will probably get the following error:

``` bash
CondaValueError: prefix already exists
```

If so either delete this existing Conda environment and run the install script again or you will have to save the new Conda environment to a different new directory.

2. If you are transferring files from Windows to the HEC you may get an error like so in your submission script e.g. scripts with `.com` file extension:

``` bash
/usr/shared_apps/packages/sge-8.1.8-1/default/spool/comp14-04/job_scripts/7121307: line 2: $'\r': command not found
/usr/shared_apps/packages/sge-8.1.8-1/default/spool/comp14-04/job_scripts/7121307: line 6: $'\r': command not found
/usr/shared_apps/packages/sge-8.1.8-1/default/spool/comp14-04/job_scripts/7121307: line 7: /etc/profile^M: No such file or directory
```

This is due to [Windows adding `\r` character to the end of new lines](https://superuser.com/questions/156516/is-there-a-bash-command-to-convert-r-n-to-n). To overcome this problem run the `dos2unix` command on the submission script that is causing these problems e.g. if the submission script is `install.com` run `dos2unix install.com` this will remove the `\r` character from the `install.com` file and should allow you to run the script through the HEC without error.

3. If your Conda or pip package installation script is not working as it is hanging/failing on installing one package this could be due to the package being corrupted in the Conda cache directory. To resolve this problem delete the Conda environment that you were creating in that installation script that failed. Then clean the Conda cache by following the instruction in the [Conda and Pip cache management section within the custom software installation guide.](./install_packages/README.md#conda-and-pip-cache-management)

4. When installing your own custom Conda environments, following the instructions in the [custom software installation guide](./install_packages), it can be the case that Conda fails without good reason, or just hangs and never installs all of the packages thus failing to install the required Conda environment fully. Sometimes this happens and by the next day it would work, which I guess might be something Conda's end that they have fixed in their remote packages. Other times it could be due to having multiple Conda environments thus if you can remove Conda environments that you do not need any more then I would suggest doing that and then cleaning the Conda and Pip cache following the instructions in the [Conda and Pip cache management section within the custom software installation guide](./install_packages/README.md#conda-and-pip-cache-management), after this your new Conda environment may install. Another suggestion that has worked in the past is to use a different Python version **if you can** e.g. instead of using Python version `3.8` use `3.7` instead. Lastly it can take a while for the HEC to create a Conda environment and install all of it's dependencies e.g. up to one hour but it should not take much longer than one hour from our experience.

## Acknowledgements

This guide has been funded through the [UCREL research centre at Lancaster University](http://ucrel.lancs.ac.uk/).

This guide has been refined and improved upon through the advice and help of Mike Pacey from [Information System Services (ISS) at Lancaster University.](https://www.lancaster.ac.uk/iss/)

