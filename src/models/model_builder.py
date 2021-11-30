
import torch
import torch.nn as nn
from pytorch_pretrained_bert import BertModel, BertConfig
from torch.nn.init import xavier_uniform_
# KoBert -> transformers, ETRI -> pretrained_bert
# from transformers import BertModel, BertConfig

from models.encoder import TransformerInterEncoder, Classifier, RNNEncoder
from models.optimizers import Optimizer


def build_optim(args, model, checkpoint):
    """ Build optimizer """
    saved_optimizer_state_dict = None

    if args.train_from != '':
        optim = checkpoint['optim']
        saved_optimizer_state_dict = optim.optimizer.state_dict()
    else:
        optim = Optimizer(
            args.optim, args.lr, args.max_grad_norm,
            beta1=args.beta1, beta2=args.beta2,
            decay_method=args.decay_method,
            warmup_steps=args.warmup_steps)

    optim.set_parameters(list(model.named_parameters()))

    if args.train_from != '':
        optim.optimizer.load_state_dict(saved_optimizer_state_dict)
        if args.visible_gpus != '-1':
            for state in optim.optimizer.state.values():
                for k, v in state.items():
                    if torch.is_tensor(v):
                        state[k] = v.cuda()

        if (optim.method == 'adam') and (len(optim.optimizer.state) < 1):
            raise RuntimeError(
                "Error: loaded Adam optimizer from existing model" +
                " but optimizer state is empty")

    return optim


class Bert(nn.Module):
    def __init__(self, args, load_pretrained_bert, bert_config):
        super(Bert, self).__init__()
        if(load_pretrained_bert):
            if(args.bert_model_type=='kobert'):
                self.model = BertModel.from_pretrained("monologg/kobert")
            elif(args.bert_model_type=='etri'):
                self.model = BertModel.from_pretrained(args.bert_model)
        else:
            self.model = BertModel(bert_config)

    def forward(self, x, segs, mask):
        # pytorch-pretrained-bert
        encoded_layers, _ = self.model(x, segs, attention_mask =mask)
        top_vec = encoded_layers[-1]
        
        # transformers
        # top_vec, _ = self.model(x, token_type_ids=segs, attention_mask=mask)
        return top_vec



class Summarizer(nn.Module):
    def __init__(self, args, device, load_pretrained_bert = False, bert_config = None):
        super(Summarizer, self).__init__()
        self.args = args
        self.device = device
        if(args.bert_model_type=='kobert'):
            bert_config = BertConfig(8002, hidden_size=args.hidden_size,
                                    num_hidden_layers=args.inter_layers, num_attention_heads=args.heads, intermediate_size=args.ff_size)
            self.bert_config = bert_config
            self.bert = Bert(args, load_pretrained_bert=True, bert_config=self.bert_config)
        elif(args.bert_model_type=='etri'):
            self.bert = Bert(args, load_pretrained_bert=True, bert_config=BertConfig.from_json_file(args.bert_config_path))
            self.bert_config = BertConfig.from_json_file(args.bert_config_path)
        if (args.encoder == 'classifier'):
            self.encoder = Classifier(self.bert_config.hidden_size)
        elif(args.encoder=='transformer'):
            self.encoder = TransformerInterEncoder(self.bert_config.hidden_size, args.ff_size, args.heads,
                                                   args.dropout, args.inter_layers)
        elif(args.encoder=='rnn'):
            self.encoder = RNNEncoder(bidirectional=True, num_layers=1,
                                      input_size=self.bert_config.hidden_size, hidden_size=args.rnn_size,
                                      dropout=args.dropout)
        elif (args.encoder == 'baseline'):
            bert_config = BertConfig(self.bert_config.vocab_size, hidden_size=args.hidden_size,
                                     num_hidden_layers=6, num_attention_heads=8, intermediate_size=args.ff_size)
            self.bert.model = BertModel(bert_config)
            self.encoder = Classifier(self.bert_config.hidden_size)

        if args.param_init != 0.0:
            for p in self.encoder.parameters():
                p.data.uniform_(-args.param_init, args.param_init)
        if args.param_init_glorot:
            for p in self.encoder.parameters():
                if p.dim() > 1:
                    xavier_uniform_(p)

        self.to(device)
    def load_cp(self, pt):
        self.load_state_dict(pt['model'], strict=True)

    def forward(self, x, segs, clss, mask, mask_cls, sentence_range=None):

        top_vec = self.bert(x, segs, mask)
        sents_vec = top_vec[torch.arange(top_vec.size(0)).unsqueeze(1), clss]
        sents_vec = sents_vec * mask_cls[:, :, None].float()
        sent_scores = self.encoder(sents_vec, mask_cls).squeeze(-1)
        return sent_scores, mask_cls
