# LibHip - A Hip Joint Finite Element Model Repository

![teaser](https://user-images.githubusercontent.com/45920627/180701601-8415f976-7371-4429-b9e8-281d793dc5c2.png)

LibHip is an open-access hip joint finite element model repository designed for simulation studies. Our repository consists of clinically verified subject-specific hip joint models along with the algorithms to reproduce them. 
The main features of the models are listed as below:
* 11 clinically verified subject-specific bilateral models covering the bones and cartilages in the hip joint area 
* Semi-automated modeling workflow using cutting-edge geometry processing tools
* A direct geometry processing cartilage reconstruction method using segmented bone models
* Multi-body volume mesh generation, resulting in high-quality discretization, conforming and congruent shared interfaces, and accurate geometries

## Data Structure
The [model_repository](https://github.com/diku-dk/libhip/tree/main/model_repository) folder contains all the research data belonging to 11 subjects: the clinical images, the segmentation label maps, the multi-body surface and volume meshes, and the finite element models. Detailed explanation of each research data is provided in the related folder.

<p align="center">
<img width="813" alt="Screenshot 2022-07-24 at 22 08 36" src="https://user-images.githubusercontent.com/45920627/180664049-89446fcb-bfa9-465f-a108-3e9cd917eec0.png">
</p>

## Modeling Flowchart and Pipeline
<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/166197148-373c2553-6d1f-44c2-a4db-4168733bd6a2.png">
</p>

The [src](https://github.com/diku-dk/libhip/tree/main/src), [notebooks](https://github.com/diku-dk/libhip/tree/main/notebooks), and the [config](https://github.com/diku-dk/libhip/tree/main/config) folders contain the codes that we used to create these models.
  - The `src` folder locates the source python functions of our modeling pipeline. These functions are called by the Jupyter notebooks in the *notebooks* folder.
  - The `notebooks` folder contains the preprocessing, cartilage generation, the volume mesh generation, and the simulation file generation codes.       These notebooks call the source codes from the *src* folder. 
  - The `config` folder contains the subject-specific configurations you need for each subject. These parameters are called by the files in the *notebooks* folder during the modeling pipeline.
  - Each time you run the Jupyter notebooks, the output of each step is stored in the [model_generation](https://github.com/diku-dk/libhip/tree/main/model_generation) folder.

## Installation
Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and [Git LFS](https://git-lfs.com/) first. Git LFS is required to download the model data rather than pointer files. Then clone the repository:
```bash
git lfs install
git clone https://github.com/diku-dk/libhip.git
cd libhip
git lfs pull
```
Create the local `.venv` from the committed lockfile:
```bash
uv sync --locked
```
The project uses Python 3.13 by default (`.python-version`) and supports Python 3.12–3.13. uv downloads the interpreter when needed. The former Conda environment export has been replaced by direct dependencies in `pyproject.toml` and exact resolved versions in `uv.lock`; Conda activation is no longer needed.

Launch Jupyter from the repository root:
```bash
uv run --locked jupyter notebook
```
Open the notebooks in `notebooks/` in numerical order and select the **Python 3 (ipykernel)** kernel from this environment. For an editor, select `.venv/bin/python` (Windows: `.venv\Scripts\python.exe`).

Meshplot is installed from a pinned upstream Git commit because it is not published on PyPI. Its plotting dependencies are declared explicitly. The `libigl` distribution supplies the `igl` Python module. Native wheel availability varies by platform; the environment is verified on Apple Silicon macOS.

Two tools remain external to the Python environment:

- [fTetWild](https://wildmeshing.github.io/ftetwild/): build the `FloatTetwild_bin` executable using CMake, then set `ftetwild_dir` in `3_VolGen.ipynb`. The Python `wildmeshing` dependency handles preprocessing but does not replace this CSG executable.
- [RAINBOW](https://github.com/diku-dk/RAINBOW): clone it and set `rainbow_dir` to the directory containing its `rainbow` package in `2_BoneAnt.ipynb`. This is the geometry library used by the notebook, not the unrelated PyPI package named `rainbow`.

To verify the Python environment:

```bash
uv run --locked pytest
uv pip check
```

To update dependencies, edit their constraints in `pyproject.toml` as needed, then run:

```bash
uv lock --upgrade
uv sync --locked
uv run --locked pytest
```

Commit `pyproject.toml`, `.python-version`, and `uv.lock` together. Meshplot's source revision must be updated explicitly. The smoke tests exercise the installed geometry APIs and notebook rendering setup; subject-specific reconstruction and FEBio simulations still require the model data and external tools.

The current Meshplot release emits upstream Traitlets deprecation warnings. Wildmeshing 0.4.1 intermittently stalled inside its native Delaunay tetrahedralizer on both Python versions during validation, including with an irregular mesh. The native check is therefore opt-in and fails after a 60-second subprocess timeout:

```bash
uv run --locked pytest -m native
```

The regular smoke suite excludes this check. Production remeshing calls are not time-limited by the test safeguard; this dependency migration does not resolve the upstream native stall.
## Citation
Please cite this work by using this reference:
```bash
@article{moshfeghifar226libhip,
  title={LibHip: An open-access hip joint model repository suitable for finite element method simulation},
  author={Moshfeghifar, Faezeh and Gholamalizadeh, Torkan and Ferguson, Zachary and Schneider, Teseo and Nielsen, Michael Bachmann and Panozzo, Daniele and Darkner, Sune and Erleben, Kenny},
  journal={Computer methods and programs in biomedicine},
  volume={226},
  pages={107140}
}
```
## Acknowledgement 
🌈 This project has received funding from the European Union’s Horizon 2020 research and innovation program under the Marie Sklodowska-Curie grant agreement No. 764644.
This repository only contains the [RAINBOW](https://rainbow.ku.dk) consortium’s views, and the Research Executive Agency and the Commission are not responsible for any use that may be made of the information it contains.

![Webp net-resizeimage](https://user-images.githubusercontent.com/45920627/132510734-41c835fc-2502-4461-b3fd-770668d43c9d.jpg)

🌟 This work was partially supported by the NSF CAREER award under Grant No. 1652515, the NSF grants OAC-1835712, OIA-1937043, CHS-1908767, CHS-1901091, NSERC DGECR-2021-00461, and RGPIN-2021-03707, a Sloan Fellowship, a gift from Adobe Research and a gift from Advanced Micro Devices, Inc. 
