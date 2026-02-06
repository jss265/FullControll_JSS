import fullcontrol as fc
from fullcontrol.gcode import ManualGcode
import FCJSS as jss
from Winder import *
import Winder  

def FINGERS_TEST():
    Winder.output_html = True
    Winder.output_gcode_to_file = True
    Winder.output_gcode_to_microSD = True
    Winder.hmtl_filename = 'hmtl/Finger_Test'
    Winder.gcode_filename = 'gcode/Finger_Test'
    Winder.gcode_filename_SD = 'D:/Finger_Test'

    steps = []

    jss.move_in_line(steps, 0,0,0,VF)  # first move
    jss.move_in_line(steps, 0,0,h+5,VF)  # clearance
    jss.move_in_line(steps, *datum, h, VF)  # over to origin
    jss.custom_line(steps, 'G4 S10')  # Pause to visually verify that nozzle is in the right place

    for finger_num in range(1,17):
        wrap_around_finger(steps, finger_num)

    jss.move_in_line(steps, *datum, h+me, VF)

    jss.custom_line(steps, 'G4 S10')  # pause for satisfaction

    VISUALIZE_AND_COMPILE(steps)

def WIND_1_THRU_4():
    Winder.output_html = True
    Winder.output_gcode_to_file = True
    Winder.output_gcode_to_microSD = True
    Winder.hmtl_filename = 'hmtl/Wind_1-4'
    Winder.gcode_filename = 'gcode/Wind_1-4'
    Winder.gcode_filename_SD = 'D:/Wind_1-4'

    steps = []

    jss.move_in_line(steps, 0,0,0,VF)  # first move
    jss.move_in_line(steps, 0,0,h+5,VF)  # clearance
    jss.move_in_line(steps, *datum, h, VF)  # over to origin
    jss.custom_line(steps, 'G4 S4')  # Pause to visually verify that nozzle is in the right place

    jss.move_in_line(steps, *datum,h+25,VF)  # Get high enought to wire up winder
    jss.custom_line(steps, 'G4 S30')  # Pause to get wire tied up

    for num in range(1, 5):
        wind_chore(steps, num, 'x')
        wrap_around_finger(steps, num)

    jss.move_in_line(steps, *datum, h+me, VF)

    jss.custom_line(steps, 'G4 S10')  # pause for satisfaction

    VISUALIZE_AND_COMPILE(steps)


# -------------------- MAIN --------------------

if __name__ == '__main__':
    # run these designs
    FINGERS_TEST()
    WIND_1_THRU_4()