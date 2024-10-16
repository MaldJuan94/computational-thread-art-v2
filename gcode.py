import math


def build_cnc_niels(width, height, sides_list, algorithm = "CTA"):
    left_points = [key for key, value in sides_list.items() if value == 2]
    top_points = [key for key, value in sides_list.items() if value == 1]
    right_points = [key for key, value in sides_list.items() if value == 0]
    bottom_points = [key for key, value in sides_list.items() if value == 3]

    left_points_coordinates = generate_points_line((0, 0), (0, height), len(left_points))[::-1]
    top_points_coordinates = generate_points_line((0, height), (width, height), len(top_points))
    right_points_coordinates = generate_points_line((width, height), (width, 0), len(right_points))
    bottom_points_coordinates = generate_points_line((width, 0), (0, 0), len(bottom_points))[::-1]

    if algorithm == "CTA":
        top_points_coordinates = top_points_coordinates[::-1]
        right_points_coordinates = right_points_coordinates[::-1]

    left_points_distance = calculate_square_uniform_distance((0, 0), (0, height), len(left_points))
    top_points_distance = calculate_square_uniform_distance((0, height), (width, height), len(top_points))
    right_points_distance = calculate_square_uniform_distance((width, height), (width, 0), len(right_points))
    bottom_points_distance = calculate_square_uniform_distance((width, 0), (0, 0), len(bottom_points))

    return {'left_points_distance': left_points_distance,
            'top_points_distance': top_points_distance,
            'right_points_distance': right_points_distance,
            'bottom_points_distance': bottom_points_distance,
            'sides_coordinates': update_sides(sides_list, left_points, top_points, right_points, bottom_points,
                                              left_points_coordinates,
                                              top_points_coordinates, right_points_coordinates,
                                              bottom_points_coordinates)}


def update_sides(sides_list, left_points, top_points, right_points, bottom_points, left_points_coordinates,
                 top_points_coordinates, right_points_coordinates, bottom_points_coordinates):
    temp_sides = sides_list.copy()
    for idx, point in enumerate(left_points):
        temp_sides[point] = left_points_coordinates[idx]

    for idx, point in enumerate(right_points):
        temp_sides[point] = right_points_coordinates[idx]

    for idx, point in enumerate(top_points):
        temp_sides[point] = top_points_coordinates[idx]

    for idx, point in enumerate(bottom_points):
        temp_sides[point] = bottom_points_coordinates[idx]

    return temp_sides


def generate_points_line(start, end, nail_quantity):
    x1, y1 = start
    x2, y2 = end
    return [(x1 + (x2 - x1) * (i + 1) / (nail_quantity + 1), y1 + (y2 - y1) * (i + 1) / (nail_quantity + 1)) for i in
            range(nail_quantity)]


def calculate_square_uniform_distance(start, end, nail_quantity):
    x1, y1 = start
    x2, y2 = end
    total_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    segment_distance = total_distance / (nail_quantity + 1)
    return segment_distance


def calculate_circle_uniform_distance(radius, nail_quantity):
    distance = (2 * math.pi * radius) / nail_quantity
    return distance


def generate_gcode(sides_list, drawing_depth,
                   safe_height):
    g_code = ["G90 ; Use absolute coordinates", "G21 ; Use units in millimeters",
              f"G1 Z{safe_height:.2f}; Go up to safe height"]

    # Start G-code
    for key, (x, y) in sides_list.items():
        g_code.append(f"G0 X{x:.2f} Y{y:.2f} ; Point {key}: move to position")
        g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
        g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")

    # End G-code
    g_code.append(F"G1 Z{safe_height:.2f} ; Go up to safe height")
    g_code.append("M30 ; End of program")

    return g_code


def generate_gcode_lines(lines_group, sides_info, side, drawing_depth, safe_height, knot_height):
    sides_coord = sides_info['sides_coordinates']

    vertical_points_distance = (sides_info['left_points_distance'] + sides_info['right_points_distance']) / 2
    horizontal_points_distance = (sides_info['top_points_distance'] + sides_info['bottom_points_distance']) / 2
    g_code_group = []
    for group in lines_group:
        current_line = group["lines"]

        flatten_group_line = [int(niel) for niel_group in current_line for niel in niel_group.split()]
        size_group_line = len(flatten_group_line)

        g_code = ["G90 ; Use absolute coordinates", "G21 ; Use units in millimeters"]

        for idx, value in enumerate(flatten_group_line):
            if idx == 0:
                g_code.append(
                    f"G0 X{sides_coord[value - 1][0]:.2f} Y{sides_coord[value - 1][1]:.2f} ; Point {value}: move to "
                    f"position (first)")
                g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
                g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")
            elif idx == size_group_line - 1:
                g_code.append(
                    f"G0 X{sides_coord[value - 1][0]:.2f} Y{sides_coord[value - 1][1]:.2f} ; Point {value}: move to "
                    f"position (last)")
                g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
                g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")
            else:
                next_value = flatten_group_line[idx + 1]
                if value + 1 == next_value or value - 1 == next_value:
                    if side[value - 1] in [0, 2]:
                        g_code += generate_gcode_square(sides_coord[value - 1][0],
                                                        sides_coord[value - 1][1],
                                                        sides_coord[next_value - 1][0],
                                                        sides_coord[next_value - 1][1],
                                                        drawing_depth,
                                                        safe_height,
                                                        knot_height,
                                                        vertical_points_distance,
                                                        side[value - 1] == 0,
                                                        True)
                    if side[value - 1] in [1, 3]:
                        g_code += generate_gcode_square(sides_coord[value - 1][0],
                                                        sides_coord[value - 1][1],
                                                        sides_coord[next_value - 1][0],
                                                        sides_coord[next_value - 1][1],
                                                        drawing_depth,
                                                        safe_height,
                                                        knot_height,
                                                        horizontal_points_distance,
                                                        side[value - 1] == 1,
                                                        False)

        g_code.append("M30 ; End of program")
        g_code_group.append({"color": group['color'], "gcode": g_code})

    return g_code_group


def generate_gcode_lines_kaspar(lines_group, sides_info, side, drawing_depth, safe_height, knot_height):
    sides_coord = sides_info['sides_coordinates']

    vertical_points_distance = (sides_info['left_points_distance'] + sides_info['right_points_distance']) / 2
    horizontal_points_distance = (sides_info['top_points_distance'] + sides_info['bottom_points_distance']) / 2
    g_code_group = []

    flatten_group_line = lines_group
    size_group_line = len(flatten_group_line)

    g_code = ["G90 ; Use absolute coordinates", "G21 ; Use units in millimeters"]

    for idx, value in enumerate(flatten_group_line):
        if idx == 0:
            g_code.append(
                f"G0 X{sides_coord[value ][0]:.2f} Y{sides_coord[value ][1]:.2f} ; Point {value}: move to "
                f"position (first)")
            g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
            g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")
        elif idx == size_group_line - 1:
            g_code.append(
                f"G0 X{sides_coord[value ][0]:.2f} Y{sides_coord[value ][1]:.2f} ; Point {value}: move to "
                f"position (last)")
            g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
            g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")
        else:
            g_code.append( f"; Point {value}: move to ")
            if side[value ] in [0, 2]:
                g_code += generate_gcode_square(sides_coord[value][0],
                                                sides_coord[value ][1],
                                                sides_coord[value ][0],
                                                sides_coord[value][1],
                                                drawing_depth,
                                                safe_height,
                                                knot_height,
                                                vertical_points_distance,
                                                side[value ] == 0,
                                                True,)
            if side[value] in [1, 3]:
                g_code += generate_gcode_square(sides_coord[value ][0],
                                                sides_coord[value ][1],
                                                sides_coord[value ][0],
                                                sides_coord[value ][1],
                                                drawing_depth,
                                                safe_height,
                                                knot_height,
                                                horizontal_points_distance,
                                                side[value ] == 1,
                                                False)

    g_code.append("M30 ; End of program")
    g_code_group.append({"color": "black", "gcode": g_code})

    return g_code_group


def generate_gcode_square(x1, y1, x2, y2, drawing_depth, safe_height, knot_height, point_distance, inverse=False,
                          vertical=True):
    g_code = []

    if vertical:
        if y1 > y2:
            y1 += point_distance / 2.22
            y2 -= point_distance / 2.22
        else:
            y1 -= point_distance / 2.22
            y2 += point_distance / 2.22

        g_code.append(f"G0 X{x1} Y{y1} Z{safe_height:.2f}")
        g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")

        x1_square = x1
        if inverse:
            x1_square += point_distance / 2
            x2 -= knot_height
        else:
            x1_square -= point_distance / 2
            x2 += knot_height

        g_code.append(f"G1 X{x1_square} Y{y1}")
        g_code.append(f"G1 X{x1_square} Y{y2}")
        g_code.append(f"G1 X{x2} Y{y2}; vertical")
        g_code.append(f"G1 Z{knot_height:.2f}; Go up to safe height")
    else:

        if x1 > x2:
            x1 += point_distance / 2.22
            x2 -= point_distance / 2.22
        else:
            x1 -= point_distance / 2.22
            x2 += point_distance / 2.22

        g_code.append(f"G0 X{x1} Y{y1} Z{safe_height:.2f}")
        g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")

        y1_square = y1
        if inverse:
            y1_square += point_distance / 2
            y2 -= knot_height
        else:
            y1_square -= point_distance / 2
            y2 += knot_height

        g_code.append(f"G1 X{x1} Y{y1_square}")
        g_code.append(f"G1 X{x2} Y{y1_square}")
        g_code.append(f"G1 X{x2} Y{y2}; horizontal")
        g_code.append(f"G1 Z{knot_height:.2f}; Go up to safe height")

    return g_code


def generate_circle_points(center, radius, nail_quantity, algorithm="CTA"):
    cx, cy = center
    points = []
    # Set the initial angle based on the direction
    initial_angle = 0 if algorithm == "CTA" else math.pi
    direction = 1 if algorithm == "CTA" else -1

    for i in range(nail_quantity):
        angle = initial_angle + direction * (2 * math.pi * i / nail_quantity)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points


def generate_circle_gcode(points, drawing_depth, safe_height):
    g_code = ["G90 ; Use absolute coordinates", "G21 ; Use units in millimeters",
              f"G1 Z{safe_height:.2f}; Go up to safe height"]

    # Start G-code
    for idx, (x, y) in enumerate(points):
        g_code.append(f"G0 X{x:.2f} Y{y:.2f} ; Point {idx}: move to position")
        g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
        g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")

    # End G-code
    g_code.append(F"G1 Z{safe_height:.2f} ; Go up to safe height")
    g_code.append("M30 ; End of program")

    return g_code


def calculate_angle_and_distance(p, center):
    x, y = p
    cx, cy = center

    # Calculate the angle of the point with respect to the center
    angle = math.atan2(y - cy, x - cx)

    # Calculate the distance from the center to the point
    distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)

    return angle, distance


def generate_new_point_with_distance(center, angle, original_distance, new_distance):
    new_radius = original_distance + new_distance

    # Calculate the new coordinates using the angle and the new radius
    cx, cy = center
    x_new = cx + new_radius * math.cos(angle)
    y_new = cy + new_radius * math.sin(angle)

    return x_new, y_new


def move_point_along_circumference(center, p, move_distance, radius):
    angle, _ = calculate_angle_and_distance(p, center)

    # Calculate additional angle based on desired distance
    move_angle = move_distance / radius

    # Calculate the new angle
    new_angle = angle + move_angle

    # Calculate the new coordinates using the new angle
    cx, cy = center
    x_new = cx + radius * math.cos(new_angle)
    y_new = cy + radius * math.sin(new_angle)

    return x_new, y_new


def determine_rotation_direction(center, p1, p2):
    # Calculate angles for p1 and p2
    angle1, _ = calculate_angle_and_distance(p1, center)
    angle2, _ = calculate_angle_and_distance(p2, center)

    # Calculate the angle difference
    angle_difference = angle2 - angle1

    # Normalize the angle difference for the range [-π, π]
    angle_difference = (angle_difference + math.pi) % (2 * math.pi) - math.pi

    # Determine the direction of rotation
    if angle_difference > 0:
        return "CCW"
    elif angle_difference < 0:
        return "CW"
    else:
        return "same_point"


def generate_circle_gcode_lines(lines_group, points, radius, nail_quantity, drawing_depth, safe_height, knot_height):
    g_code_group = []
    for group in lines_group:
        current_line = group["lines"]

        flatten_group_line = [int(niel) for niel_group in current_line for niel in niel_group.split()]
        size_group_line = len(flatten_group_line)

        g_code = ["G90 ; Use absolute coordinates", "G21 ; Use units in millimeters"]

        for idx, value in enumerate(flatten_group_line):
            if idx == 0:
                g_code.append(
                    f"G0 X{points[value - 1][0]:.2f} Y{points[value - 1][1]:.2f} ; Point {value}: move to "
                    f"position (first)")
                g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
                g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")
            elif idx == size_group_line - 1:
                g_code.append(
                    f"G0 X{points[value - 1][0]:.2f} Y{points[value - 1][1]:.2f} ; Point {value}: move to "
                    f"position (last)")
                g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
                g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")
            else:
                next_value = flatten_group_line[idx + 1]
                if value + 1 == next_value or value - 1 == next_value:
                    g_code += generate_gcode_square_for_circle(
                        points[value - 1],
                        points[next_value - 1],
                        radius,
                        nail_quantity,
                        drawing_depth,
                        safe_height,
                        knot_height
                    )

        g_code.append("M30 ; End of program")
        g_code_group.append({"color": group['color'], "gcode": g_code})

    return g_code_group


def generate_circle_gcode_lines_kaspar(lines_group, points, radius, nail_quantity, drawing_depth, safe_height, knot_height):
    g_code_group = []

    size_group_line = len(lines_group)

    g_code = ["G90 ; Use absolute coordinates", "G21 ; Use units in millimeters"]

    for idx, value in enumerate(lines_group):
        if idx == 0:
            g_code.append(
                f"G0 X{points[value][0]:.2f} Y{points[value][1]:.2f} ; Point {value}: move to "
                f"position (first)")
            g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
            g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")
        elif idx == size_group_line - 1:
            g_code.append(
                f"G0 X{points[value][0]:.2f} Y{points[value ][1]:.2f} ; Point {value}: move to "
                f"position (last)")
            g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")
            g_code.append(f"G1 Z{safe_height:.2f}; Go up to safe height")
        else:
            g_code += generate_gcode_square_for_circle(
                points[value],
                points[value],
                radius,
                nail_quantity,
                drawing_depth,
                safe_height,
                knot_height,
                "KASPAR"
            )

    g_code.append("M30 ; End of program")
    g_code_group.append({"color": 'black', "gcode": g_code})

    return g_code_group


def generate_gcode_square_for_circle(point_from, point_to, radius, nail_quantity, drawing_depth, safe_height,
                                     knot_height, algorithm = "CTA"):
    point_distance = calculate_circle_uniform_distance(radius, nail_quantity)
    center = (radius, radius)
    g_code = []
    move_distance = point_distance / 2.22

    if algorithm == "CTA":
        rotation_direction = determine_rotation_direction(center, point_from, point_to)
        if rotation_direction == 'CW':
            moved_p1 = move_point_along_circumference(center, point_from, move_distance, radius)
            moved_p2 = move_point_along_circumference(center, point_to, -move_distance, radius)
        elif rotation_direction == 'CCW':
            moved_p1 = move_point_along_circumference(center, point_from, -move_distance, radius)
            moved_p2 = move_point_along_circumference(center, point_to, move_distance, radius)
        else:
            moved_p1 = move_point_along_circumference(center, point_from, move_distance, radius)
            moved_p2 = move_point_along_circumference(center, point_to, move_distance, radius)
    else:
        moved_p1 = move_point_along_circumference(center, point_from, move_distance, radius)
        moved_p2 = move_point_along_circumference(center, point_to, -move_distance, radius)

    # Calculate angles and distances for the original points
    angle1, distance = calculate_angle_and_distance(moved_p1, center)
    angle2, distance = calculate_angle_and_distance(moved_p2, center)

    # Generate new points on the largest circle
    new_p1 = generate_new_point_with_distance(center, angle1, distance, point_distance)
    new_p2 = generate_new_point_with_distance(center, angle2, distance, point_distance)
    # Generate new points on the smallest circle
    new_p3 = generate_new_point_with_distance(center, angle2, distance, -point_distance)

    g_code.append(f"G0 X{moved_p1[0]:2f} Y{moved_p1[1]:.2f} Z{safe_height:.2f}")
    g_code.append(f"G1 Z{-drawing_depth:.2f}; Go down to tie a knot")

    g_code.append(f"G1 X{new_p1[0]:2f} Y{new_p1[1]:.2f}")
    g_code.append(f"G1 X{new_p2[0]:2f} Y{new_p2[1]:.2f}")
    g_code.append(f"G1 X{new_p3[0]:2f} Y{new_p3[1]:.2f}")
    g_code.append(f"G1 Z{knot_height:.2f}; Go up to safe height")

    return g_code


def build_gcode(shape, size, input_group, list_sides, nail_quantity, drawing_depth, safe_height, knot_height, algorithm):
    if shape.lower() in ["circle", "ellipse", "round"]:
        radius = size[0] / 2
        center = (radius, radius)
        points = generate_circle_points(center, radius, nail_quantity, algorithm)
        g_code_niels = generate_circle_gcode(points, drawing_depth, safe_height)
        if algorithm == "CTA":
            g_codes_groups = generate_circle_gcode_lines(input_group, points, radius, nail_quantity,
                                                     drawing_depth, safe_height, knot_height)
        else:
            g_codes_groups = generate_circle_gcode_lines_kaspar(input_group, points, radius, nail_quantity,
                                                         drawing_depth, safe_height, knot_height)
    else:
        sides_niels = build_cnc_niels(size[0], size[1], list_sides, algorithm)
        g_code_niels = generate_gcode(sides_niels['sides_coordinates'], drawing_depth, safe_height)
        if algorithm == "CTA":
            g_codes_groups = generate_gcode_lines(input_group, sides_niels, list_sides, drawing_depth,
                                  safe_height, knot_height)
        else:
            g_codes_groups = generate_gcode_lines_kaspar(input_group, sides_niels, list_sides, drawing_depth,
                                                  safe_height, knot_height)

    return {'g_code_niels': g_code_niels, 'g_codes_groups': g_codes_groups}
