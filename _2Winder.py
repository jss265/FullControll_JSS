import fullcontrol as fc
from fullcontrol.gcode import ManualGcode
import FCJSS as jss

# ---------------- Doc Settings ----------------
output_html = False
output_gcode_to_file = False
output_gcode_to_microSD = False
animate = None

hmtl_filename = 'hmtl/2Winder'  # folder/name w/o extension
gcode_filename = 'gcode/2Winder'  # folder/name w/o extension
gcode_filename_SD = 'D:/2Winder'  # folder/name w/o extension


# ---------------- Printer Settings ----------------
printer = 'ender_3_custom'  # printer options: generic, ultimaker2plus, prusa_i3, ender_3, cr_10, bambulab_x1, toolchanger_T0, toolchanger_T1, toolchanger_T2, toolchanger_T3
# !!NOTE!! "ender_3_custom" required otherise compiler will not respect ESSENTIAL overrides!! This will lead to catastrophic homing sequence. 
# !!NOTE!! ender_3 firmware (not gcode) requires a Homing and Parking Sequence. Therefore planning this into design and manual physical homing are both require.
#           Homing Sequence:
#               Printer head moves up, and the all the way over toward the limit switch.
#               Printer bed moves back all the way toward the limit switch.
#               Your code position (0,0,0) will begin exactly right here. 
#               NOTE this is off the print bed. If you employ an offset into the 'start_code' you can make (0,0,0) the edge of the bed
#           Parking Sequence:
#               Printer head moves up, and the all the way over toward the limit switch.
#               Printer bed moves back all the way toward the limit switch.
#               Printer bed moves all the way out.
#           Pre-gcode, manual homing REQUIRED:
#               Keep in mind the unavoidable Homing/Parking Sequences
#               Printer head(x) and bed(y) can be in any position
#               Manually move printer head(z) to the point which it barely touches the printer bed.
#               You are ready to run your gcode

printer_limits_xyz = [220, 220, 100]  # Limit adjusted for custom nozzle. ender_3 origional limit was 250
printer_offset = [20.7, 4.8, 4.8]  # Origin is bed corner TODO get new nozzle datum
print_settings = {'extrusion_width': 0.5,'extrusion_height': 0.2, 'nozzle_temp': 0, 'bed_temp': 0, 'fan_percent': 0}  # toggle off fan, bed_temp, nozzle_temp, and arbitrary values for extrusion height/width
start_code = [ManualGcode(text=f"""
G90
G21
M83
M104 S0
M106 S0
M140 S0
G92 X0 Y0 Z{printer_offset[2]}
G0 F1500 X{printer_offset[0]} Y{printer_offset[1]} Z0
G92 X0 Y0 Z0
""")]  # this removes non-necessary starting routine, and potentially catastrophic homing sequence. Z offset necessary.
end_code = [ManualGcode(text="M84")]  # disable all steppers

VF, F, M, S, VS, SS = jss.SPEED1, jss.SPEED2, jss.SPEED3, jss.SPEED4, jss.SPEED5, jss.SPEED6 # Very fast, fast, medium, slow, very slow, super slow. Edit these in FCJSS


# ---------------- Design ----------------

# -- Design Defs --
h = 31.25  # height of the winder surface
w = 42.05  # width of main base
en = 10  # length from edge to first nail
nn = 7.35  # length between each nail
pd = 5.575  # plundge depth into slot
ln = 5.5 - 0.2  # TODO verify and cope Test Grid!! length between h and nail roof - a margin of error
r = 3.675  # radius from core to nozzle path
a_small = 19.197  # arc length angle for small arcs  
a_large = 70.803  # arc length angle for large arcs
p = 0.102 + 0.01  # diamter of wire + a marigin of error

P1 = [1.208, 0.204] # location 1 relative to d1
P2 = [3.675, 0] # location 2 relative to d2
P3 = [0, -7.350] # location 3 relative to d1
P4 = [-3.675, 0] # location 4 relative to d2
P5 = [-1.208, 0.204] # location 5 relative to d1
PF1 = [-2.467, 3.471]  # final location relative to d1
P6 = [-1.208, 0.204] # location 6 relative to d2
P7 = [-3.675, 0] # location 7 relative to d1
P8 = [0, -7.350] # location 8 relative to d2
P9 = [3.675, 0] # location 9 relative to d1
P10 = [1.208, 0.204] # location 10 relative to d2
PF2 = [2.467, 3.471]  # final location relative to d2

A1 = [r, 90-a_small, -a_small]  # Arc for d1 to P1: radius, start angle, angle
A2 = [r, 270, -a_small]  # Arc for P4 to P5: radius, start angle, angle
A3 = [r, 270-a_small, a_large]  # Arc for P5 to P6: radius, start angle, angle
A4 = [r, 90+a_small, a_small]  # Arc for d1 to P1: radius, start angle, angle
A5 = [r, 270, a_small]  # Arc for d1 to P1: radius, start angle, angle
A6 = [r, 270+a_small, a_large]  # Arc for d1 to P1: radius, start angle, angle

datum = [20, 20]  # bottom right corner of the board
d1 = [
    datum[0] + en - P1[0],
    datum[1] + en - P3[1]/2 - P1[1]
]  # plunge location for odd cores
d2 = [
    datum[0] + en + nn - P6[0],
    datum[1] + en - P8[1]/2 - P6[1]
]  # plunge location for even cores

def pluge_slot(steps, finger_num, speed):
    """
    Wraps wire around pair of fingers.
    
    :param steps: list of steps to append
    :param finger_num: location of fingers to wrap
    :param speed: speed of travel from current position to begining of the wrap
    :return: (x, y, z) final position
    """
   
    return 
    
def wind_chore(steps, core_num, angle):
    '''
    Wind wire around a core.
    
    :param steps: list of steps to append
    :param core_num: location of core to wind
    :param angle: represent both start and end position relative to the core (deg OR 'x', 'x+', 'y', 'y+')
    :return: ((start_x, start_y, start_z), (final_x, final_y, final_z)) start and final positions
    '''
    n = core_num - 1

    nx = n % 4
    ny = n // 4

    x = datum[0] + en + nx*nn
    y = datum[1] + en + ny*nn

    passes = int(((4-1.8)/2)/p) - 1  # OD nail head - OD nail shaft. -1 so that wire ends on floor of h
    layers = int(ln/p) - 6  # -3 because starting position should be 1 'p' above h, and 5 'p' lower for error

    start_pos, final_pos = jss.multi_pass_wind(steps, x, y, h+p, nn/2, p, ln-p*7, layers, 100, F, 'ccw', angle, passes, 0, False)

    return start_pos, final_pos
    

# ---------------- Visualize / Compile ----------------
def VISUALIZE_AND_COMPILE(steps, animate):
    if output_html:
        steps_for_html = [s for s in steps if not isinstance(s, ManualGcode)]
        jss.save_html(steps_for_html, html_filename=hmtl_filename, animate=animate)


    if output_gcode_to_file:
        jss.save_gcode(
            steps,
            printer,
            gcode_filename,
            print_settings,
            user_overrides={
                "starting_procedure_steps": start_code,
                "ending_procedure_steps": end_code,
                "material_flow_percent": 0,
                "manual_e_ratio": 0,
                "primer": "no_primer"
                }
            )

    if output_gcode_to_microSD:
        jss.save_gcode(
            steps,
            printer,
            gcode_filename_SD,
            print_settings,
            user_overrides={
                "starting_procedure_steps": start_code,
                "ending_procedure_steps": end_code,
                "material_flow_percent": 0,
                "manual_e_ratio": 0,
                "primer": "no_primer"
                } 
        )

    if output_gcode_to_file or output_gcode_to_microSD:
        errors = jss.check_gcode_bounds(gcode_filename, printer_limits_xyz)

        if errors:
            for line_num, line, pos in errors:
                print(f"Out of bounds at line {line_num}: {line} -> {pos}")
        else:
            print("All moves within bounds.")
