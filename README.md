# USD Scene Generator

This project provides a modular Python-based toolkit for creating, customizing, and exporting OpenUSD (`.usda`) scenes using [Pixar's openUSD](https://graphics.pixar.com/usd/docs/index.html). It is designed for procedural scene generation with support for geometry, camera placement, environment lighting, and materials.

---

## 📁 Project Structure

```
openUSD_Scene_Generator/
├── assets/                # assets like hdri images for env lighting
├── blender/               # blender python scripts for batch rendering generated usd scenes with AOVs
├── core/                  # modularized openUSD scene generator
├── outputs/               # output directory for usd scene files, rendered images and metadata
├── scripts/               # python scripts for testing scene generator
├── environment.yml        # Conda environment definition (via Miniforge3)
├── LICENSE                # Project license
└── README.md              # This file
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ritmps/usd-scene-generator.git
cd usd-scene-generator
```

### 2. Create and Activate Environment

Recommend using **Miniforge3**:

```bash
conda env create -f environment.yml
conda activate usd
```

Make sure openUSD is built and installed with python bindings: https://github.com/PixarAnimationStudios/OpenUSD


### 3. Open Project in VSCode

```bash
code .
```

### 4. Run Example Scene

```bash
python .\scripts\basic_scene.py
```

This will generate a test USD scene at

```bash
.\outputs\scenes\test_scene.usda
```

You can view it with 

```bash
 usdview .\outputs\scenes\test_scene.usda
```

Use help flag to see advanced options like change to a different renderer, select a view camera and etc.

### 5. Render the scene

```bash
 usdrecord .\outputs\scenes\test_scene.usda .\outputs\renders\beauty.exr
```

Use help flag to see advanced options like change to a different renderer, select camera and etc.

## 📝 Current State of this Branch

This branch is not actively maintained and may not function as expected.

