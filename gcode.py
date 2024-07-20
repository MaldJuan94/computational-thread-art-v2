def build_cnc_niels(width, height, sides_list):
    left_points = [key for key, value in sides_list.items() if value == 2]
    top_points = [key for key, value in sides_list.items() if value == 1]
    right_points = [key for key, value in sides_list.items() if value == 0]
    bottom_points = [key for key, value in sides_list.items() if value == 3]

    left_points_coordinates = generate_points_line((0, 0), (0, height), len(left_points))[::-1]
    top_points_coordinates = generate_points_line((0, height), (width, height), len(top_points))[::-1]
    right_points_coordinates = generate_points_line((width, height), (width, 0), len(right_points))[::-1]
    bottom_points_coordinates = generate_points_line((width, 0), (0, 0), len(bottom_points))[::-1]

    return update_sides(sides_list, left_points, top_points, right_points, bottom_points, left_points_coordinates,
                        top_points_coordinates, right_points_coordinates, bottom_points_coordinates)


def update_sides(sides_list, left_points, top_points, right_points, bottom_points, left_points_coordinates,
                 top_points_coordinates, right_points_coordinates, bottom_points_coordinates):
    for idx, point in enumerate(left_points):
        sides_list[point] = left_points_coordinates[idx]

    for idx, point in enumerate(right_points):
        sides_list[point] = right_points_coordinates[idx]

    for idx, point in enumerate(top_points):
        sides_list[point] = top_points_coordinates[idx]

    for idx, point in enumerate(bottom_points):
        sides_list[point] = bottom_points_coordinates[idx]

    return sides_list


def generate_points_line(start, end, nail_quantity):
    x1, y1 = start
    x2, y2 = end
    return [(x1 + (x2 - x1) * (i + 1) / (nail_quantity + 1), y1 + (y2 - y1) * (i + 1) / (nail_quantity + 1)) for i in
            range(nail_quantity)]


def generate_gcode(sides_list, drawing_depth,
                   safe_height):
    g_code = []

    # Comenzar el G-code
    g_code.append("G90 ; Usar coordenadas absolutas")
    g_code.append("G21 ; Usar unidades en milímetros")

    g_code.append(f"G0 Z{safe_height:.2f}; Subir a altura segura")
    for key, (x, y) in sides_list.items():
        g_code.append(f"G0 X{x:.2f} Y{y:.2f} ; Punto {key} Mover a la posición")
        g_code.append(f"G1 Z{-drawing_depth:.2f}; Bajar la herramienta para perforar")
        g_code.append(f"G0 Z{safe_height:.2f}; Subir a altura segura")

    # Finalizar el G-code
    g_code.append("G0 Z10 ; Subir la herramienta")
    g_code.append("M30 ; Final del programa")

    return g_code


original_sides = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0,
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

sides = build_cnc_niels(500, 500, original_sides)

gcode = generate_gcode(sides, 5, 10)
for linea in gcode:
    print(linea)

# Dividir los puntos según el lado
# puntos_derecho = [key for key, value in sides.items() if value == 0]
# puntos_superior = [key for key, value in sides.items() if value == 1]
# puntos_izquierdo = [key for key, value in sides.items() if value == 2]
# puntos_inferior = [key for key, value in sides.items() if value == 3]
#
# print(sides.items())


# def generar_puntos_recta(inicio, fin, cantidad):
#     x1, y1 = inicio
#     x2, y2 = fin
#     return [(x1 + (x2 - x1) * (i + 1) / (cantidad + 1), y1 + (y2 - y1) * (i + 1) / (cantidad + 1)) for i in
#             range(cantidad)]


# Generar los puntos para cada lado, sin incluir esquinas
# puntos_izquierdo_coordenadas = generar_puntos_recta((0, 0), (0, altura), len(puntos_izquierdo))[::-1]
# puntos_superior_coordenadas = generar_puntos_recta((0, altura), (anchura, altura), len(puntos_superior))[::-1]
# puntos_derecho_coordenadas = generar_puntos_recta((anchura, altura), (anchura, 0), len(puntos_derecho))[::-1]
# puntos_inferior_coordenadas = generar_puntos_recta((anchura, 0), (0, 0), len(puntos_inferior))[::-1]

# Actualizar el diccionario sides con las coordenadas generadas
# for idx, punto in enumerate(puntos_derecho):
#     sides[punto] = puntos_derecho_coordenadas[idx]
#
# for idx, punto in enumerate(puntos_superior):
#     sides[punto] = puntos_superior_coordenadas[idx]
#
# for idx, punto in enumerate(puntos_izquierdo):
#     sides[punto] = puntos_izquierdo_coordenadas[idx]
#
# for idx, punto in enumerate(puntos_inferior):
#     sides[punto] = puntos_inferior_coordenadas[idx]

# Imprimir los puntos generados
# for key, value in sides.items():
#     print(f"Punto {key}: X = {value[0]:.2f}, Y = {value[1]:.2f}")


# def imprimir_puntos(puntos, nombre_lado):
#     print(f"{nombre_lado}:")
#     for i, (x, y) in enumerate(puntos):
#         print(f"Punto {i + 1}: (X: {x:.2f}, Y: {y:.2f})")
#     print()


# Generar el G-code a partir de los puntos
# def generar_gcode(puntos_izquierdo, puntos_superior, puntos_derecho, puntos_inferior, profundidad_perforacion,
#                   altura_segura):
#     gcode = []
#     todos_puntos = puntos_derecho + puntos_superior + puntos_izquierdo + puntos_inferior
#
#     # Comenzar el G-code
#     gcode.append("G90 ; Usar coordenadas absolutas")
#     gcode.append("G21 ; Usar unidades en milímetros")
#
#     gcode.append(f"G0 Z{altura_segura:.2f}; Subir a altura segura")
#     for x, y in todos_puntos:
#         ##gcode.append(f"G0 Z{altura_segura:.2f} ; Subir a altura segura")
#         gcode.append(f"G0 X{x:.2f} Y{y:.2f} ; Mover a la posición")
#         gcode.append(f"G1 Z{-profundidad_perforacion:.2f}; Bajar la herramienta para perforar")
#         gcode.append(f"G0 Z{altura_segura:.2f}; Subir a altura segura")
#
#     # Finalizar el G-code
#     gcode.append("G0 Z10 ; Subir la herramienta")
#     gcode.append("M30 ; Final del programa")
#
#     return gcode


# profundidad_perforacion = 5  # Profundidad de perforación en milímetros
# altura_segura = 10  # Altura segura en milímetros
# gcode = generar_gcode(puntos_izquierdo_coordenadas, puntos_superior_coordenadas, puntos_derecho_coordenadas,
#                       puntos_inferior_coordenadas, profundidad_perforacion,
#                       altura_segura)

# Imprimir el G-code
# for linea in gcode:
#     print(linea)
