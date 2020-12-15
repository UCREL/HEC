# HEC

Resources on how to use the [High End Computing (HEC) cluster at Lancaster University](https://answers.lancaster.ac.uk/display/ISS/High+End+Computing+%28HEC%29+help). To get access to the HEC, [follow this guidance](https://answers.lancaster.ac.uk/display/ISS/Get+access+to+the+HEC), this guidance at the time of writing mainly states that you need to ask your PI/supervisor to apply for an account for you. Once you have an account you can login via SSH e.g. `ssh username@wayland.hec.lancaster.ac.uk` for more details on how to login (e.g. login for Windows users) see this [guidance](https://answers.lancaster.ac.uk/display/ISS/Logging+in+to+the+HEC).

## Table of contents

1. [Brief overview of the HEC resources](#brief-overview-of-the-hec-resources)
2. [Presentations about the HEC](#presentations-about-the-hec)

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

## Presentations about the HEC

1. A presentation briefly describing the HEC resources, access to the HEC, file store on the HEC, installing software, and training a PyTorch model on the GPU. [PDF](./presentations/26_11_20/NLP\ Group\ 26_11_20.pdf) and [PowerPoint](./presentations/26_11_20/NLP\ Group\ 26_11_20.pptx) presentation, and the video associated to this presentation can be found [here](https://web.microsoftstream.com/video/e510670c-2bce-4cdd-8abf-95631fccdc5f) but is only accessible to Lancaster University staff/students. This was presented at the NLP group on the 26th of November.