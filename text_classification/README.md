# Text Classification Example

Here we demonstrate how to use the HEC on a text classification task, thus we are going to reproduce the results from the paper [GoEmotions: A Dataset of Fine-Grained Emotions](https://www.aclweb.org/anthology/2020.acl-main.372.pdf). The main results we are reproducing are those from table 4, whereby the task is given a text (reddit comment) predict the emotion within the comment. This task is a multi-label classification task, therefore more than one emotion can be assigned to a comment. Here we are going to use the same model, a fine tuned [BERT<sub>base</sub> model](https://www.aclweb.org/anthology/N19-1423.pdf).

## Installation

1. Python >=3.6.1
2. PyTorch >=1.0.0 -- This is best installed manually based on whether you want to use CPU or GPU and if GPU which version of CUDA.
3. `pip install requirements.txt`

As we are using the HuggingFace Transformers package and we are using the BERT pre-trained model. This pre-trained model will be downloaded automatically to the following directory bt default `~/.cache/torch/transformers/`. This default directory can be changed by setting the `TRANSFORMERS_CACHE` environment variable, alternatively you can set it in the Python code using the `cache_dir` argument.


## Dataset details

This dataset has 27 categories (see [appendix A in the paper](https://www.aclweb.org/anthology/2020.acl-main.372.pdf) for details on those 27 labels). There was another category `neutral` which is used when no emotion was expressed within the text. However from looking at the dataset the `neutral` category can exist with other emotions for a given text. They state in the paper Reddit has a bias towards young male users, toxic and offensive language thus they perform various different data filtering techniques that can be found in [section 3.1 of the paper](https://www.aclweb.org/anthology/2020.acl-main.372.pdf). They also masked  both people's names and religion terms with `[NAME]` and `[RELIGION]` tokens respectively.

To get the main dataset that was used for training, developing, and testing the model run the following script, which will create the directory `./data` and add `train.tsv`, `dev.tsv`, and `test.tsv` to that directory:

``` bash
python download_data.py
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

[BERT<sub>base</sub> model](https://www.aclweb.org/anthology/N19-1423.pdf) is a 12 layer transformer model with 12 attention heads per layer with a 768 dimension hidden layer. As we are fine tuning it for multi-label classification the final layer will use the the classification token (`[cls]` in [figure 1](https://www.aclweb.org/anthology/N19-1423.pdf)) representation as input to 28 separate linear layers (one for each of the classes, including the neutral class). All of the 28 linear layers will be put through a sigmoid activation function to predict if the text contains the associated emotion label. This model setup is the same as the GoEmotions paper and we use the same loss function the sigmoid cross entropy loss function, `BCEWithLogitsLoss` in PyTorch.

In the original paper they used the following hyper-parameters for the BERT model:

1. batch size = 16
2. learning rate = 5e-5
3. training for 4 epochs.


## Running the model

Before running the model on the HEC, it would be best to download the transformer model you are going to use. If running this on the HEC the transformer models take up a lot of hard disk so it would be best to store these in the `$global_scratch` directory. The easiest way to set where the transformer models are downloaded too is to set the `TRANSFORMERS_CACHE` environment variable, see the [caching models section on the huggingface transformer documentation for more details.](https://huggingface.co/transformers/installation.html#caching-models). By default the transformer models are saved to your home directory, which on the HEC can only store 10GB. To download the transformer model you could use the [./download_transformer_model.py](./download_transformer_model.py) script like so:

```bash
python download_transformer_model.py
``` 

Whereby default it download the `bert-base-uncased` transformer model but can also download other transformer models if wanted like RoBERTa, for a [full list of pre-trained transformer names](https://huggingface.co/transformers/pretrained_models.html):

```bash
python download_transformer_model.py --transformer-model roberta-base
```

To ensure that the transformer model is saved to a directory of choice we have wrapped this up into a bash script whereby the first argument specifies the directory assigned to `TRANSFORMERS_CACHE` environment variable and the second specifies the transformer model we want to download. In the example below we download the `albert-base-v1` transformer model and save it to the `~/transformer_models` directory (this directory does not have to exist):

```bash
./transformer_model_download.sh ~/transformer_models albert-base-v1
```

To train the model for one epoch:
``` bash
python ./bert_model.py ./data/train.tsv ./data/dev.tsv ./data/test.tsv ./data/emotions.txt ./model/saved_model.pt --cuda --batch-size 16
```

All this does is train a BERT model on the multi label training dataset for one epoch. It actually does nothing with the development and test files at the moment. At the end of the script it prints out the time it takes to train the model for one epoch. On my home machine with a 6GB nvidia 1060 it takes around 20 minutes and I have to use a batch size of 4. This also prints the loss every 100 batches and the average loss across the whole epoch it was trained on.