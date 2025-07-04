
# Design2GarmentCode: Turning Design Concepts to Tangible Garments Through Program Synthesis

[![arXiv](https://img.shields.io/badge/📃-arXiv%20-red.svg)](https://arxiv.org/abs/2412.08603)
[![webpage](https://img.shields.io/badge/🌐-Website%20-blue.svg)](https://style3d.github.io/design2garmentcode/) 
[![Youtube](https://img.shields.io/badge/📽️-Video%20-orchid.svg)](https://www.youtube.com/xxx)

<span class="author-block"><a href="">Feng Zhou</a>,&nbsp;</span>
<span class="author-block"><a href="https://walnut-ree.github.io/">Ruiyang Liu</a>,&nbsp;</span>
<span class="author-block"><a href="">Chen Liu</a>,&nbsp;</span>
<span class="author-block"><a href="">Gaofeng He</a>,&nbsp;</span>
<span class="author-block"><a href="https://dirtyharrylyl.github.io/">Yong-Lu Li</a>,&nbsp;</span>
<span class="author-block"><a href="http://www.cad.zju.edu.cn/home/jin/">Xiaogang Jin</a>,&nbsp;</span>
<span class="author-block"><a href="https://wanghmin.github.io/">Huamin Wang</a></span>

<p align="center">
  <img src="https://github.com/Style3D/design2garmentcode-impl/raw/main/assets/img/neural_symbolic-pipeline.png">
</p>
Official implementation for Design2GarmentCode, a motility-agnostic sewing pattern generation framework that leverages fine-tuned Large Multimodal Models to generate parametric pattern-making programs from multi-modal design concepts.


## Installation
### 1. Clone the repository
```bash
git clone https://github.com/Style3D/design2garmentcode-impl.git
cd design2garmentcode-impl
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

#### 1. **Provide API credentials for MMUA**  
- **Environment variable (recommended)** – defaults to *ChatGPT‑4o*  
     ```bash
     export OPENAI_API_KEY="sk‑..."
     ```  
- **Edit `system.json`** (project root) – manually specify `api_key`, `base_url`, and `model` if you prefer a file‑based approach.

#### 2. **Set up the parameter projector**:  
- Download the base model [Qwen2-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct/tree/main) and place the modal to `lmm_utils/Qwen/Qwen2-VL-2B-Instruct/`.

- Download the fine-tuned weights file from [Google Drive](https://drive.google.com/file/d/1CL7OLUq6fYcwoDuLRkBxtKNxJ0_G73U-/view?usp=sharing), and place it in `lmm_utils/Qwen/qwen2vl_lora_mlp/`.
---

## Testing with GUI

Setting up the GUI with `python gui.py` where you will see the following interface (modified from GarmentCode)

<p align="center">
  <img src="https://github.com/Style3D/design2garmentcode-impl/raw/main/assets/img/gui_example.png">
</p>

Switching to the `PARSE DESIGN` tab, and input your design input, either text description, photograph or sketch, to the chatbox. The generated sewing pattern will appear on the right side after parsing.

Once a pattern is generated, you can modify the result by typing `modify: <your-instruction>` in the chatbox.

---
## Batch Inference
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

## Simulate 3D Garment
### 1. Generate from a pattern.json
After generating the pattern data, you can simulate the corresponding 3D output directly from the pattern's JSON file with
```bash
python test_garment_sim.py --pattern_spec $INPUT_JSON 
```
Or run the simulation directly in the `3D View` GUI tab.

### Citation
```bash
If you find this work useful, please cite:

```bibtex
@article{zhou2024design2garmentcode,
  title={Design2GarmentCode: Turning Design Concepts to Tangible Garments Through Program Synthesis},
  author={Zhou, Feng and Liu, Ruiyang and Liu, Chen and He, Gaofeng and Li, Yong-Lu and Jin, Xiaogang and Wang, Huamin},
  booktitle={Proceedings of the Computer Vision and Pattern Recognition Conference},
  year={2025}
}
```