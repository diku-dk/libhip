# LibHip - A Hip Joint Finite Element Model Repository
![test4](https://user-images.githubusercontent.com/45920627/166197056-810cbb7b-5877-4e4e-ad98-5beecb1af18f.png)

## Model Features
* Open-access hip joint finite element model repository designed for simulation studies
* 11 clinically verified subject-specific bilateral models, covering the bones and cartilages in the hip joint area
* Open-access semi-automated modeling workflow using cutting-edge geometry processing tools
* A direct geometry processing cartilage reconstruction method using segmented bone models
* Multi-body volume mesh generation, resulting in high-quality discretization, conforming and congruent shared interfaces, and accurate geometries

## Modeling Flowchart and Research Data
<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/166197148-373c2553-6d1f-44c2-a4db-4168733bd6a2.png">
</p>

## Data Structure
This repository consists of five main sections:
- The [model repository](https://github.com/diku-dk/libhip/tree/main/model_repository) folder contains all the research data belonging to 11 subjects: the clinical images, the segmentation label maps, the milti-body surface and volume meshes, and the finite element models.
- The [src](https://github.com/diku-dk/libhip/tree/main/src), [notebooks](https://github.com/diku-dk/libhip/tree/main/notebooks), and the [config](https://github.com/diku-dk/libhip/tree/main/config) folders contain the codes that we used to create these models.
  - The `src` folder locates the source python functions of our modeling pipeline. These functions are called by the Jupyter notebooks in the *notebooks* folder.
  - The `notebooks` folder contains the preprocessing, the cartilage generation, the volume mesh generation, and the simulation file generation codes.       These notebooks call the source codes from the *src* folder. 
  - The `config` folder contains the subject-specific configurations which you need for each subject. These parameters are called by the files in the *notebooks* folder during the modeling pipeline.

##
Following we explain the our modeling pipeline and guid you through the existing codes and model folders:

### 0. Image Data
The input to our modeling workflow is the surface mesh of the bony structures. These models are based on CT scans obtained from the open-access [Cancer Imaging Archive](https://www.cancerimagingarchive.net). You can find the original images by browsing through the website, using the ID provided for each subject in the table below.

We further crop the CT scans to the hip joint area to minimize the computational load during segmentation and stored them in the NIFTI format. The cropped CT scans are located in the [image_data](https://github.com/diku-dk/libhip/tree/main/models/image_data) folder.

<div align="center">
  
| Model | Sex | Age | Cancer Imaging Archive ID |
| --- | --- | --- | --- | 
|m1 | Male | 65 | TCGA-4Z-AA7M |
|m2 | Male | 64 | TCGA-4Z-AA7O |
|m3 | Male | 65 | TCGA-4Z-AA7S |
|m4 | Male | 56 | TCGA-4Z-AA7W |
|m5 | Male | 73 | TCGA-4Z-AA80 |
|m6 | Male | 62 | TCGA-4Z-AA84 |
|m7 | Male | 51 | 1.3.6.1.4.1.9328.50.4.4.0004 |
|m8 | Male | 50 | ABD_LYMPH_039 |
|m9 | Male | 60 | 1.3.6.1.4.1.9328.50.4.4.0002 |
|m10 | Male | 71 | 1.3.6.1.4.1.9328.50.4.4.0040 |
|m11 | Male | -- | 1.3.6.1.4.1.9328.50.4.4.0051 |

</div>

### 1. Bone Geometry Reconstruction
We obtain an explicit surface representation of all the bones using a semi-automated approach
implemented in the [3D slicer software package](https://www.slicer.org). The bone contours and the existing gaps in the inter-bone cavities are verified by our senior [consultant radiologist](https://research.regionh.dk/rigshospitalet/en/persons/michael-bachmann-nielsen(87d575e5-755e-4182-b94d-75776981fc21)/publications.html). 

The region of interest in these models include the sacrum bone, the paired hip bones, and the paired femur bones. These segmentation masks can be found in the [segmentation_labelmap](https://github.com/diku-dk/libhip/tree/main/models/segmentation_labelmap) folder for each subject.

<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168824937-d35f5aa8-21a9-4cd1-9ee0-7f02f6d4ec70.png">
</p>

The initial [raw surface mesh](https://github.com/diku-dk/libhip/tree/main/model_repository/slicer_raw_output) transferred from the bone label maps are typically dense and may have poor quality. Our [pre-processing code](https://github.com/diku-dk/libhip/blob/main/notebooks/0_PreProcessing.ipynb) cleans and remeshes the surface meshes using mainly the [fTetWild](https://wildmeshing.github.io/ftetwild/) and [Libigl](https://libigl.github.io) libraries. You can find the cleaned and remeshed models in the [preprocessing_output](https://github.com/diku-dk/libhip/tree/main/model_repository/slicer_raw_output) folder for each subject.

<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168812343-6b0675fd-779b-4619-90cc-a7c4fce3881e.png">
</p>

### 2. Cartilage Geometry Reconstruction
We apply a specialized geometry processing method to generate subject-specific cartilages in the hip joint area. This method was initially introduced by [Moshfeghifar et al. [2022]](https://doi.org/10.48550/arXiv.2203.10667) to generate subject-specific hip joint cartilages independent of image modalities. 

Our [cartilage reconstruction code](https://github.com/diku-dk/libhip/blob/main/notebooks/1_CarGen.ipynb) adds new ideas to this algorithm to improve the hip joint results and extend this method to the paired sacroiliac joints and the pubic symphysis. The multi-body surface mesh of each subject, including the bone models and cartilage surface meshes are provided in [cargen_output](/Users/nsv780/Documents/Github/libhip/model_generation/cargen_output) folder.

<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168859866-32300557-0988-403d-b91a-c647826f97d7.png">
</p>

### 3. Multi-body Volume Mesh Generation
Using [fTetWild](https://wildmeshing.github.io/ftetwild/), we create volume mesh for all the sub-domains simultaneously, ensuring neither overlapping nor gaps in the interfaces. This method welds the interface nodes together in the meshing step, avoiding further contact definitions in the simulation setup.

Our [volume generation code](https://github.com/diku-dk/libhip/blob/main/notebooks/2_VolGen.ipynb) generates volume meshes inside and outside the model, filling a bounding box around the model. These tetrahedrons still have no inside/out classification. Thus, we apply a post-processing step to extract the interior volume of each object and filter out the elements that do not belong to any of the objects. 

<p align="center">
<img width="800" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168844422-39654fdb-5f2b-45d8-9ec0-aff3b1f2f562.png">
</p>

The output of the volume mesh generation including the surface and volume mesh of each subject is provided in [surface_mesh](http://localhost:8888/tree/Documents/Github/libhip/model_repository/surface_mesh) and [volume_mesh](http://localhost:8888/tree/Documents/Github/libhip/model_repository/volume_mesh), respectively. We deliver two mesh densities for each subject: *fine* and *coarse* meshes. The reason is to show that our pipeline can provide different mesh resolutions depending on the users’ computational resources.

### 4. Finite Element Simulation
We use two different finite element solvers to to run simulations. We demonstrate the usability of our models with the off-the-shelves [FEBio solver](https://febio.org), and we study the importance of bilateral modeling in the hip joint area using [PolyFEM](https://polyfem.github.io). 

Our [simulation generator code](https://github.com/diku-dk/libhip/blob/main/notebooks/3_SimGen.ipynb), generates `.feb` files automatically which can be run in FEBio 3. All the simulation files and the simulation results are located in the [finite element](https://github.com/diku-dk/libhip/tree/main/model_repository/finite_element) folder.

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

## Citation
Please cite this work by using this reference:

- Soon to be added due to review process.

## Acknowledgement 
- We would like to thank the [Libigl](https://libigl.github.io) team, as the core of LibHip algorithm is based on the various functions available in the Libigl library.

🌈 This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie grant agreement No. 764644.
This repository only contains the [RAINBOW](https://rainbow.ku.dk) consortium’s views and the Research Executive Agency and the Commission are not responsible for any use that may be made of the information it contains.

![Webp net-resizeimage](https://user-images.githubusercontent.com/45920627/132510734-41c835fc-2502-4461-b3fd-770668d43c9d.jpg)


- This work was partially supported by the NSF CAREER award under Grant No. 1652515, the NSF grants OAC-1835712, OIA-1937043, CHS-1908767, CHS-1901091, NSERC DGECR-2021-00461 and RGPIN-2021-03707, a Sloan Fellowship, a gift from Adobe Research and a gift from Advanced Micro Devices, Inc. 

- We thank the NYU IT High Performance Computing for resources, services, and staff expertise.




<!-- |m1 | Male | 65 | GE LightSpeed VCT | [0.85, 0.85, 1.25]  | 365x221x291 | TCGA-4Z-AA7M|
|m2 | Male | 64 | GE LightSpeed VCT| [0.78, 0.78, 1.25] |  394x215x257|TCGA-4Z-AA7O |
|m3 | Male | 65 | Siemens Emotion 6|  [0.82, 0.82, 2.5]|  378x199x244| TCGA-4Z-AA7S|
|m4 | Male | 56 | GE LightSpeed VCT| [0.90, 0.90, 1.25] | 362x184x236 |TCGA-4Z-AA7W |
|m5 | Male | 73 | GE LightSpeed VCT|  [0.87, 0.87, 1.25]| 389x226x265 |TCGA-4Z-AA80 |
|m6 | Male | 62 | Siemens Emotion 6|  [0.69, 0.69, 2.5]| 436x256x206 |TCGA-4Z-AA84 |
|m7 | Male | 51 | Siemens Sensation 64| [0.78, 0.78, 1.00] | 405x232x250 | 1.3.6.1.4.1.9328.50.4.4.0004 |
|m8 | Male | 50 | N.A| [0.97, 0.97, -] | 399x250x290 | ABD_LYMPH_039 |
|m9 | Male | 60 | Siemens Sensation 64| [0.78, 0.78, 1.00] | 427x254x318 | 1.3.6.1.4.1.9328.50.4.4.0002 |
|m10 | Male | 71 | Siemens Sensation 16 | [0.80, 0.80, 1.00] | 400x285x289 | 1.3.6.1.4.1.9328.50.4.4.0040 |
|m11 | Male | N.A | Siemens Sensation 16 | [0.82, 0.82, 1.00] | 404x230x283 | 1.3.6.1.4.1.9328.50.4.4.0051 | -->
