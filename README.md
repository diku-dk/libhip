# LibHip - A Hip Joint Finite Element Model Repository.
![test4](https://user-images.githubusercontent.com/45920627/166197056-810cbb7b-5877-4e4e-ad98-5beecb1af18f.png)

## Model Features
* Open-access hip joint finite element model repository designed for simulation studies
* 11 clinically verified subject-specific bilateral models, covering the bones and cartilages in the hip joint area
* Open-access semi-automated modeling workflow using cutting-edge geometry processing tools
* A direct geometry processing cartilage reconstruction method using segmented bone models
* Multi-body volume mesh generation, resulting in high-quality discretization, conforming and congruent shared interfaces, and accurate geometries

## Modeling Workflow and Research Data
<img width="603" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/166197148-373c2553-6d1f-44c2-a4db-4168733bd6a2.png">

* The input to our modeling workflow, including the CT scans and bone label masks can be found at [image_data](https://github.com/diku-dk/libhip/tree/main/models/image_data) and [segmentation_labelmap](https://github.com/diku-dk/libhip/tree/main/models/segmentation_labelmap), respectively.
<!-- * The multi-body surface mesh of each subject, including the remeshed and cleaned bone models and cartilage surface meshes are provided in [cargen_output](/Users/nsv780/Documents/Github/libhip/model_generation/cargen_output). -->
* The output of the volume mesh generation including the surface and volume mesh ofeach subject is provided in [surface_mesh](http://localhost:8888/tree/Documents/Github/libhip/model_repository/surface_mesh) and [volume_mesh](http://localhost:8888/tree/Documents/Github/libhip/model_repository/volume_mesh), respectively.

## Installation
First, setup your conda environment for jupyter notebooks as below: 
```python
conda create -n libhip
conda activate libhip
conda config --add channels conda-forge
```
Next, install the following packages in the cargen enviroment:
```python
conda install igl
conda install meshplot 
conda install ipympl
conda install jupyter
```
Remember to activate your environment upon running the juyter notebook: 
```python
conda activate libhip
jupyter notebook
```

## Tutorial for running the code

- Step 1: xxx 
- Step 2: xxx 
- Step 3: xxx 
- Step 4: xxx 
- Step 5: xxx 

## Citation
Please cite this work by using this reference:

- Soon to be added due to review process.

## Acknowledgement 
❤️ We would like to thank the [Libigl](https://libigl.github.io) team, as the core of CarGen algorithm is based on the various functions available in the Libigl library.

❤️ This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie grant agreement No. 764644.
This repository only contains the [RAINBOW](https://rainbow.ku.dk) consortium’s views and the Research Executive Agency and the Commission are not responsible for any use that may be made of the information it contains.

![Webp net-resizeimage](https://user-images.githubusercontent.com/45920627/132510734-41c835fc-2502-4461-b3fd-770668d43c9d.jpg)


❤️ This work was partially supported by the NSF CAREER award under Grant No. 1652515, the NSF grants OAC-1835712, OIA-1937043, CHS-1908767, CHS-1901091, NSERC DGECR-2021-00461 and RGPIN-2021-03707, a Sloan Fellowship, a gift from Adobe Research and a gift from Advanced Micro Devices, Inc. 

❤️ We thank the NYU IT High Performance Computing for resources, services, and staff expertise.
