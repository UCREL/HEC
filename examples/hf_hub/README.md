# Hugging Face Hub example

In this example we show how you can download a model repository from the [Hugging Face model hub](https://huggingface.co/models), more specifically we download the [electra small discriminator model repository](https://huggingface.co/google/electra-small-discriminator/tree/main), to a local directory, in this example the local directory is `$global_storage/hf_models/google_electra_small_discriminator` (`$global_storage` is an environment variable on the HEC, for more information on this environment variable see the [file storage table in the main README](../../README.md#file-storage)).

To do this we are going to run the [./hf_download_script.py script](./hf_download_script.py) which takes two arguments:

1. `download_dir` -- Directory to save the cloned model hub repository too. In this example this would be `$global_storage/hf_models/google_electra_small_discriminator`
2. `clone_from` -- Hugging Face model hub repository to clone from. In this example this would be `google/electra-small-discriminator`

## Installation

Before running this script we will need to create a custom Conda environment so that we have a Python environment that has the [Hugging Face Hub API](https://pypi.org/project/huggingface-hub/) and all of it's dependencies. The main dependencies for the Hugging Face API are the following, which are installed as Conda packages, of which these dependencies are specified in the [./environment.yaml file](./environment.yaml):

- git
- git-lfs

## Running on the HEC

1. Transfer this directory to your home directory on the HEC: `scp -r ../hf_hub/ username@wayland.hec.lancaster.ac.uk:./`
2. Login to the HEC `ssh username@wayland.hec.lancaster.ac.uk` and go to the `hf_hub` directory: `cd hf_hub`
3. Create the Conda environment with the relevant Conda and Python dependencies. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the Conda environment at `$global_storage/conda_environments/py3.9-hf-hub`
4. We can now run the Python script [./hf_download_script.py](./hf_download_script.py), by submitting the [./hf_download_script.com](./hf_download_script.com) job, e.g. `qsub hf_download_script.com`, this will download the [electra small discriminator model repository](https://huggingface.co/google/electra-small-discriminator/tree/main) to `$global_storage/hf_models/google_electra_small_discriminator` (the [./hf_download_script.com](./hf_download_script.com) job also creates the `$global_storage/hf_models` directory for you if it does not exist)

After you have ran the script, it also logs the name of files in the model repository that was downloaded and the model card data to the output file (my output file was named `hf_download.o9821916`), you can see below what part of the output file should contain:

```
Model card data: {'language': 'en', 'thumbnail': 'https://huggingface.co/front/thumbnails/google.png', 'license': 'apache-2.0'}
Files that have been cloned from the google/electra-small-discriminator model repository into the directory: /mmfs1/storage/users/moorea/hf_models/google_electra_small_discriminator:
config.json
pytorch_model.bin
.gitattributes
tf_model.h5
tokenizer_config.json
vocab.txt
flax_model.msgpack
README.md
tokenizer.json
.git
```

### General notes

1. According to the [Hugging Face Hub API documentation](https://huggingface.co/docs/hub/how-to-upstream#upload-very-large-files) if you want to **upload** (all this example does is download) files larger than 5GB you need to install/enable a custom transfer agent for Git-LFS **for each repository**. On line 46 of the [./hf_download_script.py python script](./hf_download_script.py#L46) it shows you how this can be installed/enabled (it does not require you to install anything, just requires you to allow/enable it from what I have found).