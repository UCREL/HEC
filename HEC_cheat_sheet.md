# Table of contents

1. [Job Submission commands](#job-submission-commands)
2. [Resource Allocation commands](#resource-allocation-commands)
3. [General Monitoring commands ](#general-monitoring-commands)
    1. [GPU Monitoring commands](#gpu-monitoring-commands)
4. [Module commands](#module-commands)


## Job Submission commands

| Command | Options | Example | Description |
|---------|---------|---------|-------------|
| qsub | | qsub submission_script | Submit the `submission_script` to be processed by the HEC |
| qdel | | qdel job_id | Cancel the job which is associated with the given `job_id`. |

If your using an [array job and want to stop specific tasks see the HEC documentation.](https://answers.lancaster.ac.uk/display/ISS/Submitting+multiple+similar+jobs+on+the+HEC)

## Resource Allocation commands

| Command | Options | Example | Description |
|---------|---------|---------|-------------|
| qslots
| gpfsquota | | gpfsquota | View your home, storage, and scratch space usage |
| qquota |  | qquota | Amount of resources your using on the HEC in relation to the amount of resources your allowed to use. Outputs nothing if your not running any jobs. |

## General Monitoring commands 

[To get an email notification on when a job completes see the HEC documentation.](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC):

| Command | Options | Example | Description |
|---------|---------|---------|-------------|
| qstat   |         | qstat   | Output a list of all your jobs currently waiting `qw`, transferring `t`, running `r`, or error state `Eqw`. |
| qtop | -u | qtop -u username | Outputs/displays the [`top` command](https://man7.org/linux/man-pages/man1/top.1.html) for all your running jobs, it can be difficult to interpret if you are running multiple jobs, in this case read the [HEC documentation to get a better understanding](https://answers.lancaster.ac.uk/display/ISS/Monitoring+jobs+on+the+HEC). |
| qacct   | -j      | qacct -j job_id        | Reports various resource usage statistics for a completed `job_id` e.g. memory and time taken. For details on the statistics see [accounting man page](https://linux.die.net/man/5/sge_accounting)            |
|         | -t      | qacct -j job_id -t task_id | Same as `-j` option but only reports for the task id. Only used when an [array job](https://answers.lancaster.ac.uk/display/ISS/Submitting+multiple+similar+jobs+on+the+HEC) has been submitted. Requires `-j` option. |

### GPU Monitoring commands

| Command | Options | Example | Description |
|---------|---------|---------|-------------|
| qgputop | -u | qgputop -u username | Displays the [nvidia-smi output](https://developer.nvidia.com/nvidia-system-management-interface) for all GPUs your using. |

## Module commands

For more details on [these commands see the HEC documentation.](https://answers.lancaster.ac.uk/display/ISS/Using+environment+modules+on+the+HEC)

| Command | Options | Example | Description |
|---------|---------|---------|-------------|
| module avail | | module avail | View all available modules |
|  | | module avail package_name | View all available modules for that particular `package_name` |
| module whatis | | module whatis matlab | A description of a software package, in this case matlab |
| module show | | module show matlab | A detailed description of a software package, in this case matlab |
| module add | | module add matlab | To use/access a module, in this case to use the matlab module. |
| module list | | module list | List all modules currently added to your environment. |
| module rm | | module rm matlab | To remove a module from your environment, in this case the matlab module. |
| module switch | | module switch pgi/6.2-32-bit | To switch versions of a module, in this case we switch from a version of `pgi` to `pgi/6.2-32-bit`. |