import argparse

from transformers import PreTrainedTokenizerBase, AutoTokenizer, AutoModel

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads the transformer model and tokenizer')
    parser.add_argument('--transformer-model', help='Name of transformer model to use', 
                        type=str, default='bert-base-uncased')
    args = parser.parse_args()
    
    # Download the transformer model and it's tokenizer
    transformer_model_name = args.transformer_model
    AutoTokenizer.from_pretrained(transformer_model_name, use_fast=True)
    AutoModel.from_pretrained(transformer_model_name)