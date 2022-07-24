# Segmentation label map
We obtain an explicit surface representation of all the bones using a semi-automated approach implemented in the [3D slicer](https://slicer.org) software package. 
This method entails initial region labelling and contouring, followed by manual refinements to ensure accurate 3D approximations with no rough surfaces, holes, or connected tissues. 
In all subjects, the segmentation label maps essentially detail the shape and boundaries of the bones and identify the inter-bone cavities in the joint areas.

The label maps are provided in NIfTI file format for each subject. Each `m*-label map.nii` includes 2D segmentation masks as below:
* Green: the label map for the **right femur**
* Yellow: the label map for the **left femur** 
* Brown: the label map for the **right pelvis**
* Blue: the label map for the **left pelvis**
* Red: the label map for the **sacrum** 

A senior consultant radiologist has verified these bone segmentation. The clinical expert initially scrolls through all the segmented slices in each subject and verifies
the bone contours and the existing gaps in the inter-bone cavities. Then, he verifies the anatomical shape and smoothness of the reconstructed 3D surfaces. This procedure justifies the validation of our method in obtaining precise geometries.

![Screenshot 2022-07-19 at 19 59 37](https://user-images.githubusercontent.com/45920627/179818776-217a6c9f-d8df-4e89-95b6-623a1b42efbf.png)
