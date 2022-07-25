# LibHip - A Hip Joint Finite Element Model Repository
<p align="center">
<img width="766" alt="Screenshot 2022-06-27 at 10 58 00" src="https://user-images.githubusercontent.com/45920627/175901433-17cbc32a-8565-4f9a-9172-bf5193370ed7.png">
</p>

LibHip is an open-access hip joint finite element model repository designed for simulation studies. Our repository consists of clinically verified subject-specific hip joint models along with the algorithms to reproduce them. 
The main features of the models are listed as below:
* 11 clinically verified subject-specific bilateral models covering the bones and cartilages in the hip joint area 
* Semi-automated modeling workflow using cutting-edge geometry processing tools
* A direct geometry processing cartilage reconstruction method using segmented bone models
* Multi-body volume mesh generation, resulting in high-quality discretization, conforming and congruent shared interfaces, and accurate geometries

## Modeling Flowchart and Research Data
<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/166197148-373c2553-6d1f-44c2-a4db-4168733bd6a2.png">
</p>

## Data Structure
This repository consists of the following sections:
- The [model repository](https://github.com/diku-dk/libhip/tree/main/model_repository) folder contains all the research data belonging to 11 subjects: the clinical images, the segmentation label maps, the multi-body surface and volume meshes, and the finite element models. Detailed explanation of each research data is provided in the related folder.

<p align="center">
<img width="813" alt="Screenshot 2022-07-24 at 22 08 36" src="https://user-images.githubusercontent.com/45920627/180664049-89446fcb-bfa9-465f-a108-3e9cd917eec0.png">
</p>




- The [src](https://github.com/diku-dk/libhip/tree/main/src), [notebooks](https://github.com/diku-dk/libhip/tree/main/notebooks), and the [config](https://github.com/diku-dk/libhip/tree/main/config) folders contain the codes that we used to create these models.
  - The `src` folder locates the source python functions of our modeling pipeline. These functions are called by the Jupyter notebooks in the *notebooks* folder.
  - The `notebooks` folder contains the preprocessing, cartilage generation, the volume mesh generation, and the simulation file generation codes.       These notebooks call the source codes from the *src* folder. 
  - The `config` folder contains the subject-specific configurations you need for each subject. These parameters are called by the files in the *notebooks* folder during the modeling pipeline.
  - Each time you run the Jupyter notebooks, the output of each step is stored in the `model generation` folder.

💡 Before running the Jupyter notebooks, please make sure to make the following empty folders in the `model generation` folder:`anatomical_info`, `cargen_output`, `ftet_output`, `json_output`, `preprocessing_output`, `simulation_output`, and `volgen_output`

##
Following, we explain our modeling pipeline step-by-step and guide you through the existing code and model folders:

### 0. Image Data
The input to our modeling workflow is the surface mesh of the bony structures. These models are based on CT scans obtained from the open-access [Cancer Imaging Archive](https://www.cancerimagingarchive.net). You can find the original images by browsing through the website, using the ID provided for each subject in the table below.

We have further cropped the CT scans to the hip joint area to minimize the computational load during segmentation and stored them in the NIFTI format. The cropped CT scans are located in the [ImageData](https://github.com/diku-dk/libhip/tree/main/model_repository/ImageData) folder.

<div align="center">
  
| Model | Sex | Age | Cancer Imaging Archive ID |
| --- | --- | --- | --- | 
|m1 | Male | 65 | TCGA-4Z-AA7M |
|m2 | Male | 64 | TCGA-4Z-AA7O |
|m3 | Male | 65 | TCGA-4Z-AA7S |
|m4 | Male | 56 | TCGA-4Z-AA7W |
|m5 | Male | 73 | TCGA-4Z-AA80 |
|m6 | Male | 62 | TCGA-4Z-AA84 |
|m7 | Male | 51 | 1.3.6.1.4.1.9328.50.4.0004 |
|m8 | Male | 50 | ABD_LYMPH_039 |
|m9 | Male | 60 | 1.3.6.1.4.1.9328.50.4.0002 |
|m10 | Male | 71 | 1.3.6.1.4.1.9328.50.4.0040 |
|m11 | Male | -- | 1.3.6.1.4.1.9328.50.4.0051 |

</div>

### 1. Bone Geometry Reconstruction
We obtain an explicit surface representation of all the bones using a semi-automated approach
implemented in the [3D slicer software package](https://www.slicer.org). The bone contours and the existing gaps in the inter-bone cavities are verified by our senior [consultant radiologist](https://research.regionh.dk/rigshospitalet/en/persons/michael-bachmann-nielsen(87d575e5-755e-4182-b94d-75776981fc21)/publications.html). 

The region of interest in these models includes the sacrum bone, the paired pelvic bones, and the paired femur bones. These segmentation masks can be found in the [LabelMap](https://github.com/diku-dk/libhip/tree/main/model_repository/LabelMaps) folder for each subject.

<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168824937-d35f5aa8-21a9-4cd1-9ee0-7f02f6d4ec70.png">
</p>

The initial [raw surface mesh](https://github.com/diku-dk/libhip/tree/main/model_repository/RawSegment) transferred from the bone label maps is typically dense and may have poor quality. Our [pre-processing code](https://github.com/diku-dk/libhip/blob/main/notebooks/0_PreProcessing.ipynb) cleans and re-meshes the surface meshes using mainly the [fTetWild](https://wildmeshing.github.io/ftetwild/) and [Libigl](https://libigl.github.io) libraries. You can find the cleaned and re-meshed models in the [CleanSegment](https://github.com/diku-dk/libhip/tree/main/model_repository/CleanSegment) folder for each subject.

<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168812343-6b0675fd-779b-4619-90cc-a7c4fce3881e.png">
</p>

### 2. Cartilage Geometry Reconstruction
We apply a specialized geometry processing method to generate subject-specific cartilages in the hip joint area. This method was initially introduced by [Moshfeghifar et al. [2022]](https://doi.org/10.48550/arXiv.2203.10667) to generate subject-specific hip joint cartilages independent of image modalities. 

Our [cartilage reconstruction code](https://github.com/diku-dk/libhip/blob/main/notebooks/1_CarGen.ipynb) adds new ideas to this algorithm to improve the hip joint results and extend this method to the paired sacroiliac joints and the pubic symphysis. The multi-body surface mesh of each subject, including the bone models and the cartilage surface meshes, are provided in the [CartiGen](https://github.com/diku-dk/libhip/tree/main/model_repository/CartiGen) folder.

<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168859866-32300557-0988-403d-b91a-c647826f97d7.png">
</p>

### 3. Multi-body Volume Mesh Generation
Using [fTetWild](https://wildmeshing.github.io/ftetwild/), we create volume mesh for all the sub-domains simultaneously, ensuring neither overlapping nor gaps in the interfaces. This method welds the interface nodes together in the meshing step, avoiding further contact definitions in the simulation setup.

Our [volume generation code](https://github.com/diku-dk/libhip/blob/main/notebooks/3_VolGen.ipynb) generates volume meshes inside and outside the model, filling a bounding box around the model. These tetrahedrons still have no inside/out classification. Thus, we apply a post-processing step to extract the interior volume of each object and filter out the elements that do not belong to any of the objects. 

<p align="center">
<img width="800" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168844422-39654fdb-5f2b-45d8-9ec0-aff3b1f2f562.png">
</p>

The output of the volume mesh generation, including the surface and volume mesh of each subject, is provided in the [SurfaceMesh](https://github.com/diku-dk/libhip/tree/main/model_repository/SurfaceMesh) and the [VolumeMesh](https://github.com/diku-dk/libhip/tree/main/model_repository/VolumeMesh) folders, respectively.

### 4. Finite Element Simulation
We demonstrate the performance of our models in different simulation setups and show that our models are compatible with different FE solvers. A pseudo-stance scenario under dynamic structural mechanics analysis is set up in the [FEBio](https://febio.org) and [PolyFEM](https://polyfem.github.io) solvers. We provide \num{11} FE model with two hip joint versions: with and without a gap between the articular cartilages. Since FEBio requires an initial slight penetration between the contact surfaces, we use the model versions with no gap in the hip joints. PolyFEM, in contrast, requires an initial configuration free of penetrations; thus, we use the model versions with a small gap between the articular cartilage layers.

Our [simulation generator code](https://github.com/diku-dk/libhip/blob/main/notebooks/4_SimGen.ipynb) generates an FEBio model file (`.feb`) automatically suitable for `FEBio Version3.0` . All the simulation files and results are located in the [Simulation](https://github.com/diku-dk/libhip/tree/main/model_repository/Simulation) folder.

## Installation
First, set up your conda environment for jupyter notebooks as below: 
```python
conda create -n libhip
conda activate libhip
conda config --add channels conda-forge
```
Next, install the following packages in the libhip environment:
```python
conda install igl
conda install meshplot 
conda install ipympl
conda install jupyter
conda install -c conda-forge matplotlib
conda install pandas
conda install -c conda-forge time
conda install -c conda-forge matplotlib
conda install -c conda-forge wildmeshing
```
Remember to activate your environment upon running the jupyter notebook: 
```python
conda activate libhip
jupyter notebook
```
Further, [install fTetWild](https://wildmeshing.github.io/ftetwild/) using CMake, [clone libisl](https://github.com/erleben/libisl.git), and install the [git lfs](https://git-lfs.github.com) on your machine beofre cloning the repository.
## Citation
Please cite this work by using this reference:

- Soon to be added due to the review process.

## Acknowledgement 
🌈 This project has received funding from the European Union’s Horizon 2020 research and innovation program under the Marie Sklodowska-Curie grant agreement No. 764644.
This repository only contains the [RAINBOW](https://rainbow.ku.dk) consortium’s views, and the Research Executive Agency and the Commission are not responsible for any use that may be made of the information it contains.

![Webp net-resizeimage](https://user-images.githubusercontent.com/45920627/132510734-41c835fc-2502-4461-b3fd-770668d43c9d.jpg)

🌟 This work was partially supported by the NSF CAREER award under Grant No. 1652515, the NSF grants OAC-1835712, OIA-1937043, CHS-1908767, CHS-1901091, NSERC DGECR-2021-00461, and RGPIN-2021-03707, a Sloan Fellowship, a gift from Adobe Research and a gift from Advanced Micro Devices, Inc. 
