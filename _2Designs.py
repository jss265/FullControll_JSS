import fullcontrol as fc
from fullcontrol.gcode import ManualGcode
import FCJSS as jss
from _2Winder import *
import _2Winder  

def FINGERS_TEST():
    _2Winder.output_html = True
    _2Winder.animate = False
    _2Winder.output_gcode_to_file = True
    _2Winder.output_gcode_to_microSD = False

    _2Winder.hmtl_filename = 'hmtl/2_Fingers_test'
    _2Winder.gcode_filename = 'gcode/2_Fingers_test'
    _2Winder.gcode_filename_SD = 'D:/2_Fingers_test'

    steps = []

    jss.move_in_line(steps, 10, 10, 0, VF)  # first point
    x, y, z = jss.move_in_line(steps, 20, 10, 0, VF)
    x, y, z = jss.arc(steps, x, y, z, 5, -45, 90, 20, M)
    x, y, z = jss.move_in_line(steps, x, y, z+10, VF)
    jss.arc(steps, x, y, z, 5, 45, -90, 20, M)

    VISUALIZE_AND_COMPILE(steps, _2Winder.animate)

# -------------------- MAIN --------------------

if __name__ == '__main__':
    
    FINGERS_TEST()