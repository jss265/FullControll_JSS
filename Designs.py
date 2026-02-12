import fullcontrol as fc
from fullcontrol.gcode import ManualGcode
import FCJSS as jss
from Winder import *
import Winder  

def TEST_DATUM():
    global output_html, output_gcode_to_microSD, output_gcode_to_file, animate, hmtl_filename, gcode_filename, gcode_filename_SD
    Winder.output_html = True
    Winder.output_gcode_to_file = True
    Winder.output_gcode_to_microSD = True
    Winder.animate = False

    Winder.hmtl_filename = 'hmtl/Test_Datum'
    Winder.gcode_filename = 'gcode/Test_Datum'
    Winder.gcode_filename_SD = 'D:/Test_Datum'

    steps = []

    jss.move_in_line(steps, 0, 0, 0, VF)
    jss.pause(steps, 5)
    jss.move_in_line(steps, 0, 0, 1, VF)

    VISUALIZE_AND_COMPILE(steps, Winder.animate)

def FINGERS_TEST():
    global output_html, output_gcode_to_microSD, output_gcode_to_file, animate, hmtl_filename, gcode_filename, gcode_filename_SD
    Winder.output_html = True
    Winder.output_gcode_to_file = True
    Winder.output_gcode_to_microSD = True
    Winder.animate = False

    Winder.hmtl_filename = 'hmtl/Finger_Test'
    Winder.gcode_filename = 'gcode/Finger_Test'
    Winder.gcode_filename_SD = 'D:/Finger_Test'

    steps = []

    jss.move_in_line(steps, 0,0,0,VF)  # first move
    jss.move_in_line(steps, 0,0,h+5,VF)  # clearance
    jss.move_in_line(steps, *datum, h, VF)  # over to origin
    jss.custom_line(steps, 'G4 S10')  # Pause to visually verify that nozzle is in the right place

    for finger_num in range(1,17):
        wrap_around_finger(steps, finger_num, VF)

    jss.move_in_line(steps, *datum, h+me, VF)

    jss.custom_line(steps, 'G4 S10')  # pause for satisfaction

    VISUALIZE_AND_COMPILE(steps, Winder.animate)

def WIND_1_THRU_4():
    global output_html, output_gcode_to_microSD, output_gcode_to_file, animate, hmtl_filename, gcode_filename, gcode_filename_SD
    Winder.output_html = True
    Winder.output_gcode_to_file = True
    Winder.output_gcode_to_microSD = True
    Winder.animate = False

    Winder.hmtl_filename = 'hmtl/Wind_1-4'
    Winder.gcode_filename = 'gcode/Wind_1-4'
    Winder.gcode_filename_SD = 'D:/Wind_1-4'

    steps = []

    jss.move_in_line(steps, 0,0,0,VF)  # first move
    jss.move_in_line(steps, 0,0,h+5,VF)  # clearance
    jss.move_in_line(steps, *datum, h, VF)  # over to origin
    jss.pause(steps, 4)  # Pause to visually verify that nozzle is in the right place

    jss.move_in_line(steps, *datum,h+25,VF)  # Get high enought to wire up winder
    jss.pause(steps, 45)  # Pause to get wire tied up

    for num in range(1, 5):
        _, final = wind_chore(steps, num, 'x')  # wind core (end on the floor of h so that wire doesn't get caught)
        jss.move_in_line(steps, final[0], final[1]-me, final[2]+me, M)  # move up and out of the way
        x, y, z = wrap_around_finger(steps, num, VF)  # wrap fingers

    jss.move_in_line(steps, x, y, z+me, M)
    jss.move_in_line(steps, *datum, h+me, VF)

    jss.custom_line(steps, 'G4 S10')  # pause for satisfaction

    VISUALIZE_AND_COMPILE(steps, Winder.animate)


# -------------------- MAIN --------------------

if __name__ == '__main__':
    
    # TEST_DATUM()
    # FINGERS_TEST()
    WIND_1_THRU_4()