# The code here is heavily based on this notebook:
# https://github.com/abhimishra91/transformers-tutorials/blob/master/transformers_multi_label_classification.ipynb
import csv
from pathlib import Path
from typing import Tuple, Dict, List, Union, Optional

from sklearn.preprocessing import MultiLabelBinarizer
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import PreTrainedTokenizerBase, AutoTokenizer, AutoModel

def label_mapper_binarizer(label_fp: Path) -> Tuple[Dict[int, str], MultiLabelBinarizer]:
    '''
    As all of the label in the datasets are based on line index in the 
    `emotions.txt` file this function returns a mapper of line index to label.
    Further it also return a binarizer that converts a list of line index labels 
    to one hot encoding which is required for training a model.

    :param label_fp: File path to a file that contains a label on each new line.
    :returns: A tuple of length 2. The first item is a mapper of line index to 
              label. The second item is a label binarizer that when given a 
              list of label indexes it will convert them to one hot encoding.
    '''
    indexes: List[List[int]] = []
    label_mapper: Dict[int, str] = {}
    with label_fp.open('r') as label_file:
        for index, line in enumerate(label_file):
            label_mapper[index] = line.strip()
            indexes.append([index])
    mlb = MultiLabelBinarizer()
    mlb.fit(indexes)
    return label_mapper, mlb

class EmotionsDataset(Dataset):

    def _get_data(self, split_fp: Path) -> Tuple[List[str], List[List[int]], List[str]]:
        '''
        :param split_fp: A TSV file path containing the GoEmotions data. columns:
                         1. text, 2. comma separated list of label ids, 3. ID of 
                         data.
        :returns: A tuple of length 3. 1. A list of texts for each sample,
                  2. For each sample the corresponding list of labels, 
                  3. For each sample it's corresponding ID string.
        '''
        texts = []
        labels = []
        unique_ids = []

        with split_fp.open('r', newline='') as split_file:
            tsv_reader = csv.reader(split_file, delimiter='\t')
            for line in tsv_reader:
                texts.append(line[0].strip())
                labels.append([int(label) for label in line[1].split(',')])
                unique_ids.append(line[2].strip())
        return texts, labels, unique_ids
            
    def __init__(self, split_fp: Path) -> None:
        self.texts, self.labels, self.unique_ids = self._get_data(split_fp)

    def __len__(self) -> int:
        return len(self.unique_ids)

    def __getitem__(self, index: int) -> Dict[str, Union[List[int], str]]:
        '''
        :param index: Sample index to return. 
        :returns: A dictionary of:
                  1. text -> text from the sample
                  2. labels -> List of labels associated to the sample
                  3. id -> String representing the unique id of this sample.

        '''
        multiple_labels: List[int] = self.labels[index]
        text = self.texts[index]

        # text id just in case we need to debug or want to find the original 
        # sample in the dataset
        _id = self.unique_ids[index]
        return {'text': text, 'labels': multiple_labels, 'id': _id}

class DataCollatorWithPadding():

    def __init__(self, tokenizer: PreTrainedTokenizerBase, 
                 label_binarizer: MultiLabelBinarizer) -> None:
        self.tokenizer = tokenizer
        self.label_binarizer = label_binarizer

    def __call__(self, batch: List[Dict[str, Union[str, List[int]]]]) -> Dict[str, torch.Tensor]:
        texts: List[str] = []
        labels: List[List[int]] = []
        for sample in batch:
            # Assert statement required for mypy
            text = sample['text']
            assert isinstance(text, str)
            texts.append(text)
            
            multi_label = sample['labels']
            assert isinstance(multi_label, list)
            labels.append(multi_label)
        tokenized_texts = self.tokenizer(texts, padding=True, truncation=True, 
                                         return_tensors="pt")
        labels = torch.from_numpy(label_binarizer.transform(labels)).float()
        tokenized_batch = {**tokenized_texts, 'labels': labels}

        return tokenized_batch

class TransformerModel(torch.nn.Module):

    def __init__(self, transformer_name: str, number_labels: int) -> None:
        super().__init__()
        self.transformer_encoder = AutoModel.from_pretrained(transformer_name)
        self.dropout = torch.nn.Dropout(0.5)

        transformer_hidden_size = self.transformer_encoder.config.hidden_size
        self.output_layer = torch.nn.Linear(transformer_hidden_size, number_labels)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, 
                token_type_ids: Optional[torch.Tensor]) -> torch.FloatTensor:
        encoded_input = self.transformer_encoder(input_ids=input_ids, 
                                                 attention_mask=attention_mask, 
                                                 token_type_ids=token_type_ids,
                                                 return_dict=True)
        dropped_encoded_input = self.dropout(encoded_input['pooler_output'])
        logits = self.output_layer(dropped_encoded_input)
        return logits

    def loss_function(self, logits: torch.FloatTensor, labels: torch.FloatTensor
                      ) -> torch.FloatTensor:
        '''
        :returns: A one dimension loss value
        '''
        return torch.nn.BCEWithLogitsLoss()(logits, labels)

def train(model: torch.nn.Module, train_dataloader: DataLoader, 
          optimizer: torch.optim.Optimizer, device: str):
    model.train()
    avg_loss = 0
    count = 0
    for index, data in enumerate(train_dataloader):
        input_ids = data['input_ids'].to(device)
        attention_mask = data['attention_mask'].to(device)
        token_type_ids = None
        if 'token_type_ids' in data:
            token_type_ids = data['token_type_ids'].to(device)
        labels = data['labels'].to(device)

        logits = model(input_ids, attention_mask, token_type_ids)

        loss = model.loss_function(logits, labels)
        avg_loss += loss
        if index % 100 == 0:
            print(f'loss at batch {index}: {loss:.4f}')
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        count = index
    avg_loss = avg_loss / count
    print(f'Average loss across epoch: {avg_loss}')

def resolved_path(fp: str) -> Path:
    return Path(fp).resolve()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Train a transformer model on a multi-label dataset')
    parser.add_argument('train_fp', help='File path to training dataset', type=resolved_path)
    parser.add_argument('dev_fp', help='File path to development dataset', type=resolved_path)
    parser.add_argument('test_fp', help='File path to test dataset', type=resolved_path)
    parser.add_argument('label_fp', help='File path to the labels file', type=resolved_path)
    parser.add_argument('save_fp', help='File path to save the trained model too', type=resolved_path)
    parser.add_argument('--cuda', help='Whether or not to use CUDA GPU device', 
                        action='store_true')
    parser.add_argument('--learning-rate', help='Learning rate', 
                        type=float, default=5e-5)
    parser.add_argument('--batch-size', help='Batch size', 
                        type=int, default=16)
    parser.add_argument('--transformer-model', help='Name of transformer model to use', 
                        type=str, default='bert-base-uncased')
    args = parser.parse_args()

    transformer_model_name = args.transformer_model
    tokenizer = AutoTokenizer.from_pretrained(transformer_model_name, use_fast=True)
    label_mapper, label_binarizer = label_mapper_binarizer(args.label_fp)
    custom_collate_fn = DataCollatorWithPadding(tokenizer, label_binarizer)
    batch_size = args.batch_size

    train_dataloader = DataLoader(EmotionsDataset(args.train_fp), 
                                  batch_size=batch_size, 
                                  shuffle=True,
                                  collate_fn=custom_collate_fn)
    dev_dataloader = DataLoader(EmotionsDataset(args.dev_fp),
                                batch_size=batch_size, 
                                collate_fn=custom_collate_fn)
    test_dataloader = DataLoader(EmotionsDataset(args.test_fp),
                                 batch_size=batch_size, 
                                 collate_fn=custom_collate_fn)

    number_labels = len(label_mapper)
    transformer_model = TransformerModel(transformer_model_name, number_labels)
    device = 'cpu'
    if args.cuda:
        device = 'cuda'
    
    transformer_model.to(device)
    optimizer = torch.optim.Adam(params=transformer_model.parameters(), 
                                 lr=args.learning_rate)
    import time
    t = time.time()
    train(transformer_model, train_dataloader, optimizer, device)
    print(f'Time to train the model for one epoch: {time.time() - t}')

    save_fp: Path = args.save_fp
    if not save_fp.parent.exists():
        save_fp.parent.mkdir(parents=True)
    t = time.time()
    torch.save(transformer_model, args.save_fp)
    print(f'Time to save model: {time.time() - t}')
