
# Design2GarmentCode: Programmatic Garment Patterns from Text and Images

[arXiv](https://arxiv.org/abs/2412.08603) | [Project Page](https://style3d.github.io/design2garmentcode/)

Feng Zhou, Ruiyang Liu, Chen Liu, Gaofeng He, Yong‑Lu Li, Xiaogang Jin, Huamin Wang. *CVPR 2025 .*

![teaser](assets/img/neural_symbolic-teaser.png)
 we propose a novel
sewing pattern generation approach Design2GarmentCode
based on Large Multimodal Models (LMMs), to generate parametric pattern-making programs from multi-modal
design concepts
---

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/your-org/design2garmentcode.git   # ← replace with the real URL
cd design2garmentcode
```

### 2. Create the Conda environment
An `environment.yml` file is provided in the project root with all required Conda and PyPI dependencies (Python 3.9.19, Torch 2.4.0 + CUDA 12.1, etc.).

```bash
conda env create -f environment.yml
conda activate d2g
python -m pip install --upgrade pip          # optional: upgrade pip
```

### 3. (Optional) Enable 3‑D simulation
If you need local cloth simulation and 3‑D visualization, follow the installation instructions for **GarmentCode Warp Simulator**:  
<https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode>

---
### 4. Language‑Model API
`Design2GarmentCode` communicates with large multimodal models.  
Follow the steps **in the given order**:

1. **Provide API credentials**  
   - **Environment variable (recommended)** – defaults to *ChatGPT‑4o*  
     ```bash
     export OPENAI_API_KEY="sk‑..."
     ```  
   - **Edit `system.json`** (project root) – manually specify `api_key`, `base_url`, and `model` if you prefer a file‑based approach.
2. **Download the required models**:  
   - First, download the base model [Qwen2-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct/tree/main).  
     Place the entire folder at:  
     `lmm_utils/Qwen/Qwen2-VL-2B-Instruct/`

   - Next, download the fine-tuned weights file [model.pth](lmm_utils/Qwen/qwen2vl_lora_mlp/model.pth),  
     and place it in:  
     `lmm_utils/Qwen/qwen2vl_lora_mlp/`
---

## Quick GUI Demo

```bash
python gui.py         
```
- Input: free‑form prompt or an image/sketch  
- Output: GarmentCode JSON, preview image, and (optionally) physics simulation
---
## Model Inference
### 1. Text Guided Generation

Use `test_text_batch.py` to process a list of text descriptions from a JSON file.

```bash
python lmm_utils/test_text_batch.py \
  --input assets/test_text/examples.json \
  --output assets/test_text_result \
  --sim 
```

- `--input`: Path to your input JSON file containing multiple garment description texts.
- `--output`: Directory where the output `.json` files will be saved.
- `--sim`: Enable or disable physical simulation output.
Supports physical simulation (enabled by default in script).

---

### 2. Image Guided Generation

Use `test_picture_batch.py` to process all image files in a directory.

```bash
python lmm_utils/test_picture_batch.py \
  --input assets/test_img/examples \
  --output assets/test_image_result/examples \
  --sim 
```
- `--input`: Folder containing multiple image files.
- `--output`: Output folder where results will be saved.
- `--sim`: Enable or disable physical simulation output.

---
### 3. Modify Patterns in the GUI
Once a pattern is generated in GUI, you can refine them directly inside the GUI:

1. Focus the **input box** at the bottom.  
2. Type `modify: <your-instruction>` .  
3. Press **Enter** – the system will regenerate the pattern to reflect your changes.


## Get 3D Garment Patterns
### 1. Generate from a pattern.json
After generating the pattern data, you can simulate the corresponding 3D output directly from the pattern's JSON file.
```bash
python test_garment_sim.py --pattern_spec $INPUT_JSON 
```
### 2. Generate from gui
You can also run the simulation directly on the GUI to obtain 3D data.
```bash
python gui.py 
```
### Citation
```bash
If you find this work useful, please cite:

```bibtex
@article{zhou2024design2garmentcode,
  title={Design2GarmentCode: Turning Design Concepts to Tangible Garments Through Program Synthesis},
  author={Zhou, Feng and Liu, Ruiyang and Liu, Chen and He, Gaofeng and Li, Yong-Lu and Jin, Xiaogang and Wang, Huamin},
  journal={arXiv preprint arXiv:2412.08603},
  year={2024}
}
```