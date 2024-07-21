import math


def build_cnc_niels(width, height, sides_list):
    left_points = [key for key, value in sides_list.items() if value == 2]
    top_points = [key for key, value in sides_list.items() if value == 1]
    right_points = [key for key, value in sides_list.items() if value == 0]
    bottom_points = [key for key, value in sides_list.items() if value == 3]

    left_points_coordinates = generate_points_line((0, 0), (0, height), len(left_points))[::-1]
    top_points_coordinates = generate_points_line((0, height), (width, height), len(top_points))[::-1]
    right_points_coordinates = generate_points_line((width, height), (width, 0), len(right_points))[::-1]
    bottom_points_coordinates = generate_points_line((width, 0), (0, 0), len(bottom_points))[::-1]

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


def generate_circle_points(center, radius, nail_quantity):
    cx, cy = center
    points = []
    for i in range(nail_quantity):
        angle = 2 * math.pi * i / nail_quantity
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

    return (x_new, y_new)


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

    return (x_new, y_new)


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


def generate_gcode_square_for_circle(point_from, point_to, radius, nail_quantity, drawing_depth, safe_height,
                                     knot_height):
    point_distance = calculate_circle_uniform_distance(radius, nail_quantity)
    center = (radius, radius)
    g_code = []
    move_distance = point_distance / 2.22

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


def build_gcode(shape, size, input_group, sides, nail_quantity, drawing_depth, safe_height, knot_height):
    if shape.lower() in ["circle", "ellipse", "round"]:
        radius = size[0] / 2
        center = (radius, radius)
        points = generate_circle_points(center, radius, nail_quantity)
        g_code_niels = generate_circle_gcode(points, drawing_depth, safe_height)
        g_codes_groups = generate_circle_gcode_lines(input_group['lines'], points, radius, nail_quantity,
                                                     drawing_depth, safe_height, knot_height)
    else:
        sides_niels = build_cnc_niels(size[0], size[1], sides)
        g_code_niels = generate_gcode(sides_niels['sides_coordinates'], drawing_depth, safe_height)
        g_codes_groups = generate_gcode_lines(input_group['lines'], sides_niels, sides, drawing_depth,
                                              safe_height, knot_height)

    return {'g_code_niels': g_code_niels, 'g_codes_groups': g_codes_groups}


sides = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0,
         16: 0,
         17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0,
         31: 0, 32: 0,
         33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0,
         47: 0, 48: 0,
         49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0, 55: 0, 56: 0, 57: 0, 58: 0, 59: 0, 60: 0, 61: 0, 62: 0,
         63: 0, 64: 1,
         65: 1, 66: 1, 67: 1, 68: 1, 69: 1, 70: 1, 71: 1, 72: 1, 73: 1, 74: 1, 75: 1, 76: 1, 77: 1, 78: 1,
         79: 1, 80: 1,
         81: 1, 82: 1, 83: 1, 84: 1, 85: 1, 86: 1, 87: 1, 88: 1, 89: 1, 90: 1, 91: 1, 92: 1, 93: 1, 94: 1,
         95: 1, 96: 1,
         97: 1, 98: 1, 99: 1, 100: 1, 101: 1, 102: 1, 103: 1, 104: 1, 105: 1, 106: 1, 107: 1, 108: 1, 109: 1,
         110: 1,
         111: 1, 112: 1, 113: 1, 114: 1, 115: 1, 116: 1, 117: 1, 118: 1, 119: 1, 120: 1, 121: 1, 122: 1,
         123: 1, 124: 1,
         125: 1, 126: 2, 127: 2, 128: 2, 129: 2, 130: 2, 131: 2, 132: 2, 133: 2, 134: 2, 135: 2, 136: 2,
         137: 2, 138: 2,
         139: 2, 140: 2, 141: 2, 142: 2, 143: 2, 144: 2, 145: 2, 146: 2, 147: 2, 148: 2, 149: 2, 150: 2,
         151: 2, 152: 2,
         153: 2, 154: 2, 155: 2, 156: 2, 157: 2, 158: 2, 159: 2, 160: 2, 161: 2, 162: 2, 163: 2, 164: 2,
         165: 2, 166: 2,
         167: 2, 168: 2, 169: 2, 170: 2, 171: 2, 172: 2, 173: 2, 174: 2, 175: 2, 176: 2, 177: 2, 178: 2,
         179: 2, 180: 2,
         181: 2, 182: 2, 183: 2, 184: 2, 185: 2, 186: 2, 187: 2, 188: 2, 189: 2, 190: 3, 191: 3, 192: 3,
         193: 3, 194: 3,
         195: 3, 196: 3, 197: 3, 198: 3, 199: 3, 200: 3, 201: 3, 202: 3, 203: 3, 204: 3, 205: 3, 206: 3,
         207: 3, 208: 3,
         209: 3, 210: 3, 211: 3, 212: 3, 213: 3, 214: 3, 215: 3, 216: 3, 217: 3, 218: 3, 219: 3, 220: 3,
         221: 3, 222: 3,
         223: 3, 224: 3, 225: 3, 226: 3, 227: 3, 228: 3, 229: 3, 230: 3, 231: 3, 232: 3, 233: 3, 234: 3,
         235: 3, 236: 3,
         237: 3, 238: 3, 239: 3, 240: 3, 241: 3, 242: 3, 243: 3, 244: 3, 245: 3, 246: 3, 247: 3, 248: 3,
         249: 3, 250: 3,
         251: 3}

input_lines_circle_group = {'path': 'lines/lines-face-10.pdf', 'stats': [{'color': 'white', 'distance': '0.29 km'},
                                                                         {'color': 'black', 'distance': '0.30 km'}],
                            'lines': [{'color': 'black', 'by_now': '0/1400', 'by_end': '351/1400', 'now': 'black 1/2',
                                       'lines': ['172 90', '89 45', '46 75', '76 34', '33 83', '84 32', '31 85',
                                                 '86 41', '42 76', '75 52', '51 81', '82 36', '35 96', '95 38', '37 80',
                                                 '79 56', '55 74', '73 56', '55 41', '42 90', '89 31', '32 56', '55 95',
                                                 '96 54', '53 74', '73 95', '96 37', '38 77', '78 94', '93 39', '40 89',
                                                 '90 30', '29 78', '77 41', '42 82', '81 46', '45 82', '81 32', '31 94',
                                                 '93 34', '33 97', '98 36', '35 212', '211 32', '31 212', '211 36',
                                                 '35 83', '84 51', '52 79', '80 55', '56 72', '71 38', '37 97', '98 44',
                                                 '43 73', '74 94', '93 44', '43 75', '76 49', '50 97', '98 34',
                                                 '33 213', '214 31', '32 88', '87 35', '36 210', '209 33', '34 96',
                                                 '95 41', '42 84', '83 43', '44 69', '70 96', '95 39', '40 94', '93 79',
                                                 '80 47', '48 86', '85 45', '46 67', '68 97', '98 33', '34 211',
                                                 '212 33', '34 90', '89 36', '35 211', '212 30', '29 91', '92 41',
                                                 '42 87', '88 41', '42 221', '222 41', '42 94', '93 29', '30 92',
                                                 '91 33', '34 215', '216 33', '34 212', '211 38', '37 86', '85 55',
                                                 '56 70', '69 46', '45 90', '89 35', '36 87', '88 47', '48 66', '65 49',
                                                 '50 85', '86 39', '40 210', '209 32', '31 213', '214 37', '38 99',
                                                 '100 37', '38 210', '209 36', '35 97', '98 41', '42 85', '86 43',
                                                 '44 72', '71 48', '47 72', '71 95', '96 176', '175 94', '93 176',
                                                 '175 96', '95 28', '27 92', '91 41', '42 213', '214 30', '29 87',
                                                 '88 49', '50 82', '81 44', '43 220', '219 38', '37 103', '104 40',
                                                 '39 97', '98 178', '177 94', '93 174', '173 94', '93 43', '44 213',
                                                 '214 32', '31 210', '209 37', '38 96', '95 176', '175 97', '98 32',
                                                 '31 215', '216 30', '29 96', '95 58', '57 78', '77 32', '31 91',
                                                 '92 177', '178 93', '94 60', '59 74', '73 37', '38 213', '214 35',
                                                 '36 218', '217 39', '40 92', '91 75', '76 58', '57 104', '103 41',
                                                 '42 211', '212 46', '45 212', '211 39', '40 99', '100 34', '33 208',
                                                 '207 34', '33 214', '213 32', '31 86', '85 49', '50 64', '63 92',
                                                 '91 46', '45 80', '79 46', '45 97', '98 182', '181 99', '100 35',
                                                 '36 213', '214 39', '40 106', '105 44', '43 210', '209 39', '40 212',
                                                 '211 29', '30 94', '93 175', '176 97', '98 54', '53 82', '81 36',
                                                 '35 90', '89 171', '172 95', '96 52', '51 97', '98 29', '30 86',
                                                 '85 41', '42 214', '213 29', '30 95', '96 182', '181 92', '91 179',
                                                 '180 100', '99 49', '50 247', '248 54', '53 78', '77 47', '48 102',
                                                 '101 34', '33 217', '218 39', '40 96', '95 177', '178 91', '92 32',
                                                 '31 217', '218 50', '49 83', '84 56', '55 241', '242 156', '155 239',
                                                 '240 154', '153 238', '237 151', '152 237', '238 47', '48 214',
                                                 '213 43', '44 92', '91 25', '26 196', '195 27', '28 159', '160 24',
                                                 '23 78', '77 63', '64 16', '15 81', '82 21', '22 81', '82 18', '17 79',
                                                 '80 52', '51 114', '113 45', '46 86', '85 169', '170 96', '95 183',
                                                 '184 94', '93 179', '180 98', '97 174', '173 97', '98 31', '32 210',
                                                 '209 35', '36 75', '76 54', '53 104', '103 185', '186 96', '95 171',
                                                 '172 31', '32 216', '215 41', '42 89', '90 181', '182 97', '98 35',
                                                 '36 220', '219 45', '46 213', '214 45', '46 112', '111 48', '47 103',
                                                 '104 187', '188 94', '93 61', '62 81', '82 14', '13 128', '127 54',
                                                 '53 249', '250 62', '61 88', '87 169', '170 97', '98 187', '188 93',
                                                 '94 174', '173 79', '80 23', '24 159', '160 32', '31 157', '158 33',
                                                 '34 213', '214 29', '30 218', '217 37', '38 215', '216 48', '47 212',
                                                 '211 41', '42 161', '162 48', '47 115', '116 46', '45 243', '244 59',
                                                 '60 124', '123 13', '14 74', '73 165', '166 86', '85 152', '151 235',
                                                 '236 150']},
                                      {'color': 'white', 'by_now': '351/1400', 'by_end': '1051/1400',
                                       'now': 'white 1/1',
                                       'lines': ['117 134', '133 167', '168 205', '206 182', '181 200', '199 182',
                                                 '181 209', '210 180', '179 212', '211 179', '180 201', '202 179',
                                                 '180 207', '208 191', '192 206', '205 183', '184 198', '197 155',
                                                 '156 100', '99 113', '114 98', '97 117', '118 147', '148 114',
                                                 '113 154', '153 102', '101 155', '156 98', '97 136', '135 151',
                                                 '152 114', '113 136', '135 114', '113 165', '166 152', '151 103',
                                                 '104 150', '149 107', '108 138', '137 166', '165 101', '102 155',
                                                 '156 220', '219 21', '22 250', '249 227', '228 247', '248 31',
                                                 '32 243', '244 229', '230 17', '18 220', '219 250', '249 24', '23 227',
                                                 '228 18', '17 251', '252 15', '16 221', '222 7', '8 215', '216 178',
                                                 '177 213', '214 176', '175 217', '218 22', '21 251', '252 224',
                                                 '223 4', '3 224', '223 24', '23 239', '240 224', '223 161', '162 99',
                                                 '100 161', '162 220', '219 19', '20 5', '6 217', '218 157', '158 99',
                                                 '100 152', '151 117', '118 133', '134 152', '151 102', '101 160',
                                                 '159 98', '97 132', '131 168', '167 208', '207 178', '177 208',
                                                 '207 167', '168 123', '124 141', '142 106', '105 144', '143 119',
                                                 '120 146', '145 4', '3 146', '145 104', '103 150', '149 105',
                                                 '106 140', '139 1', '2 226', '225 26', '25 238', '237 30', '29 244',
                                                 '243 22', '21 227', '228 191', '192 227', '228 164', '163 218',
                                                 '217 4', '3 138', '137 109', '110 165', '166 209', '210 176',
                                                 '175 215', '216 7', '8 161', '162 222', '221 158', '157 224', '223 15',
                                                 '16 163', '164 15', '16 232', '231 246', '245 28', '27 221', '222 26',
                                                 '25 228', '227 251', '252 135', '136 251', '252 132', '131 186',
                                                 '185 204', '203 160', '159 214', '213 178', '177 202', '201 55',
                                                 '56 199', '200 163', '164 114', '113 160', '159 219', '220 153',
                                                 '154 3', '4 26', '25 226', '225 158', '157 101', '102 170', '169 104',
                                                 '103 146', '145 122', '121 142', '141 252', '251 125', '126 28',
                                                 '27 248', '247 230', '229 22', '21 121', '122 222', '221 165',
                                                 '166 219', '220 28', '27 124', '123 185', '186 61', '62 185', '186 43',
                                                 '44 185', '186 200', '199 55', '56 195', '196 73', '74 207', '208 182',
                                                 '181 112', '111 155', '156 225', '226 24', '23 217', '218 177',
                                                 '178 22', '21 169', '170 204', '203 68', '67 191', '192 69', '70 194',
                                                 '193 47', '48 191', '192 66', '65 204', '203 66', '65 188', '187 64',
                                                 '63 188', '187 129', '130 252', '251 133', '134 4', '3 147', '148 117',
                                                 '118 217', '218 117', '118 164', '163 99', '100 151', '152 190',
                                                 '189 45', '46 194', '193 71', '72 209', '210 112', '111 149', '150 40',
                                                 '39 149', '150 101', '102 161', '162 11', '12 234', '233 31', '32 128',
                                                 '127 2', '1 15', '16 244', '243 220', '219 176', '175 63', '64 174',
                                                 '173 109', '110 167', '168 106', '105 157', '158 216', '215 11',
                                                 '12 163', '164 98', '97 157', '158 222', '221 8', '7 160', '159 103',
                                                 '104 174', '173 23', '24 124', '123 25', '26 235', '236 31', '32 135',
                                                 '136 2', '1 218', '217 17', '18 240', '239 139', '140 38', '37 147',
                                                 '148 50', '49 195', '196 51', '52 200', '199 120', '119 163',
                                                 '164 222', '221 25', '26 129', '130 106', '105 143', '144 4', '3 225',
                                                 '226 157', '158 211', '212 173', '174 22', '21 175', '176 20',
                                                 '19 223', '224 159', '160 10', '9 150', '149 48', '47 192', '191 86',
                                                 '85 209', '210 71', '72 206', '205 162', '161 13', '14 233', '234 252',
                                                 '251 150', '149 113', '114 144', '143 5', '6 162', '161 98', '97 152',
                                                 '151 41', '42 170', '169 59', '60 184', '183 197', '198 76', '75 206',
                                                 '205 179', '180 55', '56 157', '158 110', '109 123', '124 225',
                                                 '226 252', '251 94', '93 252', '251 130', '129 34', '33 127',
                                                 '128 204', '203 181', '182 57', '58 154', '153 251', '252 128',
                                                 '127 30', '29 239', '240 89', '90 248', '247 145', '146 245',
                                                 '246 131', '132 185', '186 122', '121 23', '24 218', '217 165',
                                                 '166 99', '100 144', '143 43', '44 142', '141 238', '237 142', '141 6',
                                                 '5 222', '221 160', '159 229', '230 163', '164 210', '209 113',
                                                 '114 208', '207 88', '87 245', '246 111', '112 211', '212 74',
                                                 '73 208', '207 59', '60 200', '199 90', '89 194', '193 52', '51 147',
                                                 '148 105', '106 243', '244 93', '94 243', '244 148', '147 4', '3 30',
                                                 '29 10', '9 30', '29 15', '16 117', '118 146', '145 35', '36 131',
                                                 '132 28', '27 133', '134 7', '8 214', '213 161', '162 202', '201 54',
                                                 '53 204', '203 172', '171 101', '102 131', '132 205', '206 168',
                                                 '167 19', '20 222', '221 248', '247 32', '31 235', '236 222',
                                                 '221 151', '152 2', '1 97', '98 148', '147 2', '1 177', '178 69',
                                                 '70 177', '178 67', '68 190', '189 49', '50 207', '208 87', '88 196',
                                                 '195 45', '46 188', '187 66', '65 177', '178 212', '211 61', '62 210',
                                                 '209 94', '93 249', '250 235', '236 201', '202 129', '130 114',
                                                 '113 141', '142 108', '107 167', '168 100', '99 145', '146 165',
                                                 '166 220', '219 154', '153 42', '41 171', '172 100', '99 156', '155 2',
                                                 '1 30', '29 227', '228 250', '249 220', '219 22', '21 220', '219 252',
                                                 '251 137', '138 34', '33 132', '131 250', '249 151', '152 49',
                                                 '50 150', '149 11', '12 181', '182 200', '199 61', '62 189', '190 43',
                                                 '44 134', '133 5', '6 137', '138 247', '248 123', '124 107', '108 156',
                                                 '155 213', '214 9', '10 164', '163 19', '20 122', '121 28', '27 106',
                                                 '105 169', '170 61', '62 198', '197 72', '71 211', '212 95', '96 11',
                                                 '12 26', '25 175', '176 250', '249 91', '92 231', '232 137', '138 241',
                                                 '242 221', '222 241', '242 83', '84 188', '187 47', '48 145', '146 38',
                                                 '37 137', '138 189', '190 176', '175 220', '219 25', '26 108',
                                                 '107 139', '140 125', '126 34', '33 139', '140 239', '240 148',
                                                 '147 163', '164 101', '102 147', '148 162', '161 221', '222 155',
                                                 '156 57', '58 209', '210 87', '88 205', '206 52', '51 191', '192 90',
                                                 '89 193', '194 169', '170 38', '37 130', '129 4', '3 135', '136 110',
                                                 '109 25', '26 218', '217 178', '177 25', '26 122', '121 223', '224 14',
                                                 '13 225', '226 155', '156 106', '105 173', '174 251', '252 125',
                                                 '126 225', '226 87', '88 197', '198 77', '78 216', '215 5', '6 105',
                                                 '106 182', '181 24', '23 124', '123 143', '144 184', '183 74',
                                                 '73 195', '196 167', '168 109', '110 21', '22 179', '180 73', '74 160',
                                                 '159 215', '216 81', '82 206', '205 63', '64 205', '206 60', '59 185',
                                                 '186 65', '66 176', '175 102', '101 15', '16 199', '200 92', '91 196',
                                                 '195 46', '45 205', '206 115', '116 17', '18 223', '224 127',
                                                 '128 247', '248 229', '230 21', '22 103', '104 241', '242 80',
                                                 '79 181', '182 110', '109 166', '165 112', '111 153', '154 15',
                                                 '16 118', '117 153', '154 49', '50 194', '193 57', '58 200', '199 12',
                                                 '11 213', '214 1', '2 92', '91 246', '245 142', '141 52', '51 204',
                                                 '203 54', '53 150', '149 243', '244 132', '131 208', '207 48',
                                                 '47 146', '145 167', '168 35', '36 148', '147 12', '11 28', '27 217',
                                                 '218 167', '168 195', '196 86', '85 206', '205 89', '90 250',
                                                 '249 138', '137 250', '249 115', '116 182', '181 21', '22 106',
                                                 '105 17', '18 101', '102 171', '172 144', '143 236', '235 144',
                                                 '143 173', '174 103', '104 228', '227 157', '158 217', '218 85',
                                                 '86 211', '212 70', '69 189', '190 52', '51 206', '205 119', '120 96',
                                                 '95 242', '241 17', '18 231', '232 32', '31 251', '252 216', '215 115',
                                                 '116 13', '14 161', '162 13', '14 111', '112 245', '246 140',
                                                 '139 188', '187 86', '85 246', '245 176', '175 246', '245 93',
                                                 '94 202', '201 182', '181 41', '42 136', '135 208', '207 243',
                                                 '244 177', '178 24', '23 101', '102 156', '155 41', '42 154', '153 47',
                                                 '48 204', '203 120', '119 14', '13 151', '152 220', '219 163', '164 8',
                                                 '7 136', '135 29', '30 133', '134 115']},
                                      {'color': 'black', 'by_now': '1051/1400', 'by_end': '1400/1400',
                                       'now': 'black 2/2',
                                       'lines': ['149 234', '233 147', '148 231', '232 147', '148 87', '88 44',
                                                 '43 222', '221 39', '40 107', '108 52', '51 68', '67 1', '2 65',
                                                 '66 6', '5 124', '123 12', '11 133', '134 56', '55 135', '136 74',
                                                 '73 5', '6 117', '118 9', '10 127', '128 53', '54 89', '90 40',
                                                 '39 213', '214 106', '105 212', '211 102', '101 209', '210 34',
                                                 '33 159', '160 27', '28 88', '87 45', '46 160', '159 36', '35 206',
                                                 '205 41', '42 209', '210 103', '104 45', '46 218', '217 32', '31 78',
                                                 '77 175', '176 92', '91 185', '186 103', '104 38', '37 220', '219 44',
                                                 '43 107', '108 223', '224 33', '34 158', '157 241', '242 153',
                                                 '154 237', '238 40', '39 101', '102 187', '188 91', '92 184', '183 96',
                                                 '95 53', '54 122', '121 57', '58 72', '71 164', '163 68', '67 167',
                                                 '168 96', '95 187', '188 21', '22 194', '193 23', '24 93', '94 192',
                                                 '191 9', '10 83', '84 62', '61 14', '13 83', '84 52', '51 214',
                                                 '213 49', '50 126', '125 53', '54 239', '240 42', '41 210', '209 99',
                                                 '100 59', '60 141', '142 228', '227 144', '143 83', '84 177', '178 95',
                                                 '96 177', '178 86', '85 149', '150 20', '19 132', '131 17', '18 76',
                                                 '75 171', '172 30', '29 159', '160 26', '25 195', '196 22', '21 197',
                                                 '198 39', '40 216', '215 33', '34 223', '224 107', '108 221',
                                                 '222 109', '110 67', '68 252', '251 52', '51 131', '132 77', '78 141',
                                                 '142 14', '13 122', '121 61', '62 141', '142 24', '23 160', '159 22',
                                                 '21 196', '195 17', '18 147', '148 28', '27 89', '90 189', '190 6',
                                                 '5 118', '117 44', '43 162', '161 49', '50 74', '73 138', '137 20',
                                                 '19 151', '152 234', '233 155', '156 245', '246 68', '67 164',
                                                 '163 83', '84 153', '154 230', '229 36', '35 94', '93 23', '24 77',
                                                 '78 174', '173 33', '34 157', '158 25', '26 194', '193 13', '14 135',
                                                 '136 68', '67 138', '137 56', '55 73', '74 47', '48 97', '98 176',
                                                 '175 74', '73 121', '122 52', '51 123', '124 4', '3 120', '119 4',
                                                 '3 188', '187 94', '93 159', '160 40', '39 91', '92 35', '36 207',
                                                 '208 100', '99 199', '200 42', '41 208', '207 45', '46 164', '163 249',
                                                 '250 67', '68 169', '170 30', '29 173', '174 96', '95 27', '28 215',
                                                 '216 46', '45 163', '164 93', '94 59', '60 146', '145 230', '229 110',
                                                 '109 48', '47 162', '161 48', '47 85', '86 169', '170 31', '32 171',
                                                 '172 34', '33 228', '227 37', '38 106', '105 188', '187 92', '91 168',
                                                 '167 97', '98 200', '199 37', '38 220', '219 95', '96 197', '198 44',
                                                 '43 208', '207 102', '101 243', '244 63', '64 145', '146 234',
                                                 '233 150', '149 62', '61 242', '241 153', '154 234', '233 179',
                                                 '180 232', '231 144', '143 72', '71 165', '166 1', '2 189', '190 21',
                                                 '22 138', '137 27', '28 212', '211 30', '29 155', '156 93', '94 168',
                                                 '167 215', '216 58', '57 131', '132 71', '72 188', '187 57', '58 251',
                                                 '252 113', '114 48', '47 211', '212 37', '38 93', '94 183', '184 103',
                                                 '104 235', '236 43', '44 126', '125 192', '191 11', '12 124', '123 65',
                                                 '66 148', '147 88', '87 150', '149 27', '28 196', '195 23', '24 192',
                                                 '191 76', '75 130', '129 12', '11 121', '122 56', '55 221', '222 42',
                                                 '41 100', '99 239', '240 98', '97 225', '226 143', '144 81', '82 67',
                                                 '68 185', '186 250', '249 70', '69 134', '133 10', '9 126', '125 77',
                                                 '78 119', '120 77', '78 11', '12 76', '75 174', '173 7', '8 192',
                                                 '191 61', '62 120', '119 2', '1 51', '52 130', '129 194', '193 130',
                                                 '129 76', '75 25', '26 136', '135 76', '75 2', '1 169', '170 85',
                                                 '86 17', '18 145', '146 16', '15 141', '142 59', '60 17', '18 183',
                                                 '184 53', '54 161', '162 176', '175 35', '36 234', '233 156',
                                                 '155 243', '244 158', '157 245', '246 185', '186 245', '246 155',
                                                 '156 25']}]}

input_lines_group = {'path': 'lines/lines-face-10.pdf',
                     'stats': [{'color': 'white', 'distance': '0.33 km'}, {'color': 'black', 'distance': '0.37 km'}],
                     'lines': [
                         {'color': 'black', 'by_now': '0/1400', 'by_end': '351/1400', 'now': 'black 1/2',
                          'lines': ['172 106', '105 57', '58 122', '121 59', '60 120', '119 53', '54 118', '117 62',
                                    '61 119',
                                    '120 52',
                                    '51 122', '121 56', '55 122', '121 49', '50 122', '121 57', '58 115', '116 63',
                                    '64 131',
                                    '132 74',
                                    '73 238', '237 74', '73 239', '240 77', '78 137', '138 72', '71 140', '139 71',
                                    '72 236',
                                    '235 73',
                                    '74 238', '237 75', '76 131', '132 61', '62 139', '140 69', '70 134', '133 73',
                                    '74 239',
                                    '240 74',
                                    '73 137', '138 76', '75 238', '237 77', '78 130', '129 79', '80 136', '135 74',
                                    '73 237',
                                    '238 76',
                                    '75 239', '240 73', '74 141', '142 70', '69 141', '142 73', '74 136', '135 81',
                                    '82 134',
                                    '133 85',
                                    '86 132', '131 87', '88 130', '129 53', '54 124', '123 48', '47 122', '121 52',
                                    '51 113',
                                    '114 56',
                                    '55 117', '118 210', '209 117', '118 50', '49 123', '124 52', '51 125', '126 53',
                                    '54 107',
                                    '108 59',
                                    '60 107', '108 53', '54 115', '116 53', '54 134', '133 60', '59 113', '114 57',
                                    '58 110',
                                    '109 52',
                                    '51 117', '118 211', '212 119', '120 211', '212 120', '119 210', '209 116',
                                    '115 55',
                                    '56 136',
                                    '135 57', '58 137', '138 70', '69 143', '144 68', '67 142', '141 71', '72 238',
                                    '237 79',
                                    '80 238',
                                    '237 76', '75 236', '235 72', '71 136', '135 79', '80 240', '239 77', '78 238',
                                    '237 81',
                                    '82 239',
                                    '240 76', '75 241', '242 79', '80 141', '142 79', '80 138', '137 71', '72 239',
                                    '240 78',
                                    '77 242',
                                    '241 78', '77 238', '237 78', '77 140', '139 75', '76 239', '240 75', '76 144',
                                    '143 66',
                                    '65 144',
                                    '143 71', '72 149', '150 74', '73 236', '235 74', '73 140', '139 79', '80 133',
                                    '134 85',
                                    '86 137',
                                    '138 61', '62 106', '105 55', '56 131', '132 82', '81 238', '237 72', '71 146',
                                    '145 68',
                                    '67 147',
                                    '148 70', '69 139', '140 61', '62 132', '131 52', '51 128', '127 50', '49 119',
                                    '120 48',
                                    '47 125',
                                    '126 45', '46 123', '124 45', '46 116', '115 208', '207 114', '113 61', '62 140',
                                    '139 61',
                                    '62 136',
                                    '135 72', '71 131', '132 93', '94 42', '41 96', '95 43', '44 110', '109 56',
                                    '55 136',
                                    '135 56',
                                    '55 131', '132 54', '53 122', '121 54', '53 134', '133 57', '58 103', '104 61',
                                    '62 138',
                                    '137 82',
                                    '81 239', '240 79', '80 242', '241 74', '73 241', '242 78', '77 236', '235 75',
                                    '76 236',
                                    '235 76',
                                    '75 242', '241 76', '75 134', '133 53', '54 111', '112 57', '58 138', '137 63',
                                    '64 142',
                                    '141 85',
                                    '86 24', '23 85', '86 136', '135 90', '89 28', '27 88', '87 129', '130 57', '58 96',
                                    '95 147',
                                    '148 74', '73 234', '233 72', '71 145', '146 68', '67 141', '142 76', '75 145',
                                    '146 85',
                                    '86 138',
                                    '137 59', '60 140', '139 82', '81 240', '239 79', '80 239', '240 82', '81 153',
                                    '154 80',
                                    '79 243',
                                    '244 80', '79 238', '237 82', '81 131', '132 51', '52 116', '115 209', '210 117',
                                    '118 209',
                                    '210 116', '115 210', '209 119', '120 213', '214 119', '120 210', '209 120',
                                    '119 211',
                                    '212 117',
                                    '118 212', '211 116', '115 47', '48 109', '110 40', '39 106', '105 49', '50 114',
                                    '113 207',
                                    '208 116', '115 207', '208 118', '117 214', '213 119', '120 43', '44 119',
                                    '120 215',
                                    '216 119',
                                    '120 46', '45 117', '118 206', '205 113', '114 208', '207 119', '120 58', '57 138',
                                    '137 60',
                                    '59 103', '104 41', '42 121', '122 44', '43 124', '123 57', '58 130', '129 49',
                                    '50 109',
                                    '110 47',
                                    '48 115', '116 60', '59 117', '118 215', '216 120', '119 208', '207 117', '118 214',
                                    '213 118',
                                    '117 211', '212 121', '122 41', '42 96', '95 31', '32 98', '97 32', '31 96',
                                    '95 33',
                                    '34 89',
                                    '90 34', '33 98', '97 61', '62 143', '144 73', '74 236', '235 78', '77 241',
                                    '242 74',
                                    '73 233',
                                    '234 72', '71 238', '237 80', '79 151', '152 79', '80 143', '144 90', '89 38',
                                    '37 91',
                                    '92 133',
                                    '134 79', '80 243', '244 81', '82 238', '237 83', '84 240', '239 78', '77 136']},
                         {'color': 'white', 'by_now': '351/1400', 'by_end': '1051/1400', 'now': 'white 1/1',
                          'lines': ['117 189', '190 121', '122 198', '197 125', '126 193', '194 125', '126 201',
                                    '202 125',
                                    '126 196',
                                    '195 123', '124 203', '204 147', '148 202', '201 122', '121 192', '191 44', '43 72',
                                    '71 250',
                                    '249 65', '66 247', '248 69', '70 252', '251 68', '67 252', '251 71', '72 37',
                                    '38 248',
                                    '247 71',
                                    '72 249', '250 62', '61 243', '244 183', '184 240', '239 181', '182 238', '237 185',
                                    '186 236',
                                    '235 188', '187 235', '236 179', '180 235', '236 178', '177 224', '223 17',
                                    '18 225',
                                    '226 176',
                                    '175 122', '121 203', '204 124', '123 193', '194 127', '128 201', '202 122',
                                    '121 197',
                                    '198 124',
                                    '123 169', '170 199', '200 154', '153 201', '202 168', '167 124', '123 201',
                                    '202 136',
                                    '135 196',
                                    '195 124', '123 199', '200 186', '185 10', '9 211', '212 14', '13 217', '218 15',
                                    '16 70',
                                    '69 246',
                                    '245 70', '69 46', '45 70', '69 250', '249 66', '65 241', '242 68', '67 246',
                                    '245 71',
                                    '72 5',
                                    '6 213', '214 4', '3 67', '68 248', '247 41', '42 251', '252 68', '67 244',
                                    '243 68',
                                    '67 248',
                                    '247 13', '14 219', '220 13', '14 215', '216 15', '16 214', '213 8', '7 180',
                                    '179 198',
                                    '197 187',
                                    '188 195', '196 162', '161 198', '197 123', '124 192', '191 43', '44 245', '246 71',
                                    '72 251',
                                    '252 69', '70 247', '248 12', '11 182', '181 9', '10 211', '212 5', '6 180',
                                    '179 8',
                                    '7 219',
                                    '220 96', '95 220', '219 173', '174 35', '36 173', '174 222', '221 12', '11 207',
                                    '208 160',
                                    '159 124', '123 205', '206 142', '141 193', '194 126', '125 200', '199 155',
                                    '156 218',
                                    '217 3',
                                    '4 248', '247 53', '54 69', '70 243', '244 70', '69 20', '19 226', '225 173',
                                    '174 198',
                                    '197 182',
                                    '181 233', '234 183', '184 201', '202 121', '122 203', '204 126', '125 139',
                                    '140 200',
                                    '199 120',
                                    '119 194', '193 127', '128 204', '203 134', '133 205', '206 122', '121 194',
                                    '193 124',
                                    '123 200',
                                    '199 142', '141 201', '202 120', '119 176', '175 35', '36 249', '250 3', '4 223',
                                    '224 100',
                                    '99 223', '224 101', '102 233', '234 189', '190 41', '42 189', '190 45', '46 68',
                                    '67 50',
                                    '49 244',
                                    '243 51', '52 248', '247 69', '70 246', '245 59', '60 68', '67 56', '55 246',
                                    '245 182',
                                    '181 12',
                                    '11 249', '250 31', '32 165', '166 31', '32 162', '161 218', '217 9', '10 181',
                                    '182 7',
                                    '8 71',
                                    '72 18', '17 221', '222 97', '98 221', '222 168', '167 33', '34 165', '166 199',
                                    '200 122',
                                    '121 201', '202 140', '139 194', '193 39', '40 69', '70 242', '241 63', '64 242',
                                    '241 68',
                                    '67 62',
                                    '61 242', '241 183', '184 194', '193 45', '46 249', '250 5', '6 249', '250 44',
                                    '43 246',
                                    '245 67',
                                    '68 63', '64 239', '240 180', '179 121', '122 205', '206 12', '11 210', '209 13',
                                    '14 184',
                                    '183 195', '196 125', '126 199', '200 50', '49 198', '197 124', '123 202',
                                    '201 124',
                                    '123 132',
                                    '131 197', '198 171', '172 32', '31 163', '164 30', '29 251', '252 151', '152 218',
                                    '217 92',
                                    '91 230', '229 21', '22 229', '230 97', '98 231', '232 100', '99 233', '234 160',
                                    '159 58',
                                    '57 158',
                                    '157 29', '30 163', '164 219', '220 98', '97 221', '222 8', '7 247', '248 5',
                                    '6 223',
                                    '224 84',
                                    '83 225', '226 184', '183 8', '7 211', '212 54', '53 156', '155 198', '197 188',
                                    '187 38',
                                    '37 177',
                                    '178 8', '7 157', '158 31', '32 247', '248 71', '72 246', '245 48', '47 238',
                                    '237 184',
                                    '183 13',
                                    '14 185', '186 198', '197 126', '125 154', '153 1', '2 152', '151 227', '228 87',
                                    '88 224',
                                    '223 100', '99 232', '231 156', '155 52', '51 70', '69 62', '61 71', '72 59',
                                    '60 244',
                                    '243 69',
                                    '70 249', '250 150', '149 201', '202 126', '125 204', '203 123', '124 205',
                                    '206 123',
                                    '124 142',
                                    '141 215', '216 91', '92 233', '234 98', '97 212', '211 56', '55 68', '67 242',
                                    '241 177',
                                    '178 195',
                                    '196 186', '185 199', '200 161', '162 29', '30 248', '247 72', '71 33', '34 172',
                                    '171 195',
                                    '196 127', '128 122', '121 169', '170 32', '31 160', '159 35', '36 70', '69 242',
                                    '241 146',
                                    '145 123', '124 209', '210 12', '11 221', '222 82', '81 220', '219 94', '93 218',
                                    '217 158',
                                    '157 55', '56 243', '244 68', '67 249', '250 9', '10 184', '183 15', '16 189',
                                    '190 7',
                                    '8 180',
                                    '179 197', '198 125', '126 209', '210 165', '166 33', '34 163', '164 240',
                                    '239 165',
                                    '166 60',
                                    '59 158', '157 56', '55 162', '161 30', '29 249', '250 4', '3 251', '252 27',
                                    '28 175',
                                    '176 38',
                                    '37 188', '187 194', '193 188', '187 195', '196 170', '169 201', '202 129',
                                    '130 200',
                                    '199 124',
                                    '123 208', '207 122', '121 204', '203 125', '126 195', '196 49', '50 155',
                                    '156 197',
                                    '198 120',
                                    '119 192', '191 40', '39 246', '245 181', '182 14', '13 205', '206 166', '165 38',
                                    '37 173',
                                    '174 36', '35 181', '182 9', '10 222', '221 96', '95 230', '229 88', '87 227',
                                    '228 86',
                                    '85 226',
                                    '225 102', '101 225', '226 91', '92 234', '233 100', '99 222', '221 175', '176 40',
                                    '39 237',
                                    '238 33', '34 158', '157 54', '53 69', '70 11', '12 180', '179 34', '33 246',
                                    '245 54',
                                    '53 72',
                                    '71 62', '61 67', '68 64', '63 66', '65 216', '215 135', '136 206', '205 121',
                                    '122 158',
                                    '157 232',
                                    '231 96', '95 221', '222 98', '97 220', '219 5', '6 250', '249 7', '8 218',
                                    '217 165',
                                    '166 18',
                                    '17 248', '247 30', '29 163', '164 61', '62 213', '214 55', '56 161', '162 33',
                                    '34 169',
                                    '170 33',
                                    '34 68', '67 243', '244 72', '71 242', '241 148', '147 121', '122 204', '203 120',
                                    '119 180',
                                    '179 194', '193 180', '179 41', '42 188', '187 17', '18 220', '219 160', '159 220',
                                    '219 175',
                                    '176 197', '198 130', '129 124', '123 173', '174 27', '28 233', '234 91', '92 231',
                                    '232 90',
                                    '89 225', '226 103', '104 227', '228 186', '185 231', '232 101', '102 224',
                                    '223 169',
                                    '170 23',
                                    '24 230', '229 154', '153 48', '47 246', '245 66', '65 246', '245 175', '176 66',
                                    '65 250',
                                    '249 2',
                                    '1 155', '156 52', '51 154', '153 47', '48 199', '200 173', '174 64', '63 70',
                                    '69 244',
                                    '243 71',
                                    '72 252', '251 4', '3 248', '247 10', '9 158', '157 31', '32 171', '172 194',
                                    '193 49',
                                    '50 198',
                                    '197 162', '161 62', '61 160', '159 121', '122 129', '130 195', '196 122',
                                    '121 198',
                                    '197 122',
                                    '121 134', '133 123', '124 200', '199 129', '130 30', '29 72', '71 60', '59 210',
                                    '209 10',
                                    '9 248',
                                    '247 22', '21 249', '250 25', '26 176', '175 227', '228 22', '21 169', '170 20',
                                    '19 251',
                                    '252 149',
                                    '150 43', '44 214', '213 98', '97 232', '231 94', '93 206', '205 128', '127 192',
                                    '191 20',
                                    '19 193',
                                    '194 189', '190 6', '5 181', '182 242', '241 67', '68 246', '245 39', '40 67',
                                    '68 27',
                                    '28 163',
                                    '164 36', '35 168', '167 59', '60 160', '159 33', '34 135', '136 33', '34 181',
                                    '182 85',
                                    '86 225',
                                    '226 83', '84 227', '228 154', '153 3', '4 187', '188 14', '13 181', '182 199',
                                    '200 120',
                                    '119 200',
                                    '199 47', '48 143', '144 238', '237 102', '101 214', '213 58', '57 164', '163 195',
                                    '196 184',
                                    '183 11', '12 187', '188 41', '42 178', '177 28', '27 148', '147 237', '238 145',
                                    '146 122',
                                    '121 206', '205 125', '126 239', '240 66', '65 248', '247 38', '37 166', '165 56',
                                    '55 244',
                                    '243 66', '65 175', '176 29', '30 162', '161 53', '54 155', '156 28', '27 166',
                                    '165 242',
                                    '241 171',
                                    '172 223', '224 103', '104 238', '237 162', '161 240', '239 144', '143 25',
                                    '26 248',
                                    '247 177',
                                    '178 83', '84 221', '222 83', '84 188', '187 227', '228 149', '150 218', '217 94',
                                    '93 234',
                                    '233 145', '146 198', '197 27', '28 168', '167 221', '222 81', '82 225', '226 88',
                                    '87 223',
                                    '224 20', '19 171', '172 22', '21 138', '137 35', '36 134', '133 32', '31 246',
                                    '245 69',
                                    '70 61',
                                    '62 169', '170 219', '220 99', '100 213', '214 128', '127 201', '202 10']},
                         {'color': 'black', 'by_now': '1051/1400', 'by_end': '1400/1400', 'now': 'black 2/2',
                          'lines': ['135 63', '64 145', '146 66', '65 147', '148 98', '97 34', '33 102', '101 202',
                                    '201 99',
                                    '100 36',
                                    '35 101', '102 63', '64 141', '142 61', '62 144', '143 77', '78 243', '244 86',
                                    '85 241',
                                    '242 76',
                                    '75 137', '138 84', '83 238', '237 71', '72 240', '239 83', '84 238', '237 84',
                                    '83 241',
                                    '242 81',
                                    '82 130', '129 48', '47 118', '117 218', '217 120', '119 206', '205 117', '118 218',
                                    '217 118',
                                    '117 219', '220 119', '120 214', '213 116', '115 214', '213 113', '114 210',
                                    '209 106',
                                    '105 56',
                                    '55 109', '110 205', '206 112', '111 206', '205 115', '116 56', '55 132', '131 96',
                                    '95 161',
                                    '162 104', '103 203', '204 118', '117 49', '50 125', '126 46', '45 121', '122 38',
                                    '37 97',
                                    '98 29',
                                    '30 91', '92 36', '35 91', '92 29', '30 97', '98 158', '157 86', '85 159', '160 87',
                                    '88 159',
                                    '160 43', '44 127', '128 52', '51 119', '120 222', '221 120', '119 215', '216 118',
                                    '117 208',
                                    '207 118', '117 204', '203 102', '101 60', '59 134', '133 54', '53 113', '114 206',
                                    '205 119',
                                    '120 47', '48 106', '105 210', '209 114', '113 52', '51 134', '133 82', '81 241',
                                    '242 82',
                                    '81 243',
                                    '244 79', '80 149', '150 75', '76 245', '246 76', '75 234', '233 74', '73 242',
                                    '241 79',
                                    '80 140',
                                    '139 58', '57 108', '107 61', '62 96', '95 23', '24 181', '182 24', '23 181',
                                    '182 23',
                                    '24 94',
                                    '93 156', '155 102', '101 168', '167 106', '105 158', '157 92', '91 171', '172 14',
                                    '13 173',
                                    '174 18', '17 174', '173 16', '15 174', '173 104', '103 208', '207 102', '101 34',
                                    '33 151',
                                    '152 40', '39 90', '89 162', '161 46', '45 129', '130 56', '55 137', '138 95',
                                    '96 159',
                                    '160 44',
                                    '43 223', '224 46', '45 111', '112 212', '211 121', '122 40', '39 158', '157 38',
                                    '37 111',
                                    '112 211', '212 116', '115 218', '217 117', '118 203', '204 112', '111 211',
                                    '212 110',
                                    '109 60',
                                    '59 139', '140 75', '76 228', '227 72', '71 236', '235 80', '79 198', '197 78',
                                    '77 247',
                                    '248 78',
                                    '77 151', '152 102', '101 32', '31 90', '89 165', '166 107', '108 58', '57 128',
                                    '127 46',
                                    '45 95',
                                    '96 179', '180 22', '21 179', '180 24', '23 179', '180 21', '22 178', '177 19',
                                    '20 178',
                                    '177 21',
                                    '22 86', '85 240', '239 86', '85 239', '240 83', '84 239', '240 90', '89 153',
                                    '154 41',
                                    '42 115',
                                    '116 206', '205 99', '100 206', '205 118', '117 206', '205 111', '112 49', '50 130',
                                    '129 60',
                                    '59 141', '142 63', '64 146', '145 79', '80 196', '195 74', '73 228', '227 74',
                                    '73 194',
                                    '193 71',
                                    '72 232', '231 72', '71 209', '210 103', '104 159', '160 85', '86 14', '13 172',
                                    '171 45',
                                    '46 162',
                                    '161 83', '84 244', '243 82', '81 245', '246 78', '77 154', '153 41', '42 155',
                                    '156 36',
                                    '35 123',
                                    '124 56', '55 135', '136 54', '53 111', '112 35', '36 221', '222 39', '40 158',
                                    '157 106',
                                    '105 154',
                                    '153 100', '99 28', '27 93', '94 149', '150 103', '104 207', '208 113', '114 215',
                                    '216 116',
                                    '115 206', '205 100', '99 164', '163 87', '88 33', '34 152', '151 36', '35 155',
                                    '156 91',
                                    '92 167',
                                    '168 89', '90 134', '133 52', '51 105', '106 151', '152 71', '72 229', '230 77',
                                    '78 236',
                                    '235 69',
                                    '70 236', '235 71', '72 194', '193 69', '70 207', '208 69', '70 144', '143 91',
                                    '92 21',
                                    '22 84',
                                    '83 197', '198 113', '114 44', '43 164', '163 84', '83 242', '241 84', '83 243',
                                    '244 75',
                                    '76 194',
                                    '193 75', '76 132', '131 48', '47 162', '161 102', '101 163', '164 41', '42 117',
                                    '118 219',
                                    '220 117', '118 202', '201 117', '118 221', '222 40', '39 153', '154 71', '72 228',
                                    '227 66',
                                    '65 226', '225 55', '56 137', '138 63', '64 135', '136 89', '90 20', '19 176',
                                    '175 16',
                                    '15 175',
                                    '176 20', '19 175', '176 18', '17 175', '176 95', '96 44', '43 156', '155 99',
                                    '100 148',
                                    '147 72',
                                    '71 207', '208 105']}]}

response = build_gcode('circle', [100, 100], input_lines_circle_group, None, 252, 0, 5, 2)

# response = build_gcode('rectangle', [100, 100], input_lines_group, sides, 252, 0, 5, 2)

for linea in response['g_code_niels']:
    print(linea)

for g_codes_group in response['g_codes_groups']:
    print(g_codes_group['color'] + "\n")
    for lines in g_codes_group['gcode']:
        print(lines)

# for g_codes_group in g_codes_groups:
#     print(g_codes_group['color'] + "\n")
#     for lines in g_codes_group['gcode']:
#         print(lines)

# gcode = generate_gcode(sides_niels['sides_coordinates'], 0, 2)
# for linea in gcode:
#     print(linea)

# Centro del círculo y radio
# size = 100
# radius = size / 2
# center = (radius, radius)  # Centro del área de trabajo de 100x100 mm
# nail_quantity = 252  # Cantidad de clavos

# Generar los puntos en la circunferencia
# points = generate_circle_points(center, radius, nail_quantity)

# Generar el G-code para los puntos
# gcode = generate_circle_gcode(points, 0, 2)
# for linea in gcode:
#     print(linea)

# g_codes_groups = generate_circle_gcode_lines(input_lines_circle_group['lines'], points, radius, nail_quantity, 0, 5, 2)
# for g_codes_group in g_codes_groups:
#     print(g_codes_group['color'] + "\n")
#     for lines in g_codes_group['gcode']:
#         print(lines)
