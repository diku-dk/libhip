# Image Data

The input to our modeling workflow is the surface mesh of the bony structures. These models are based on CT scans obtained from the open-access [Cancer Imaging Archive](https://www.cancerimagingarchive.net). The subjects are in a supine position during the image acquisition, which is the closest to an *unloaded* joint state. We chose 11 subjects of the same gender and age range, with no reported disease related to the hip joint, the slightest rotation in the body, high image resolution, and minimum image noise.
 
You can find the original images by browsing through the website, using the ID provided for each subject in the table below. 

<div align="center">
  
| Model | Sex | Age | Cancer Imaging Archive ID | Matrix size before crop (pixels)|Matrix size after crop (pixels)
| --- | --- | --- | --- | --- |--- | 
|m1 | Male | 65 | TCGA-4Z-AA7M |521×521×663|365×221×291
|m2 | Male | 64 | TCGA-4Z-AA7O |521×521×613|394×215×257
|m3 | Male | 65 | TCGA-4Z-AA7S |521×521×475|378×199×244
|m4 | Male | 56 | TCGA-4Z-AA7W |521×521×455|362×184×236
|m5 | Male | 73 | TCGA-4Z-AA80 |521×521×468|389×226×265
|m6 | Male | 62 | TCGA-4Z-AA84 |521×521×388|436×256×206
|m7 | Male | 51 | 1.3.6.1.4.1.9328.50.4.0004 |521×521×520|405×232×250
|m8 | Male | 50 | ABD_LYMPH_039 |521×521×717|399×250×290
|m9 | Male | 60 | 1.3.6.1.4.1.9328.50.4.0002 |521×521×617|427×254×318
|m10 | Male | 71 | 1.3.6.1.4.1.9328.50.4.0040 |521×521×524|400×285×289
|m11 | Male | -- | 1.3.6.1.4.1.9328.50.4.0051 |521×521×603|404×230×283

</div>

We have further cropped the CT scans to the hip joint area to minimize the computational load during segmentation and stored them in the NIFTI format as: `m*_image_cropped.nii`. You can load these images using [3D Slicer](https://www.slicer.org)

![Screenshot 2022-07-24 at 18 27 22](https://user-images.githubusercontent.com/45920627/180656858-83c4954b-33b3-4eb0-8715-cfd2fa5dc8c1.png)

