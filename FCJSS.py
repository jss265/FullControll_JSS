import os
import math
from typing import List
from pathlib import Path
import re

import plotly.io as pio
import plotly.graph_objects as go

import fullcontrol as fc
from fullcontrol import PlotControls
from fullcontrol.visualize.steps2visualization import visualize
from fullcontrol.visualize.plotly import plot as fc_plot
from fullcontrol.gcode import ManualGcode

# ---------------- Constants ----------------
BLACK = [0,0,0]
RED = [1,0,0]
GREEN = [0,1,0]
YELLOW = [1,1,0]
BLUE = [0,0,1]
MAGENTA = [1,0,1]
CYAN = [0,1,1]
WHITE = [1,1,1]

SPEED1 = 7200
SPEED2 = 3600
SPEED3 = 3000
SPEED4 = 1500
SPEED5 = 750
SPEED6 = 100

# ---------------- Functions ----------------

def custom_line(steps: List, line):
    """
    Inserts a custom gcode line. These will NOT be represented in the visualization.
    There is not example code in demo for this reason.
    
    :param steps: list of steps to append
    :param line: line of code to add (str)
    """
    steps.append(ManualGcode(text=line))

def pause(steps: List, s):
    custom_line(steps, f'G4 S{s}')

def move_in_line(steps: List, x, y, z, speed):
    """
    Add a linear movement to the gcode
    
    :param steps: list of steps to append
    :param x, y, z: coordinates of movement destination
    :param speed: required speed in mm/min eg. 3000 mm/min = 50 mm/s
    """
    if not hasattr(move_in_line, "last_speed"):
        move_in_line.last_speed = None

    if speed != move_in_line.last_speed:
        steps.append(fc.Printer(travel_speed=speed))
        move_in_line.last_speed = speed
    
    if speed >= SPEED1:
        color = WHITE
    elif speed >= SPEED2:
        color = BLUE
    elif speed >= SPEED3:
        color = GREEN
    elif speed >= SPEED4:
        color = YELLOW
    elif speed >= SPEED5:
        color = RED
    else:
        color = BLACK

    steps.append(fc.Point(x=x,y=y,z=z, color=color))

def wind_helix(
    steps: List,
    center_x=0,
    center_y=0,
    start_z=0,
    radius=10,
    pitch=2,
    height=20,
    turns=None,
    points_per_turn=100,
    speed=SPEED3,
    rotation='ccw',   # 'ccw' or 'cw'
    start_angle=0,      # new: starting angle offset in radians, controls which side the spiral begins
    print_report=True
):
    """
    Add a helical (spiral) path to steps.

    :param steps: List of fc.Point objects to append
    :param center_x: X center of the helix
    :param center_y: Y center of the helix
    :param start_z: starting Z coordinate
    :param radius: radius of the helix in mm
    :param pitch: vertical distance per turn (mm)
    :param height: total height of helix (mm)
    :param turns (int): optional, number of full turns (calculated from height/pitch if None)
    :param points_per_turn: number of points per full turn
    :param speed: movement speed (mm/min)
    :param rotation: 'ccw' = counterclockwise, 'cw' = clockwise
    :param start_angle: new, starting angle offset in degrees (going CCW) or 'x', 'y', 'x+', 'y+'
    """
    if isinstance(start_angle, str):
        if start_angle.lower() == 'x':
            start_angle = 270
        elif start_angle.lower() == 'x+':
            start_angle = 90
        elif start_angle.lower() == 'y':
            start_angle = 180
        elif start_angle.lower() == 'y+':
            start_angle = 0
        else:
            raise ValueError("Invalid start_angle string. Use 'x', 'x+', 'y', 'y+' or radians.")

    if turns is None:
        turns = abs(height / pitch)

    total_points = int(points_per_turn * turns)
    dz = height / total_points  # Z increment per point

    # Direction multiplier for CW / CCW
    direction = 1 if rotation == 'ccw' else -1
    dtheta = direction * 2 * math.pi / points_per_turn  # angle increment per point

    z = start_z
    for i in range(total_points + 1):
        theta = i * dtheta + (start_angle * math.pi / 180)  # apply start_angle offset here
        x = center_x + radius * math.cos(theta)
        y = center_y + radius * math.sin(theta)

        move_in_line(steps, x, y, z, speed)
        z += dz
    
    if print_report:
        total_windings = int(turns)
        print(f'{total_windings} windings wound at {center_x}, {center_y}, {start_z}')

def multi_pass_wind(
    steps: List,
    center_x=0,
    center_y=0,
    start_z=0,
    start_radius=10,
    pitch=2,
    height=20,
    turns=None,
    points_per_turn=100,
    speed=SPEED3,
    rotation='ccw',      # 'ccw' or 'cw'
    start_angle=0,        # starting angle offset in degrees
    passes=2,            # number of passes
    spacing=2,           # radial distance to increase radius for each pass
    start_down=False    # if True, first pass goes downward
):
    """
    Create multiple helical passes stacked radially (radius increases each pass) 
    with alternating pitch direction (up/down).

    :param steps: list of fc.Point objects
    :param center_x: X center of helices
    :param center_y: Y center of helices
    :param start_z: starting Z coordinate
    :param start_radius: starting radius of the first helix
    :param pitch: pitch of each helix (flips sign each pass)
    :param height: height of each individual helix (ignored if turns is specified)
    :param turns: number of full turns for each helix (optional)
    :param points_per_turn: points per turn
    :param speed: movement speed in mm/min
    :param rotation: 'ccw' or 'cw'
    :param start_angle: starting angle offset in radians (going CCW) or 'x', 'y', 'x+', 'y+'
    :param passes: number of passes
    :param spacing: radial distance to increase radius for each pass
    :param start_down: if True, first pass goes downward
    :return: (x, y, z) final position of the wind
    """
    direction_multiplier = -1 if start_down else 1
    current_radius = start_radius
    current_z = start_z

    total_turns = turns if turns is not None else int(abs(height / pitch))

    for i in range(passes):
        # flip pitch according to direction_multiplier
        helix_height = height * direction_multiplier if turns is None else abs(turns * pitch) * direction_multiplier

        wind_helix(
            steps,
            center_x=center_x,
            center_y=center_y,
            start_z=current_z,
            radius=current_radius,
            pitch=pitch * direction_multiplier,  # flip pitch sign each pass
            height=helix_height,
            turns=turns,
            points_per_turn=points_per_turn,
            speed=speed,
            rotation=rotation,
            start_angle=start_angle,     # pass the angle along
            print_report=False
        )

        current_radius += spacing        # increase radius for next pass
        direction_multiplier *= -1       # flip direction/pitch for next pass
        current_z += helix_height        # set new starting Z for next pass

    total_windings = total_turns * passes
    print(f'{total_windings} windings wound at {center_x}, {center_y}, {start_z}')
    
    # Calculate final position
    # The final radius after all passes (before last increment in loop)
    final_radius = start_radius + spacing * (passes - 1)
    
    # Convert start_angle to radians
    if isinstance(start_angle, str):
        if start_angle.lower() == 'x':
            angle_deg = 270
        elif start_angle.lower() == 'x+':
            angle_deg = 90
        elif start_angle.lower() == 'y':
            angle_deg = 180
        elif start_angle.lower() == 'y+':
            angle_deg = 0
        else:
            raise ValueError("Invalid start_angle string. Use 'x', 'x+', 'y', 'y+' or degrees.")
    else:
        angle_deg = start_angle
    
    angle_rad = angle_deg * math.pi / 180
    
    # Calculate final x, y position based on final radius and angle
    final_x = center_x + final_radius * math.cos(angle_rad)
    final_y = center_y + final_radius * math.sin(angle_rad)
    
    return final_x, final_y, current_z

def save_gcode(steps, printer, gcode_filename, print_settings, user_overrides):
    """
    Compile GCode associated with steps passed in
    
    :param steps: design steps 
    :param printer: type of printer being used
    :param gcode_filename: destination file location
    :param print_settings: printer settings being used
    :param user_overrides: overrides starting procedure
    """
    out_path = Path(gcode_filename)
    os.makedirs(out_path.parent, exist_ok=True)
    out_path = out_path.with_suffix('.gcode')

    initialization_data = {
        **print_settings,
        **user_overrides
    }
    
    fc.transform(
        steps,
        'gcode',
        fc.GcodeControls(
            printer_name=printer,
            save_as=gcode_filename,
            initialization_data=initialization_data, 
            include_date=False
        )
    )
    print(f"Saved FullControl GCode to:     {out_path.resolve()}")  # space added after ':' to align with save_html print line

def save_html(steps, html_filename="fc_plot.html", embed=True, animate=False, frame_step=50):
    """
    Save the FullControl plot as a standalone, interactive HTML file.
    
    :param steps: List of FullControl steps
    :param html_filename: Output filename
    :param embed: Whether to embed Plotly.js
    :param animate: Whether to create an animated progress plot
    :param frame_step: Number of steps per animation frame
    """
    
    plot_controls = PlotControls(
        color_type="manual",
        style="line",
        raw_data=True
    )
    
    # ---- REQUIRED FOR NON-EXTRUSION PLOTS ----
    plot_controls.line_width = 1.0
    
    if not animate:
        # Original static plot logic
        plot_data = visualize(steps, plot_controls, show_tips=False)
        
        captured_fig = {"fig": None}
        original_show = go.Figure.show
        
        def capture_show(self, *args, **kwargs):
            captured_fig["fig"] = self
            return None
        
        go.Figure.show = capture_show
        try:
            fc_plot(plot_data, plot_controls)
        finally:
            go.Figure.show = original_show
        
        fig = captured_fig["fig"]
        if fig is None:
            raise RuntimeError("Failed to capture FullControl figure")
        
        # Ensure equal axis scaling
        fig.update_layout(scene=dict(aspectratio=dict(x=1, y=1, z=1)))
    else:
        # Animated plot logic
        frames = []
        frame_names = []
        
        # Create frames at regular intervals
        for i in range(0, len(steps), frame_step):
            end_idx = min(i + frame_step, len(steps))
            frame_steps = steps[:end_idx]
            
            plot_data = visualize(frame_steps, plot_controls, show_tips=False)
            
            captured_fig = {"fig": None}
            original_show = go.Figure.show
            
            def capture_show(self, *args, **kwargs):
                captured_fig["fig"] = self
                return None
            
            go.Figure.show = capture_show
            try:
                fc_plot(plot_data, plot_controls)
            finally:
                go.Figure.show = original_show
            
            frame_fig = captured_fig["fig"]
            if frame_fig is not None:

                frames.append(go.Frame(data=frame_fig.data, name=f"Step {end_idx}"))
                frame_names.append(f"Step {end_idx}")
        
        if not frames:
            raise RuntimeError("Failed to create any animation frames")
        
        # Calculate full bounds from all steps
        xs, ys, zs = [], [], []

        for s in steps:
            if isinstance(s, fc.Point):
                xs.append(s.x)
                ys.append(s.y)
                zs.append(s.z)

        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        zmin, zmax = min(zs), max(zs)
        
        # Calculate the maximum range to ensure equal scaling
        xrange = xmax - xmin
        yrange = ymax - ymin
        zrange = zmax - zmin
        max_range = max(xrange, yrange, zrange)
        
        # Center each range and expand to max_range
        x_center = (xmin + xmax) / 2
        y_center = (ymin + ymax) / 2
        z_center = (zmin + zmax) / 2
        
        # Add invisible reference markers to all frames to keep axes fixed
        ref_marker = go.Scatter3d(
            x=[x_center - max_range/2, x_center + max_range/2],
            y=[y_center - max_range/2, y_center + max_range/2],
            z=[z_center - max_range/2, z_center + max_range/2],
            mode='markers',
            marker=dict(size=0, opacity=0),
            showlegend=False,
            hoverinfo='skip'
        )
        
        # Add reference marker to first frame and all subsequent frames
        frames[0].data = list(frames[0].data) + [ref_marker]
        for i in range(1, len(frames)):
            frames[i].data = list(frames[i].data) + [ref_marker]
        
        # Create the figure with animation
        fig = go.Figure(data=frames[0].data, frames=frames)
        
        fig.update_layout(
            scene=dict(
                aspectmode="data",
                xaxis=dict(range=[x_center - max_range/2, x_center + max_range/2], autorange=False),
                yaxis=dict(range=[y_center - max_range/2, y_center + max_range/2], autorange=False),
                zaxis=dict(range=[z_center - max_range/2, z_center + max_range/2], autorange=False),
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                dict(
                                    frame=dict(duration=500, redraw=True),
                                    fromcurrent=True,
                                    mode="immediate",
                                    transition=dict(duration=0)
                                )
                            ]
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[
                                [None],
                                dict(
                                    frame=dict(duration=0, redraw=False),
                                    mode="immediate",
                                    transition=dict(duration=0)
                                )
                            ]
                        )
                    ]
                )
            ],
            sliders=[
                dict(
                    active=0,
                    steps=[
                        dict(
                            method="animate",
                            args=[
                                [frame.name],
                                dict(
                                    frame=dict(duration=0, redraw=True),
                                    mode="immediate",
                                    transition=dict(duration=0)
                                )
                            ],
                            label=frame.name
                        ) for frame in frames
                    ],
                    currentvalue={"prefix": "Progress: "},
                )
            ]
        )
    
    out_path = Path(html_filename) if not animate else Path(html_filename+'_animate')
    os.makedirs(out_path.parent, exist_ok=True)
    if out_path.suffix != '.html':
        out_path = out_path.with_suffix('.html')
    pio.write_html(fig, out_path, include_plotlyjs=embed, auto_open=False)
    
    print(f"Saved FullControl HTML plot to: {out_path.resolve()}")

def check_gcode_bounds(gcode_path: Path, limits_xyz):
    """
    Checks that ABSOLUTION MOTIONS G0, G1, G2, G3, do not exceed limits.
    Does NOT check for splines (G5, homing G28, or probing moves G29, G30, G38)
    NOTE: Be careful to ensure that G92 (set position) to (0,0,0) at the beginning
    of code, and that the print head is moved physically to position z=0
    before your gcode code runs. Failure can result in printer damage.

    :param gcode_path: Input GCode
    :param limits_xyz: Set limits as [x, y, z] (mm)
    """
    gcode_path = Path(gcode_path)
    if gcode_path.suffix.lower() != ".gcode":
        gcode_path = gcode_path.with_suffix(".gcode")

    max_x, max_y, max_z = limits_xyz
    x = y = z = 0.0
    errors = []

    with open(gcode_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            # Only check motion commands
            if line.startswith(("G0", "G1", "G2", "G3")):
                mx = re.search(r"\bX(-?\d+\.?\d*)", line)
                my = re.search(r"\bY(-?\d+\.?\d*)", line)
                mz = re.search(r"\bZ(-?\d+\.?\d*)", line)

                if mx: x = float(mx.group(1))
                if my: y = float(my.group(1))
                if mz: z = float(mz.group(1))

                if x < 0 or x > max_x or y < 0 or y > max_y or z < 0 or z > max_z:
                    errors.append((line_num, line, (x, y, z)))

    return errors  # [[line_num, line, pos]]
