The bone anatomical measurements are as below:

* **Hip joint center (HJC)** & **simplified femoral head radius (SR)**: we fit a sphere to the femoral head and choose the center and radius of this sphere as the hip joint center and the simplified femoral head radius, respectively. To minimize the bias from manual fitting, we use a least-squares method for spherical fit; 
* **Actual femoral head surface mesh (AR)**: the distance from the HJC to the femoral head surface mesh; 
* **Visible femur length (VFL)**:  the length of the line connecting the most proximal point of the femur to the mid-point of the most distal part of the same bone;
* **Neck-shaft angle (NSA)**: measures the angle between the neck and shaft axes. We first extract the centerline of the femoral bone geometry using the VMTK extension in the 3D slicer software package. Then, we apply a least-squares Linear Regression method to find the best fitting lines to the neck and shaft part of the centerline. The angle between these two lines shows the NSA;
* **Width of the pelvis (PW)**: the distance between the most lateral point of the pelvic bones to the femoral head center;
* **Inter-hip separation (IHS)**: the distance between the paired hip joint centers; 
* **Height of ilium (IH)**: the vertical distance between the most superior part of the pelvic bones and the hip joint center; 
* **Width of ilium (IW)**: the horizontal distance between the hip joint center and the most lateral point of the pelvic bones;

<p align="center">
<img width="600" alt="bone_ant" src="https://user-images.githubusercontent.com/45920627/182394952-2a371d4b-2cab-4834-b833-8997ead09466.png">
</p>
