import fullcontrol as fc
from fullcontrol.gcode import ManualGcode
import FCJSS as jss

# ---------------- Doc Settings ----------------
output_html = True
output_gcode_to_file = True
output_gcode_to_microSD = True

hmtl_filename = 'hmtl/fc_plot_Winder'  # folder/name w/o extension
gcode_filename = 'gcode/fc_gcode_Winder'  # folder/name w/o extension
gcode_filename_SD = 'D:/fc_gcode_Winder'  # folder/name w/o extension


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
printer_offset = [19.8, 4.9, 4.8]  # Printer offset. Z is opposite X and Y. Take a moment to think about which direction it should go, knowning the nozzle will be off to the left, in front of, and above the bed corner.
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

# -- Design Vars --
winder_offset_x = 44.1
nre = 6.31 + 1  # nozzle radius + margin of error
f = 10.3  # finger length to edge
# -- ----------- --

steps = []

jss.move_in_line(steps, 0,0,0,VF)  # first move
jss.move_in_line(steps, 0,0,10, VF)  # up
jss.move_in_line(steps, winder_offset_x, 0, 0, VF)  # find corner of 
jss.custom_line(steps, 'G92 X0 Y0 Z0')

jss.custom_line(steps, 'G4 S10')  # Pause to visually verify that nozzle is in the right place
jss.move_in_line(steps, 0,0,50,VF)  # Get high enought to wire up winder
# jss.custom_line(steps, 'G4 S60')  # Pause to get wire tied up



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
