import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig
from peft import PeftModel, PeftConfig
import torch
from datasets import Dataset
from modelscope import snapshot_download, AutoTokenizer
from qwen_vl_utils import process_vision_info
from peft import LoraConfig, TaskType, get_peft_model, PeftModel
from transformers import (
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
    # Qwen2VLForConditionalGeneration,
    AutoProcessor,
    PreTrainedModel
)
from lmm_utils.Qwen.qwen2vl_lora_mlp.qwen2vl_modify_modeling_qwen2_vl import Qwen2VLForConditionalGeneration
import json
# Qwen2VLForConditionalGeneration
class LoRAWithMLP(nn.Module):
    def __init__(self, base_model_name, mlp_hidden_size=512, num_mlp_layers=2,device='cuda:0'):
        super().__init__()
        self.device=device
        self.base_model = Qwen2VLForConditionalGeneration.from_pretrained("./lmm_utils/Qwen/Qwen2-VL-2B-Instruct/", device_map=device,
                                                                torch_dtype=torch.bfloat16, trust_remote_code=True, )
        self.base_model.enable_input_require_grads()  # This method is performed when gradient checkpoints are turned on
        config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            # target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            inference_mode=False,  # Training mode
            r=64,
            lora_alpha=16,
            lora_dropout=0.05,
            bias="none",
        )
        # Get the LoRA model
        self.lora_model = get_peft_model(self.base_model, config)
        mlp_layers = []
        input_dim = self.lora_model.config.hidden_size  # Inherit large model hidden_size
        for _ in range(num_mlp_layers):
            mlp_layers.append(nn.Linear(input_dim, mlp_hidden_size,dtype=torch.bfloat16))
            mlp_layers.append(nn.ReLU())
            input_dim = mlp_hidden_size
        mlp_layers.append(nn.Linear(mlp_hidden_size, 123,dtype=torch.bfloat16))  #Output size = hidden_size
        self.mlp = nn.Sequential(*mlp_layers)

    def forward(self, input_ids=None,
        attention_mask=None,
        inputs_embeds=None,
        labels=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
        task_ids=None,
        **kwargs,):
        # Calculate the output of the large model after LoRA adaptation

        lora_output = self.lora_model(input_ids=input_ids,attention_mask=attention_mask,inputs_embeds=inputs_embeds,labels=None,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            task_ids=task_ids,
            )

        # Calculate the output of MLP additional processing
        mlp_output = self.mlp(lora_output.hidden_states[:,-1])

        return mlp_output  # Let MLP adjust the output of LoRA


    def save_checkpoint(self, path,epoch,optimizer,scheduler,best_valid_loss,avg_train_loss):
        filtered_dict = {name: param for name, param in self.state_dict().items() if
                         'base_model' not in name or 'lora' in name}
        checkpoint_dict = {
            'epoch': epoch,
            'model_state_dict': filtered_dict,
            'optimizer_state_dict': optimizer.state_dict(),
            'best_valid_loss': best_valid_loss,
            'avg_train_loss': avg_train_loss,
            "scheduler_state_dict":scheduler.state_dict(),
        }
        torch.save(checkpoint_dict, path)
    def load_checkpoint(self, path, optimizer,scheduler, device):
        """
        Load the checkpoint and restore the model and optimizer state
        :p aram model: The model that needs to be restored
        :p aram optimizer: The optimizer that needs to be restored
        :p aram path: checkpoint file path
        :p aram device: Runtime device (default GPU)
        :return: epoch of training, best validation loss, training loss
        """
        checkpoint = torch.load(path, map_location=device,optimizer=None,) # Load checkpoint

        self.load_state_dict(checkpoint['model_state_dict'], strict=False)  # Load the model parameters
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])  # Load optimizer parameters
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        epoch = checkpoint.get('epoch', 0)  # Get the epoch
        best_valid_loss = checkpoint.get('best_valid_loss', float('inf')) # Get the best verification loss
        avg_train_loss = checkpoint.get('avg_train_loss', float('inf'))  # Get the average training loss

        return epoch, best_valid_loss

    def save_weights(self, path):
        """ Only LoRA + MLP weights are saved, and the original Qwen2VL model is not included """
        # for name, param in self.state_dict().items():
        #     print(name, param.requires_grad)
        filtered_dict = {name: param for name, param in self.state_dict().items() if 'base_model' not in name or 'lora' in name}
        torch.save(filtered_dict, path)
        # torch.save(self.state_dict(), path)

    def load_weights(self, path):
        """ Load LoRA + MLP weights (need to initialize the model first) """
        state_dict = torch.load(path, map_location=self.device)
        self.load_state_dict(state_dict, strict=False)  # strict=False Some layers are allowed to be missing
