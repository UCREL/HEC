# Multi Label Text Classification GPU Example

Here we demonstrate how to use the HEC on a text classification task, thus we are going to reproduce the results from the paper [GoEmotions: A Dataset of Fine-Grained Emotions](https://www.aclweb.org/anthology/2020.acl-main.372.pdf). The main results we are reproducing are those from table 4, whereby the task is given a text (reddit comment) predict the emotion within the comment. This task is a multi-label classification task, therefore more than one emotion can be assigned to a comment. Here we are going to use the same model, a fine tuned [BERT<sub>base</sub> model](https://www.aclweb.org/anthology/N19-1423.pdf).


## Dataset details

This dataset has 27 categories (see [appendix A in the paper](https://www.aclweb.org/anthology/2020.acl-main.372.pdf) for details on those 27 labels). There was another category `neutral` which is used when no emotion was expressed within the text. However from looking at the dataset the `neutral` category can exist with other emotions for a given text. They state in the paper Reddit has a bias towards young male users, toxic and offensive language thus they perform various different data filtering techniques that can be found in [section 3.1 of the paper](https://www.aclweb.org/anthology/2020.acl-main.372.pdf). They also masked  both people's names and religion terms with `[NAME]` and `[RELIGION]` tokens respectively.

To get the main dataset that was used for training, developing, and testing the model run the following script, which will create the directory `./data` and add `train.tsv`, `dev.tsv`, and `test.tsv` to that directory:

``` bash
python download_data.py ./data
```

Each TSV contains the following columns:

1. text.
2. comma-separated list of emotion ids (the ids are indexed based on the order of emotions in [./data/emotions.txt](./data/emotions.txt) e.g. id 27=`neutral` and id 0=`admiration`).
3. id of the comment.

The following statistics of the different splits (train, development, and test) per label separated by a comma:

1. label name
2. label raw count
3. percentage of texts that contains this label
4. percentage of times it occurs with another label.

Can be seen if the following script is ran:

```bash
python data_analysis.py
```

The number of examples per split matches that stated in the original paper stated in their [Github repository](https://github.com/google-research/google-research/tree/master/goemotions#data):

1. Train - 43,410 samples
2. Development - 5,426 samples
3. Test - 5,427 samples

Furthermore what I find interesting is that across all of the three splits the neutral label for at least 9.8% of samples is in a text that is assigned with at least one other label. However out of all of the labels the neutral label is most likely assigned to a sample with no other label with respect to the frequency of each label e.g. some labels occur very frequently but when normalised to their label count they are less likely to be assigned to a sample with no other label.

## Model details

This section explains the model that was used in the [GoEmotions: A Dataset of Fine-Grained Emotions](https://www.aclweb.org/anthology/2020.acl-main.372.pdf) paper.

[BERT<sub>base</sub> model](https://www.aclweb.org/anthology/N19-1423.pdf) is a 12 layer transformer model with 12 attention heads per layer with a 768 dimension hidden layer. As we are fine tuning it for multi-label classification the final layer will use the the classification token (`[cls]` in [figure 1](https://www.aclweb.org/anthology/N19-1423.pdf)) representation as input to 28 separate linear layers (one for each of the classes, including the neutral class). All of the 28 linear layers will be put through a sigmoid activation function to predict if the text contains the associated emotion label. This model setup is the same as the GoEmotions paper and we use the same loss function the sigmoid cross entropy loss function, `BCEWithLogitsLoss` in PyTorch.

In the original paper they used the following hyper-parameters for the BERT model:

1. batch size = 16
2. learning rate = 5e-5
3. training for 4 epochs.


## Explaining the scripts

1. [download_transformer_model.py](./download_transformer_model.py) -- Downloads a transformer model from the HuggingFace library, this is best to do before running any scripts that require a transformer model as those scripts would have to download the transformer model and that could take up time on a GPU node where as the process of downloading the model can be done on a small CPU node. By default it download the `bert-base-uncased` transformer model but can also download other transformer models if wanted like RoBERTa, for a [full list of pre-trained transformer names](https://huggingface.co/transformers/pretrained_models.html):

```bash
python download_transformer_model.py --transformer-model roberta-base
```

Further when running this script on the HEC the transformer models be default are saved to your `Home` directory, which on the HEC can only store 10GB. However you can change this by setting a different File path to the environment variable `TRANSFORMERS_CACHE` e.g. setting `TRANSFORMERS_CACHE` to `$global_storage/huggingface_transformer_models_cache` e.g.:

``` bash
TRANSFORMERS_CACHE=$global_storage/huggingface_transformer_models_cache
export TRANSFORMERS_CACHE
```

For more details on the HuggingFace model caching see the see the [caching models section on the HuggingFace transformer documentation.](https://huggingface.co/transformers/installation.html#caching-models)

2. [download_data.py](./download_data.py) -- Downloads the data to a given directory e.g. in this case it will download the `train`, `dev`, `test`, and emotion labels to the directory `./data` whereby each will be called `./data/train.tsv`, `./data/dev.tsv`, `./data/test.tsv`, and `./data/emotions.txt`:

``` bash
python download_data.py ./data
```

3. [bert_model.py](./bert_model.py) -- Trains a transformer model for one epoch with the following arguments:
    1. Path to training data
    2. Path to development data
    3. Path to test data
    4. Path to the emotion labels
    5. Path to save the trained model
    6. `--cuda` -- whether to use CUDA or not e.g. `--cuda` for GPU.
    7. `--learning-rate` -- whether to specify a learning rate other than the default `5e-5`
    8. `--batch-size` -- whether to specify a batch size other than default `16`
    9. `--transformer-model` -- whether to use a transformer model other than the default English `bert-base-uncased`. For a [full list of pre-trained transformer names that can be used.](https://huggingface.co/transformers/pretrained_models.html)

Example of how to use this script:

``` bash
python ./bert_model.py ./data/train.tsv ./data/dev.tsv ./data/test.tsv ./data/emotions.txt ./model/saved_model.pt --cuda --batch-size 16
```

This specifies that we do want to use the GPU (`--cuda`) and to use a batch size of 16.

**NOTE** The `bert_model.py` is work in progress in that it only trains the model for one epoch on the given data and prints out how long it took to train for one epoch, how long it took to save the trained model, the loss every 100 batches and the average loss across the whole epoch it was trained on. On my home machine when using the English `bert-base-uncased` transformer model it took 20 minutes to run using a 6GB nvidia 1060 GPU with a batch size of 4.

## Running on the HEC

The following steps explains how to train a transformer model on the HEC using this Emotions dataset, in this case we are going to fine-tune the English `roberta-base` transformer model. In all of the steps we are going to utilise in some way the scripts explained in [Explaining the scripts section above](#explaining-the-scripts).

1. Transfer this directory to your home directory on the HEC: `scp -r ../multi_label_classification_gpu/ username@wayland.hec.lancaster.ac.uk:./`
2. Login to the HEC `ssh username@wayland.hec.lancaster.ac.uk` and go to the text classification directory: `cd multi_label_classification_gpu`
3. Create the Conda environment with the relevant python dependencies. This can be done by submitting the [./install.com](./install.com) job e.g. `qsub install.com`. This will create the Conda environment at `$global_storage/conda_environments/py3.7-text-classification`
4. Download the transformer model, `roberta-base`, and the data we are going to train/test. This is done now before training the model so we do not waste GPU node time downloading the model and data rather here we shall use a CPU node. `qsub download_model_data.com` will download the data to `$global_storage/data/go-emotions` and the model to `$global_storage/huggingface_transformer_models_cache`.
5. Now we are going to train the model so we need to switch to the GPU cluster `switch-gpu`
6. To train the model for one epoch `qsub run_transformer_model.com`. This will save the fine-tuned `roberta-base` model to `$global_storage/models/go-emotions//roberta_base.pt`. This ran on the HEC in 157 seconds which is a lot quicker than my home machine which took 20 minutes.
7. To find out how much GPU memory you used you can cat the output of the output file e.g. `cat run-transformer-model.o3177`, in my case it used 16 GB (17728274432 bytes). You can find how much RAM was used through `qacct -j 3177` and then looking at the field `maxvmem` in my case it used 4 GB.
