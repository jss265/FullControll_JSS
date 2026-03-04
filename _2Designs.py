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

def SLOT_TEST():  # this is a clearance path test for the new 4x4 grid
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = False

    _2Winder.hmtl_filename = 'hmtl/2_Slot_test'
    _2Winder.gcode_filename = 'gcode/2_Slot_test'
    _2Winder.gcode_filename_SD = 'D:/2_Slot_test'

    steps = []

    x, y, _ = jss.move_in_line(steps, 0, 0, 0, F)  # first point
    _, _, z = jss.move_in_line(steps, x, y, h+5, F)  # up
    jss.move_in_line(steps, *datum, z, F)  # to datum
    jss.move_in_line(steps, *datum, h, F)  # touch grid top
    x, y = datum
    y += en + nn/2
    jss.move_in_line(steps, x, y, h+p*2, F)  # move up to first nail
    jss.pause(steps, 10)

    z_between = h + 10
    first = 1
    last = 5
    for core in range(first, last+1):
        plunge_slot(steps, core)
        _, final_pos = wind_chore(steps, core, 'x+')
        jss.move_in_line(steps, final_pos[0], final_pos[1], z_between, S)
        

    VISUALIZE_AND_COMPILE(steps, _2Winder.animate, frame_step=1)
    
def WIND_TEST_4x4():  # this winds the EM Chores a few times and moves around the fingers/webbing to test the webbing
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = False

    _2Winder.hmtl_filename = 'hmtl/2_Wind_Test_4x4'
    _2Winder.gcode_filename = 'gcode/2_Wind_Test_4x4'
    _2Winder.gcode_filename_SD = 'D:/2_Wind_Test_4x4'

    steps = []

    jss.move_in_line(steps, 0, 0, 0, VF)  # first point

    VISUALIZE_AND_COMPILE(steps, _2Winder.animate)

def FULL_4x4():  # full wind to test board when it is ready
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = False

    _2Winder.hmtl_filename = 'hmtl/2_Full_4x4'
    _2Winder.gcode_filename = 'gcode/2_Full_4x4'
    _2Winder.gcode_filename_SD = 'D:/2_Full_4x4'

    steps = []

    jss.move_in_line(steps, 0, 0, 0, VF)  # first point

    VISUALIZE_AND_COMPILE(steps, _2Winder.animate)

# -------------------- MAIN --------------------

if __name__ == '__main__':
    
    # ARC_DEMO()
    SLOT_TEST()
    # WIND_TEST_4x4()
    # FULL_4x4()