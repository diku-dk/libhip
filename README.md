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
First, clone this repository to your local directory and go into that folder. Below, is an example of how to clone this repository using the command line:
```python
git clone https://github.com/diku-dk/libhip.git
cd libhip
```
Next, create a conda environment named `libhip`, using the channel `conda-forge` and the list of packages in the `requirements.txt` file: 
```python
conda create --name libhip -c conda-forge --file requirements.txt 
```
Finally, activate your environment and run the jupyter notebook: 
```python
conda activate libhip
jupyter notebook
```
Further, [install fTetWild](https://wildmeshing.github.io/ftetwild/) using CMake, [clone libisl](https://github.com/erleben/libisl.git), and install the [git lfs](https://git-lfs.github.com) on your machine.
## Citation
Please cite this work by using this reference:

- Soon to be added due to the review process.

## Acknowledgement 
🌈 This project has received funding from the European Union’s Horizon 2020 research and innovation program under the Marie Sklodowska-Curie grant agreement No. 764644.
This repository only contains the [RAINBOW](https://rainbow.ku.dk) consortium’s views, and the Research Executive Agency and the Commission are not responsible for any use that may be made of the information it contains.

![Webp net-resizeimage](https://user-images.githubusercontent.com/45920627/132510734-41c835fc-2502-4461-b3fd-770668d43c9d.jpg)

🌟 This work was partially supported by the NSF CAREER award under Grant No. 1652515, the NSF grants OAC-1835712, OIA-1937043, CHS-1908767, CHS-1901091, NSERC DGECR-2021-00461, and RGPIN-2021-03707, a Sloan Fellowship, a gift from Adobe Research and a gift from Advanced Micro Devices, Inc. 
