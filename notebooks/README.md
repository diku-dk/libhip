Here, we explain our modeling pipeline and guide you through the existing codes. We start from the methods which we use to reconstruct the anatomical structures. Next, we describe the volume mesh generation step and explain the steps to ensure high-quality meshes. Finally, we describe the FE setup we employ to test the quality of our models.

# Pre-processing of the input data
The input to our modeling workflow is the surface mesh of the bony structures. 
* The bone surface mesh is segmented directly from CT images. For more information about the images and the delineated label maps please checkout the [ImageData](https://github.com/diku-dk/libhip/tree/main/model_repository/ImageData) and the [LabelMap](https://github.com/diku-dk/libhip/tree/main/model_repository/LabelMaps) folders, respectively.
* The initial 3D representation of the bone labelmaps are stored in the [RawSegment](https://github.com/diku-dk/libhip/tree/main/model_repository/RawSegment) folder. These models are typically dense and may have poor qualities; Thus, we need to improve the quality and resize the triangles before using them for our pipeline.

The `0_PreProcessing.ipynb` code cleans and re-meshes the surface meshes and stores the output in the [preprocessing_output](https://github.com/diku-dk/libhip/tree/main/model_generation/preprocessing_output) folder. 

<p align="center">
<img width="800" alt="remeshing_tree" src = "https://user-images.githubusercontent.com/45920627/182364874-1bdbd277-8e99-4590-9349-c7d8a97132c8.png">
</p>

:bulb: You can find the cleaned and re-meshed bone models for all the subjects in the [CleanSegment](https://github.com/diku-dk/libhip/tree/main/model_repository/CleanSegment) folder.

<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168812343-6b0675fd-779b-4619-90cc-a7c4fce3881e.png">
</p>

# Cartilage Geometry Reconstruction
We apply a specialized geometry processing method to generate subject-specific cartilages in the hip joint area. This method was initially introduced by [Moshfeghifar et al. [2022]](https://doi.org/10.48550/arXiv.2203.10667) and we added new ideas to this algorithm to improve the hip joint results and extend this method to sacroiliac joints and pubic symphysis.

The `1_CarGen.ipynb` code generates single-piece cartilages for the sacroiliac joint and the pubic symphysis, filling the inter-bone cavity. The joint space in the hip joint is divided between the acetabular and the femoral layers, allocating roughly half of the joint space to each cartilage's thickness. Further, the average cartilage thickness and the bone coverage area are measured for the three joints. 

We want our models to be compatible with FE solvers with different approaches; Thus, we provide two versions of hip joint models for each subject : *with* and *without a gap* between the articular cartilages. 

Once you run this code, the outputs and teh cartilage anatomical measurements are stored in the [cargen_output](https://github.com/diku-dk/libhip/tree/main/model_generation/cargen_output) and the [anatomical_info](https://github.com/diku-dk/libhip/tree/main/model_generation/anatomical_info) folders, respectively.

<p align="center">
<img width="800" alt="cargen_tree" src = "https://user-images.githubusercontent.com/45920627/182378275-b46c97c3-af79-4dcf-9b7f-5af70f5572cf.png">
</p>

:bulb: You can find the cartilage and the underlying bone surface meshes for all the subjects in the [CartiGen](https://github.com/diku-dk/libhip/tree/main/model_repository/CartiGen) folder.

<p align="center">
<img width="700" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168859866-32300557-0988-403d-b91a-c647826f97d7.png">
</p>

# Bone anatomical measurements
The `2_BoneAnt.ipynb` code measures the bone anatomical measurements and saves the output in the [anatomical_info](https://github.com/diku-dk/libhip/tree/main/model_generation/anatomical_info) folder. In this jupyter notebook, we use the available modules in the [RAINBOW](https://github.com/diku-dk/RAINBOW) library to measure the hip joint center. Please remember to clone this library and then update the corresponding path to the **python** folder inside this code.

```python
sys.path.append (str(Path.home()/'Documents'/'Github'/'RAINBOW'/'python'))
```
<p align="center">
<img width="800" alt="bone_tree" src = "https://user-images.githubusercontent.com/45920627/182417305-4bd853f9-7dd6-4248-922a-b87b74ec9c5e.png">
</p>

:bulb: You can find the bone anatomical measurements for all the subjects in the [MorphoData](https://github.com/diku-dk/libhip/tree/main/model_repository/MorphoData) folder.

# Multi-body Volume Mesh Generation
The `3_VolGen.ipynb` code creates volume mesh for all the sub-domains simultaneously, ensuring neither overlapping nor gaps in the interfaces. This method welds the interface nodes together in the meshing step, avoiding further contact definitions in the simulation setup.

In the first step, we create a volume mesh inside and outside the model, filling a bounding box around the model. These tetrahedrons still have no inside/out classification. Next, we apply a post-processing step to extract the interior volume of each object and filter out the elements that do not belong to any of the objects. 

In this jupyter notebook, we use [fTetWild](https://wildmeshing.github.io/ftetwild/) to create the volume meshes. Please remember to install this library and then update the corresponding path to the **build** folder inside this code.

```python
ftetwild_dir = Path.home()/ 'Documents'/ 'Github'/ 'fTetWild'/ 'build'
```

Each time you run this code, the final multi-body volume mesh together with the extracted surface meshes are stored in the [volgen_output](https://github.com/diku-dk/libhip/tree/main/model_generation/volgen_output) folder. This code has several mid-outputs which the user will not need and they are stored in the [mid_outputs](https://github.com/diku-dk/libhip/tree/main/model_generation/mid_outputs) folder. 

<p align="center">
<img width="800" alt="Screenshot 2022-04-28 at 10 50 05" src="https://user-images.githubusercontent.com/45920627/168844422-39654fdb-5f2b-45d8-9ec0-aff3b1f2f562.png">
</p>

:bulb: The surface and volume mesh for all the subjects are provided in the [SurfaceMesh](https://github.com/diku-dk/libhip/tree/main/model_repository/SurfaceMesh) and the [VolumeMesh](https://github.com/diku-dk/libhip/tree/main/model_repository/VolumeMesh) folders, respectively.





# Finite Element Simulation
We demonstrate the performance of our models in different simulation setups and show that our models are compatible with different FE solvers. A pseudo-stance scenario under dynamic structural mechanics analysis is set up in the [FEBio](https://febio.org) and [PolyFEM](https://polyfem.github.io) solvers. 

We provide 11 FE model with two hip joint versions: with and without a gap between the articular cartilages. Since FEBio requires an initial slight penetration between the contact surfaces, we use the model versions with no gap in the hip joints. PolyFEM, in contrast, requires an initial configuration free of penetrations; thus, we use the model versions with a small gap between the articular cartilage layers.

The `4_SimGen.ipynb` code generates an FEBio model file (`.feb`) automatically suitable for `FEBio Version3.0` . Each time you run the code, the output foles are stored in the [simulation_output](https://github.com/diku-dk/libhip/tree/main/model_generation/simulation_output) folder.  All the simulation files and results are located in the [Simulation](https://github.com/diku-dk/libhip/tree/main/model_repository/Simulation) folder.
