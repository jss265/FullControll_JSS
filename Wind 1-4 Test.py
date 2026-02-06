import fullcontrol as fc
from fullcontrol.gcode import ManualGcode
import FCJSS as jss

# ---------------- Doc Settings ----------------
output_html = True
output_gcode_to_file = True
output_gcode_to_microSD = True

hmtl_filename = 'hmtl/Winder'  # folder/name w/o extension
gcode_filename = 'gcode/Winder'  # folder/name w/o extension
gcode_filename_SD = 'D:/Winder'  # folder/name w/o extension


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
printer_offset = [19.8, 4.9, 4.8]  # Origin is bed corner TODO get new nozzle datum
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
h = 28.25  # height of the winder surface
w = 59  # width of main base
lw = 2.5  # length from h to webbing 
ln = 5.5 - .2  # length from h to nail roof - a margin of error TODO verify this val
lf = 8.6  # length from inner to outer finger
le = 5.9  # length between sets of fingers
en = 10  # length from edge to nail
nn = 13  # length from nail to nail
me = 1  # standard margin of error
nre = 2 + 1  # nozzle radius + a margin of error
f = 10.3  # finger length to edge
nd = 1.1  # radius of the nail

datum = [20, 20]

def wrap_around_finger(steps, finger_num):
    A = B = C = D = E = G = []  # don't use F (fast)

    if finger_num in [1, 2, 3, 4]: group = 'x'
    elif finger_num in [5, 6, 7, 8]: group = 'y+'
    elif finger_num in [9, 10, 11, 12]: group = 'x+'
    elif finger_num in [13, 14, 15, 16]: group = 'y'
    else: raise ValueError(f'got {finger_num}, expected 1-32')

    n = (finger_num - 1) % 4
    if group == 'x':
        Ax = Bx = Cx = datum[0] + lf + le/2 + n*(lf+le)
        Dx = Ex = Gx = datum[0] + lf + le/2 + (n-1)*(lf+le)
        Ay = By = Ey = Gy = datum[1]-nre
        Cy = Dy = datum[1]-nre-f
    elif group == 'y+':
        Ax = Bx = Ex = Gx = datum[0]+w+nre
        Cx = Dx = datum[0]+w+nre+f
        Ay = By = Cy = datum[1] + lf + le/2 + n*(lf+le)
        Dy = Ey = Gy = datum[1] + lf + le/2 + (n-1)*(lf+le)
    elif group == 'x+':
        Ax = Bx = Cx = datum[0] + w - lf - le/2 - n*(lf+le)
        Dx = Ex = Gx = datum[0] + w - lf - le/2 - (n-1)*(lf+le)
        Ay = By = Ey = Gy = datum[1]+w+nre        
        Cy = Dy = datum[1]+w+nre+f        
    elif group == 'y':
        Ax = Bx = Ex = Gx = datum[0]-nre
        Cx = Dx = datum[0]-nre-f
        Ay = By = Cy = datum[1] + w - lf - le/2 - n*(lf+le)
        Dy = Ey = Gy = datum[1] + w - lf - le/2 - (n-1)*(lf+le)

    else: raise ValueError('around_finger error. Unknown cause')

    A = [Ax, Ay, h+me]
    B = [Bx, By, h-lw]
    C = [Cx, Cy, h-lw]
    D = [Dx, Dy, h-lw]
    E = [Ex, Ey, h-lw]
    G = [Gx, Gy, h+me]
    
    jss.move_in_line(steps, *A, VF)  # to spot
    jss.move_in_line(steps, *B, S)  # down
    jss.move_in_line(steps, *C, F)
    jss.move_in_line(steps, *D, M)  # around
    jss.move_in_line(steps, *E, F)
    jss.move_in_line(steps, *G, M)  # up
    
def wind_chore(steps, core_num, rad):
    n = core_num - 1

    nx = n // 4
    ny = n % 4

    x = datum[0] + nx*nn
    y = datum[1] + ny*nn

    jss.multi_pass_wind(steps, x, y, h, rad, )
    
# -- ----------- --

steps = []

jss.move_in_line(steps, 0,0,0,VF)  # first move
jss.move_in_line(steps, 0,0,h+5,VF)  # clearance
jss.move_in_line(steps, *datum, h, VF)  # over to origin
jss.custom_line(steps, 'G4 S4')  # Pause to visually verify that nozzle is in the right place

jss.move_in_line(steps, *datum,h+25,VF)  # Get high enought to wire up winder
jss.custom_line(steps, 'G4 S30')  # Pause to get wire tied up

jss.multi_pass_wind()
wrap_around_finger(steps, 1)

# jss.move_in_line(steps, *datum, h+me, VF)

jss.custom_line(steps, 'G4 S10')  # pause for satisfaction

# ---------------- Visualize / Compile ----------------
if output_html:
    steps_for_html = [s for s in steps if not isinstance(s, ManualGcode)]
    jss.save_html(steps_for_html, html_filename=hmtl_filename)


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
