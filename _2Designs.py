import fullcontrol as fc
from fullcontrol.gcode import ManualGcode
import FCJSS as jss
from _2Winder import *
import _2Winder  

def ARC_DEMO():  # just to test arcs
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = False

    _2Winder.hmtl_filename = 'hmtl/2_Arc_demo'
    _2Winder.gcode_filename = 'gcode/2_Arc_demo'
    _2Winder.gcode_filename_SD = 'D:/2_Arc_demo'

    steps = []

    jss.move_in_line(steps, 0, 0, 0, VF)  # first point
    jss.arc(steps, 0, 0, 0, 5, 90, 15, 100, F)
    
    # jss.move_in_line(steps, 10, 10, 0, VF)  # first point
    # x, y, z = jss.move_in_line(steps, 20, 10, 0, VF)
    # x, y, z = jss.arc(steps, x, y, z, 5, -45, 90, 20, M)
    # x, y, z = jss.move_in_line(steps, x, y, z+10, VF)
    # jss.arc(steps, x, y, z, 5, 45, -90, 20, M)

    VISUALIZE_AND_COMPILE(steps, _2Winder.animate)

def MISS_NAILS():  # test clearance between cores
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = True

    _2Winder.hmtl_filename = 'hmtl/MISS_NAILS'
    _2Winder.gcode_filename = 'gcode/MISS_NAILS'
    _2Winder.gcode_filename_SD = 'D:/MISS_NAILS'

    steps = []
    
    x, y, _ = jss.move_in_line(steps, 0, 0, 0, VF)  # first point
    _, _, z = jss.move_in_line(steps, x, y, h+5, VF)  # up
    jss.move_in_line(steps, *datum, z, VF)  # to datum
    x, y, z = jss.move_in_line(steps, *datum, h, M)  # touch grid top
    jss.pause(steps, 10)

    x, y, z = jss.move_in_line(steps, x, y, z+2*p, VS)  # move just off the grid

    # Between nails in x
    x, y, z = jss.move_in_line(steps, x, y+en-nn/2, z, VS)  # to below nail row
    dist = w
    for i in range(1,6):
        x, y, z = jss.move_in_line(steps, x+dist, y, z, VS)  # move accross
        if i == 5: break
        x, y, z = jss.move_in_line(steps, x, y+nn, z, VS)  # move accross
        dist *= -1

    # Between nails in y
    x, y, z = jss.move_in_line(steps, x-en+nn/2, y, z, VS)  # to column outside
    x, y, z = jss.move_in_line(steps, x, y+en-nn/2, z, VS)  # to edge
    dist = w
    for i in range(1,6):
        dist *= -1
        x, y, z = jss.move_in_line(steps, x, y+dist, z, VS)  # move accross
        if i == 5: break
        x, y, z = jss.move_in_line(steps, x-nn, y, z, VS)  # move accross

    VISUALIZE_AND_COMPILE(steps, _2Winder.animate, frame_step=1)

def SLOT_TEST():  # this is a clearance path test for the new 4x4 grid
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = True

    _2Winder.hmtl_filename = 'hmtl/2_Slot_test'
    _2Winder.gcode_filename = 'gcode/2_Slot_test'
    _2Winder.gcode_filename_SD = 'D:/2_Slot_test'

    steps = []

    x, y, _ = jss.move_in_line(steps, 0, 0, 0, F)  # first point
    _, _, z = jss.move_in_line(steps, x, y, h+5, F)  # up
    jss.move_in_line(steps, *datum, z, F)  # to datum
    jss.pause(steps, 2)
    jss.move_in_line(steps, *datum, h, F)  # touch grid top
    x, y = datum
    y += en + nn/2
    jss.move_in_line(steps, x, y, h+p*2, F)  # move up to first nail
    jss.pause(steps, 2)

    first = 1
    last = 16
    for core in range(first, last+1):
        x, y, z = plunge_slot(steps, core)
        if core == 16:
            x, y, z = jss.move_in_line(steps, x, y, z+10, F)  # move up and end
            break
        if core % 4 == 0:
            x, y, z = jss.move_in_line(steps, x+r, y, z, VF)  # position between rows
            jss.move_in_line(steps, x, y+nn, z, VF)  # increase y between rows of cores


    VISUALIZE_AND_COMPILE(steps, _2Winder.animate, frame_step=1)
    
def WIND_TEST_4x4():  # this winds the EM Chores a few times and moves around the fingers/webbing to test the webbing
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = True

    _2Winder.hmtl_filename = 'hmtl/2_Wind_Test_4x4'
    _2Winder.gcode_filename = 'gcode/2_Wind_Test_4x4'
    _2Winder.gcode_filename_SD = 'D:/2_Wind_Test_4x4'

    steps = []

    x, y, _ = jss.move_in_line(steps, 0, 0, 0, F)  # first point
    _, _, z = jss.move_in_line(steps, x, y, h+5, F)  # up
    jss.move_in_line(steps, *datum, z, F)  # to datum
    jss.pause(steps, 2)
    jss.move_in_line(steps, *datum, h, F)  # touch grid top
    x, y = datum
    y += en + nn/2
    jss.move_in_line(steps, x, y, h+p*2, F)  # move up to first nail and just off grid surface
    jss.pause(steps, 10)

    z_between = h + 10
    first = 1
    last = 2
    for core in range(first, last+1):
        rotation = 'ccw' if core % 2 == 0 else 'cw'
        plunge_slot(steps, core)
        _, final_pos = wind_chore(steps, core, 'x+', rotation)
        if core == 16:
            x, y, z = jss.move_in_line(steps, final_pos[0], final_pos[1], z+10, F)  # move up and end
            break
        if core % 4 == 0: 
            x, y, z = jss.move_in_line(steps, final_pos[0]+r, final_pos[1], z, VF)  # position between rows
            jss.move_in_line(steps, x, y, z_between, S)  # increase z between cores
            jss.move_in_line(steps, x, y+nn, z_between, S)  # increase y between rows of cores
        else:
            jss.move_in_line(steps, final_pos[0], final_pos[1], z_between, S)  # increase z between cores
        
    VISUALIZE_AND_COMPILE(steps, _2Winder.animate, frame_step=2)

def FULL_4x4():  # full wind to test board when it is ready
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = True

    _2Winder.hmtl_filename = 'hmtl/2_Full_4x4'
    _2Winder.gcode_filename = 'gcode/2_Full_4x4'
    _2Winder.gcode_filename_SD = 'D:/2_Full_4x4'

    steps = []

    x, y, _ = jss.move_in_line(steps, 0, 0, 0, F)  # first point
    _, _, z = jss.move_in_line(steps, x, y, h+5, F)  # up
    jss.move_in_line(steps, *datum, z, F)  # to datum
    jss.pause(steps, 2)
    jss.move_in_line(steps, *datum, h, F)  # touch grid top
    x, y = datum
    y += en + nn/2
    jss.move_in_line(steps, x, y, h+p*2, F)  # move up to first nail and just off grid surface
    jss.pause(steps, 30)

    first = 1
    last = 4
    for core in range(first, last+1):
        rotation = 'ccw' if core % 2 == 0 else 'cw'
        plunge_slot(steps, core)
        _, final_pos = wind_chore(steps, core, 'x+', rotation)
        if core == last:
            x, y, z = jss.move_in_line(steps, final_pos[0], final_pos[1], z+10, F)  # move up and end
            break
        if core % 4 == 0: 
            x, y, z = jss.move_in_line(steps, final_pos[0]+r, final_pos[1], final_pos[2], VF)  # position between rows
            jss.move_in_line(steps, x, y+nn, final_pos[2], S)  # increase y between rows of cores
        
    VISUALIZE_AND_COMPILE(steps, _2Winder.animate, frame_step=2)

# -------------------- MAIN --------------------

if __name__ == '__main__':
    
    # ARC_DEMO()
    # MISS_NAILS()  # WORKED!!
    # SLOT_TEST()  # WORKED!!
    # WIND_TEST_4x4()  # SEEMED TO WORK!!
    FULL_4x4()