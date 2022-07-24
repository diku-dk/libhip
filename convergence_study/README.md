# Mesh Convergence Study
We perform a mesh convergence analysis to obtain the optimal mesh resolution and the corresponding meshing parameters. The meshing parameters for other subjects are then calibrated to produce similar mesh properties as the optimal mesh settings. 
 
## Data Structure
We generate seven different set of mesh resolutions of the [subject m1](https://github.com/diku-dk/libhip/tree/main/model_repository/CartiGen/m1) as stated in the Table below. We change the mesh resolution by tweaking the **envelope of size epsilon** and **the ideal edge legnth (l)** parameters of [fTetWild](https://wildmeshing.github.io/ftetwild/).

<div align="center">
 
| Model set | epsilon | l-girdle| l-legs |elements| 
| --- | --- | --- | --- |--- |
|Res_1 | 0.0009  | 0.041 | 0.037 | 100K | 
|Res_2 | 0.00075 | 0.034 | 0.024 | 128K | 
|Res_3 | 0.00065 | 0.030 | 0.021 | 162K | 
|Res_4 | 0.00055 | 0.022 | 0.018 | 193K | 
|Res_5 | 0.0005  | 0.015 | 0.012 | 336K |
|Res_6 | 0.0005  | 0.009 | 0.009 | 718K |
|Res_7 | 0.0005  | 0.008 | 0.007 | 1.2M |
 
</div>

## Simulation Setup
The same simulation setup explained in **experiment A** in Section 3.8 of the manuscript is then applied to all these mesh resolutions. The von mises stress pattern and value are estimated as the relative output in two specific zones: 
 * The stress value in the femoral head center
 * The stress distribution pattern in the femoral cartilage

A pseudo-stance scenario under *dynamic* structural mechanics analysis is set up in [FEBio](https://febio.org). Since FEBio requires an initial slight penetration between the contact surfaces, we use the model versions with no gap in the hip joints to build the simulation files. We fix the pelvic girdle by restricting the sacrum's displacement and rotation in the x,y, and z-direction. The distal end of each femoral bone is tied to a rigid body. This rigid body has a force applied in the z-direction and is restricted in the other directions. The rigid force starts from zero and increases linearly to 430N on each femur. The articular interfaces in the hip joints are selected as the contact surfaces, and an augmented surface contact algorithm with friction-less tangential interaction is applied between them.

<p align="center">
<img alt="Screenshot 2022-07-24 at 18 08 08" src="https://user-images.githubusercontent.com/45920627/180656143-66edec29-5300-47f2-906f-01accc955278.png">
</p>

## Stress value in the femoral head center
In each mesh resolution, the von Mises stress is calculated for the left and right femoral head centers. The relative percentage change of the output to the highest resolution (Res_7) is considered the convergence criterion. As seen in the Table, the percentage change decreases for both the left and right sides and decreases as the mesh resolution increases and converges with less than 3% residual mesh error after **Res_5**. 

<div align="center">
 
| Model set | simulation time | left stress (MPa) | right stress (MPa)| Left %Change | Right %Change | 
| --- | --- | --- | --- |--- |--- | 
|Res_1 |  0:01:24 | 0.267 | 0.207 | 13.67 | 15.94 |
|Res_2 | 0:02:11 | 0.240 | 0.228 | 3.75  | 5.26  |
|Res_3 | 0:02:34 | 0.229 | 0.255 | 0.88  | 5.88  |
|Res_4 | 0:02:54 | 0.249 | 0.255 | 7.23  | 5.88  |
|**Res_5**|**0:04:44**|**0.226**|**0.235**|**2.21**|**2.13**|
|Res_6 |0:13:37 | 0.239 | 0.234 |1.28|2.56|
|Res_7 |0:56:52 | 0.231 | 0.240 |0|0|

</div>

## Stress distribution pattern in the femoral cartilage
The figure below illustrates the stress distribution pattern in the femoral head cartilage. It should be noted that observing the stress value in the femoral cartilage is a difficult approach for a mesh convergence study when non-smooth contract is involved. The stress values we observe depend both on the sliding forces in a non-smooth contact problem and mesh resolution. In this case, many other parameters, such as the sliding contact and the dynamic setup, can affect the output results. Therefore, we only focus on the stress pattern in this zone. The stress pattern varies and then gets consistent to a certain level after **Res5**.

<p align="center">
<img alt="Screenshot 2022-07-17 at 11 05 07" src="https://user-images.githubusercontent.com/45920627/179405020-32dd1c3a-4228-4384-85dd-65756ddd934b.png">
</p>

#
Besides convergence, this experiment shows that our modeling pipeline can re-generate different mesh resolutions with minimal manual effort. The simulation results of all these finite element models converge correctly with no issues related to mesh properties. Therefore, one can generate finer/coarser versions based on the users’ computational resources.


