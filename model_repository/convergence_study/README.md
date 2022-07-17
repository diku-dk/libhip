# Mesh Convergence Study
We perform a mesh convergence analysis to obtain the optimal mesh size for the models with respect to multiple approaches. First, we investigare the effect of different mesh sizes on the simulation output. Next, we study the effect of the order of the tetrahedral elements on the simulation output. 

These experiment further show that our modeling pipeline can re-generate different mesh resolutions with minimal manual effort. The simulation results of all these finite element models converge correctly with no issues related to mesh properties. Therefore, one can generate finer/coarser versions based on their specific problem.
## 1 - Mesh convergence with respect to the mesh resolution
In this method we study the effect of mesh resolution on the simulation results. The von mises stress pattern and value are estimated as the relative output in two specific zones: 
 * The top part of the femoral cartilage
 * The center of the femoral head
### Data Structure
We generate seven different set of mesh resolutions of the [subject m1](https://github.com/diku-dk/libhip/tree/main/model_repository/cargen_output/m1) as stated in the Table below. We change the mesh resolution by tweaking the **envelope of size epsilon** and **the ideal edge legnth (l)** parameters of [fTetWild](https://wildmeshing.github.io/ftetwild/).

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

### Simulation Setup
The same simulation setup explained in **Experiment A** in Section 3.8 of the manuscript is then applied to all these mesh resolutions. A pseudo-stance scenario under dynamic structural mechanics analysis is setup the von Mises stress is calculated as the direct simulation output.  The pelvic girdle is fixed in the x,y, and z-direction and we push the femur bones toward the pelvic girdle in the z-direction. The femur bones have restricted displacement and rotation in the x and y-direction and we apply a load equal to the bodyweight to the distal end of the femoral bones. This load starts from zero and increases linearly to 430 N on each femur. An augmented surface contact algorithm with friction-less tangential interaction is applied between the articular interfaces allowing unhindered motion in the hip joint.

It should be noted that the stress value in the femoral cartilage is not a proper measure for the classical mesh convergence, as the stress value estimations are a consequence of sliding forces in a non-smooth contact problem. In this case, many other parameters, such as the sliding contact and the dynamic setup, can affect the output results. Therefore, we only focus on the stress pattern in this zone. 

<p align="center">
<img width="350" alt="Screenshot 2022-07-17 at 11 05 07" src="https://user-images.githubusercontent.com/45920627/179391566-4139d630-46ef-4687-a123-b69870b2a582.png">
</p>

### Results
The stress pattern is consistent to a certain level in the optimal mesh size. The stress value in the femoral head converges with less than $2\%$ residual mesh error.

<div align="center">
 
| Model set | simulation time | left stress (MPa) | right stress (MPa)| Left %Change | % Right %Change | 
| --- | --- | --- | --- |--- |--- | 
|Res_1 |  0:01:13 | 0.267 | 0.207 | 13.67 | 15.94 |
|Res_2 | 0:02:11 | 0.240 | 0.228 | 3.75  | 5.26  |
|Res_3 | 0:02:34 | 0.229 | 0.255 | 0.88  | 5.88  |
|Res_4 | 0:02:54 | 0.249 | 0.255 | 7.23  | 5.88  |
|**Res_5**|**0:04:44**|**0.226**|**0.235**|**2.21**|**2.13**|
|Res_6 |0:13:37 | 0.239 | 0.234 |1.28|2.56|
|Res_7 |0:40:21 | 0.231 | 0.240 |0|0|
 
</div>


## Mesh convergence w.r.t the **order** of the elements
This experiment aims to show how PolyFEM can use multiple element orders in a multi-body domain. In some cases, this help to have more accurate results by only increasing the order of the elements in thin domains. We assigned **Tet4, Tet10, Tet20** elements to the cartilage tissue, and ran the same simulation setup explained in **Experiment B** in Section 3.8 of the manuscript. 



    




<!-- <div align="center">

| Model | elapsed time | left | right | both |Left percentage of change|Right percentage of change|Both percentage of change both|
| --- | --- | --- | --- |--- |--- |--- |--- |
|Res_1 | 0:01:52 | 0.227 | 0.217 | 0.222 |1.77|10.60|6.31|
|Res_2 | 0:02:11 | 0.240 | 0.228 | 0.234 |3.75|5.26|0.85|
|Res_3 | 0:02:34 | 0.229 | 0.255 | 0.242 |0.88|5.88|2.48|
|Res_4 | 0:02:54 | 0.249 | 0.255 | 0.252 |7.23|5.88|6.35|
|Res_5 | 0:04:44 | 0.226 | 0.235 | 0.230 |2.21|2.13|2.61|
|Res_6 | 0:13:37 | 0.239 | 0.234 | 0.236 |1.28|2.56|0|
|Res_7 | 0:40:21 | 0.231 | 0.240 | 0.236 |0|0|0|

</div>
 -->
 
