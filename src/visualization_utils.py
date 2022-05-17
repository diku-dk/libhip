import numpy as np
import igl
import meshplot as mp
import matplotlib.pyplot as plt
import math

# mp.offline()
" Colors and Eye-candies"

# color definitions
pastel_light_blue = np.array([179, 205, 226]) / 255.
pastel_blue = np.array([102, 179, 230]) / 255.
bone = np.array([0.92, 0.90, 0.85])
pastel_orange = np.array([255, 126, 35]) / 255.
pastel_yellow = np.array([241, 214, 145]) / 255.
pastel_green = np.array([102, 230, 153])/255.
green = np.array([128, 174, 128]) / 255.
blue = np.array([111, 184, 210]) / 255.
sweet_pink = np.array([0.9, 0.4, 0.45])  #230, 102, 115
rib = np.array([253, 232, 158]) / 255.
skin = np.array([242, 209, 177]) / 255.
chest = np.array([188, 95, 76]) / 255.


# Meshplot settings
sh_true = {'wireframe': True, 'flat': True, 'side': 'FrontSide', 'reflectivity': 0.1, 'metalness': 0}
sh_false = {'wireframe': False, 'flat': True, 'side': 'FrontSide', 'reflectivity': 0.1, 'metalness': 0}

from ipywidgets import interact, interactive, fixed, interact_manual
def renwder (vertices, faces, colors, camera_position, camera_quat, light_settings) :

    frame = mp.plot  ( vertices, faces, c = colors, shading = { 'wireframe' : False, 'wire_width' : 0.00000001,
                                                                'wire_color': 'black', 'width' : 1200,
                                                                'height' : 720, 'colormap' :'jet' } )
    for m in meshes:
        frame.add_mesh(v=m[0], f=m[1], c=np.array([.92, .9, .85]), shading={'flat':True, 'side': 'FrontSide', 'reflectivity': 0.1, 'metalness': 0})

    frame._scene.children[0].position   = camera_position
    frame._scene.children[0].quaternion = camera_quat

    interact(update_light, x=(-2000, 2000), y=(-4000, 4000), z=(-2000, 10000), intesity=(0, 1.0, 0.01), frame=fixed(frame))

    frame._scene.children[0].children[0].position  = ( light_settings[0], light_settings[1], light_settings[2] )
    frame._scene.children[0].children[0].intensity = light_settings[3]


def update_light(x=0, y=0, z=0, intensity=0.6, frame=None):

        current_position = frame._scene.children[0].children[0].position

        update = (current_position[0] + x, current_position[1] + y, current_position[2] + z)

        print("Camera pos:", frame._scene.children[0].position,
              ", Camera rot:", frame._scene.children[0].quaternion)

        frame._scene.children[0].children[0].position = (x, y, z)
        frame._scene.children[0].children[0].intensity = intensity

        frame._scene.exec_three_obj_method('update')


# camera_pos = ( -0.5612357999401881, 706.7391948567785, -620.4622757920592 )
# camera_rot = ( 0.007326719680403353, 0.7144338544707698, 0.6996246202961217, -0.0074818072864300976 )

# frame = mp.plot  ( s1_vertices, s1_faces, c = cargen.bone, shading = cargen.sh_false )
# frame.add_mesh ( s2_vertices, s2_faces, c = cargen.bone, shading = cargen.sh_false )
# frame.add_mesh ( s3_vertices, s3_faces, c = cargen.bone, shading = cargen.sh_false )
# frame.add_mesh ( s4_vertices, s4_faces, c = cargen.bone, shading = cargen.sh_false )
# frame.add_mesh ( s5_vertices, s5_faces, c = cargen.bone, shading = cargen.sh_false )

# frame._scene.children[0].position   = camera_pos
# frame._scene.children[0].quaternion = camera_rot

# interact(update_light, x=(-2000, 2000), y=(-4000, 4000), z=(-2000, 10000), intesity=(0, 1.0, 0.01), frame=fixed(frame))

# light_settings  = ( 927, -130, 2030, 0.6 )
# frame._scene.children[0].children[0].position  = ( light_settings[0], light_settings[1], light_settings[2] )
# frame._scene.children[0].children[0].intensity = light_settings[3]


# # interact(update_light, x=(-2000, 2000), y=(-4000, 4000), z=(-2000, 10000), intesity=(0, 1.0, 0.01), frame=fixed(frame))

# # frame._scene.children[0].children[0].position  = ( light_settings[0], light_settings[1], light_settings[2] )
# # frame._scene.children[0].children[0].intensity = light_settings[3]
# # frame._scene.children[0].position = camera_pos
# # frame._scene.children[0].quaternion = camera_rot


