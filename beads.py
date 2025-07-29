import random
from PIL import Image
from PyPDF2 import PdfMerger
import cv2
import numpy
from random import randint, shuffle
import math




def beads_processing(length=10, order_conditions=5,relative_order_conditions=5 ,content_conditions=5, equal_conditions=5, true_probability=0.5, colornames = 0, bordersize=100, offset=200, end=100, size=100, between_dist_relative=1, levelsize=300):
    h = 3508
    w = 2480
    # bordersize = 100
    # offset = 200
    # end = 100

    all_beads = {(1, (0, 0, 255)), (1, (0, 255, 0)), (1, (255, 0, 0)), (1, (0, 255, 255)), (1, (255, 255, 0)),
                 (1, (255, 0, 255)),
                 (2, (0, 0, 255)), (2, (0, 255, 0)), (2, (255, 0, 0)), (2, (0, 255, 255)), (2, (255, 255, 0)),
                 (2, (255, 0, 255)),
                 (3, (0, 0, 255)), (3, (0, 255, 0)), (3, (255, 0, 0)), (3, (0, 255, 255)), (3, (255, 255, 0)),
                 (3, (255, 0, 255))
                 }

    colors = {
        (0, 0, 0): "черная",
        (0, 0, 255): "красная",
        (0, 255, 0): "зеленая",
        (255, 0, 0): "синяя",
        (0, 255, 255): "желтая",
        (255, 255, 0): "голубая",
        (255, 0, 255): "фиолетовая"
    }
    types = {
        1: "круглая",
        2: "квадратная",
        3: "треугольная"
    }

    colors_second = {
        (0, 0, 0): "черную",
        (0, 0, 255): "красную",
        (0, 255, 0): "зеленую",
        (255, 0, 0): "синюю",
        (0, 255, 255): "желтую",
        (255, 255, 0): "голубую",
        (255, 0, 255): "фиолетовую"
    }
    types_second = {
        1: "круглую",
        2: "квадратную",
        3: "треугольную"
    }
    colors_third = {
        (0, 0, 0): "черной",
        (0, 0, 255): "красной",
        (0, 255, 0): "зеленой",
        (255, 0, 0): "синей",
        (0, 255, 255): "желтой",
        (255, 255, 0): "голубой",
        (255, 0, 255): "фиолетовой"
    }
    types_third = {
        1: "круглой",
        2: "квадратной",
        3: "треугольной"
    }

    # order_conditions = 5
    # relative_order_conditions = 5
    # content_conditions = 5
    # equal_conditions = 5
    # true_probability = 0.5
    # добавить условия с порядком до 9999 (первая, вторая, ... девять тысяч девятьсот девяносто девятая, предпоследняя, последняя), определение цвета бусины, содержание той или иной бусины, сравнение (или неравенство) 2 бусин

    # between_dist_relative = 1
    # size = 100
    between_dist_relative = between_dist_relative / 100

    max_len = (16 - math.ceil((bordersize) / (1 / between_dist_relative))) * 100 // size
    print(max_len)
    test_size_vertical = 200
    text = "Определи истинность утверждений, напиши буквы И, Л или Н в окнах"
    # text = "Opredeli istinnost utverzhdeniy, napishi bukvi I ili L v oknah"
    # length = 10
    levels = math.ceil(length / max_len)
    print(levels)

    # levelsize = 300


    def triangle(size, x, y, color=(0, 0, 255)):
        nonlocal array, colornames, colors, font
        vertices = numpy.array([[x, y], [x + size // 2, y - size * int(3 ** 0.5)], [x + size, y]])
        cv2.fillPoly(array, [vertices], color=color)
        cv2.polylines(array, [vertices], color=(0, 0, 0), thickness=3, isClosed=1)
        if colornames:
            cv2.putText(array, colors[color][0], (x-40, y+40), font, 2, (0, 0, 0), 2)


    def square(size, x, y, color=(0, 0, 255)):
        nonlocal array, colornames, colors, font
        vertices = numpy.array([[x, y], [x + size, y], [x + size, y - size], [x, y - size]])
        cv2.fillPoly(array, [vertices], color=color)
        cv2.polylines(array, [vertices], color=(0, 0, 0), thickness=3, isClosed=1)
        if colornames:
            cv2.putText(array, colors[color][0], (x-40, y+40), font, 2, (0, 0, 0), 2)



    def circle(size, x, y, color=(0, 0, 255)):
        nonlocal array, colornames, colors, font
        cv2.circle(array, (x + size // 2, y - size // 2), size // 4, color, size // 2)
        cv2.circle(array, (x + size // 2, y - size // 2), size // 2, (0, 0, 0), 2)
        # cv2.fill
        if colornames:
            cv2.putText(array, colors[color][0], (x-40, y+40), font, 2, (0, 0, 0), 2)



    def new_page(pages):
        nonlocal array, h, w

        # cv2.imwrite("newimage.pdf", array)
        if pages:
            image1 = Image.open("newimage.png")
            # im1 = image1.convert('RGB')
            image1.save("newimage2.pdf")

            merger = PdfMerger()

            with open("newimage.pdf", "rb") as main:
                merger.append(main)

            with open("newimage2.pdf", "rb") as out:
                merger.append(out)

            with open("newimage.pdf", "wb") as main:
                merger.write(main)

            # pdf_images = []
            # with Image.open("newimage.pdf") as img:
            #     for page in range(img.n_frames):
            #         img.seek(page)
            #         pdf_images.append(img.copy())
            # png_image = Image.open("newimage.png")
            # pdf_images.append(png_image)
            #
            # pdf_images[0].save("newimage.pdf", save_all=True, append_images=pdf_images[1:])
        else:
            image1 = Image.open("newimage.png")
            # im1 = image1.convert('RGB')
            image1.save("newimage.pdf")


    array = numpy.ones((h, w, 3), dtype=numpy.uint8) * 255
    font = cv2.FONT_HERSHEY_COMPLEX

    cv2.putText(array, text, (bordersize, offset), font, 1.8 / 2280 * (w - 2 * bordersize), (0, 0, 0), 5)

    # array = numpy.array([[(255, 255, 255) for _ in range(w)] for _ in range(h)])

    cv2.line(array, (bordersize, offset + test_size_vertical - 50), (bordersize, offset + test_size_vertical + 150),
             (0, 200, 0), 5)

    for index in range(levels):
        if index == levels - 1 and levels > 1:
            cv2.line(array, (bordersize, offset + test_size_vertical + 50 + index * levelsize), (
            w - bordersize - (max_len - (length - 1) % max_len - 1) * 1950 // 14,
            offset + test_size_vertical + 50 + index * levelsize), (0, 200, 0), 5)
        else:
            cv2.line(array, (bordersize, offset + test_size_vertical + 50 + index * levelsize),
                     (w - bordersize, offset + test_size_vertical + 50 + index * levelsize), (0, 200, 0), 5)

    for index in range(levels - 1):
        cv2.line(array, (bordersize, offset + test_size_vertical + 50 + int((index + 0.5) * levelsize)),
                 (bordersize, offset + test_size_vertical + 50 + (index + 1) * levelsize), (0, 200, 0), 5)
        cv2.line(array, (w - bordersize, offset + test_size_vertical + 50 + index * levelsize),
                 (w - bordersize, offset + test_size_vertical + 50 + int((index + 0.5) * levelsize)), (0, 200, 0), 5)
        cv2.line(array, (bordersize, offset + test_size_vertical + 50 + int((index + 0.5) * levelsize)),
                 (w - bordersize, offset + test_size_vertical + 50 + int((index + 0.5) * levelsize)), (0, 200, 0), 5)

    if length <= max_len:
        cv2.line(array, (w - bordersize, offset + test_size_vertical + 50 + (levels - 1) * levelsize),
                 (w - bordersize - 50, offset + test_size_vertical + (levels - 1) * levelsize), (0, 200, 0), 5)
        cv2.line(array, (w - bordersize, offset + test_size_vertical + 50 + (levels - 1) * levelsize),
                 (w - bordersize - 50, offset + test_size_vertical + 100 + (levels - 1) * levelsize), (0, 200, 0), 5)
    else:
        cv2.line(array, (w - bordersize - (max_len - (length - 1) % max_len - 1) * 1950 // 14,
                         offset + test_size_vertical + 50 + (levels - 1) * levelsize), (
                 w - bordersize - 50 - (max_len - (length - 1) % max_len - 1) * 1950 // 14,
                 offset + test_size_vertical + (levels - 1) * levelsize), (0, 200, 0), 5)
        cv2.line(array, (w - bordersize - (max_len - (length - 1) % max_len - 1) * 1950 // 14,
                         offset + test_size_vertical + 50 + (levels - 1) * levelsize), (
                 w - bordersize - 50 - (max_len - (length - 1) % max_len - 1) * 1950 // 14,
                 offset + test_size_vertical + 100 + (levels - 1) * levelsize), (0, 200, 0), 5)

    # triangle(100, 150, 500, (255, 0, 0))
    # square(100, 300, 500, (0, 255, 0))
    # circle(100, 450, 500)
    #
    # square(100, 2100, 500)

    startx = 50 + bordersize
    endx = 2000 - bordersize
    y = 250 + size // 2 + offset

    figures = []
    if length <= max_len:
        for index in range(length):
            color = (255, 255, 255)
            while color == (255, 255, 255):
                color = (255 * randint(0, 1), 255 * randint(0, 1), 255 * randint(0, 1))

            match randint(1, 3):
                case 1:
                    triangle(size, int(startx + index * ((endx - startx) / (length - 1))), y, color)
                    figures.append((3, color))
                case 2:
                    square(size, int(startx + index * ((endx - startx) / (length - 1))), y, color)
                    figures.append((2, color))
                case 3:
                    circle(size, int(startx + index * ((endx - startx) / (length - 1))), y, color)
                    figures.append((1, color))
    else:
        if length % max_len == 0 and length > max_len:
            levels += 1
        for y_add in range(levels - 1):
            for index in range(max_len):
                color = (255, 255, 255)
                while color == (255, 255, 255):
                    color = (255 * randint(0, 1), 255 * randint(0, 1), 255 * randint(0, 1))

                match randint(1, 3):
                    case 1:
                        triangle(size, int(startx + index * ((endx - startx) / (max_len - 1))), y + y_add * levelsize, color)
                        figures.append((3, color))
                    case 2:
                        square(size, int(startx + index * ((endx - startx) / (max_len - 1))), y + y_add * levelsize, color)
                        figures.append((2, color))
                    case 3:
                        circle(size, int(startx + index * ((endx - startx) / (max_len - 1))), y + y_add * levelsize, color)
                        figures.append((1, color))
        length = length % max_len
        for index in range(length):
            color = (255, 255, 255)
            while color == (255, 255, 255):
                color = (255 * randint(0, 1), 255 * randint(0, 1), 255 * randint(0, 1))

            match randint(1, 3):
                case 1:
                    triangle(size, int(startx + index * ((endx - startx) / (max_len - 1))), y + (levels - 1) * levelsize,
                             color)
                    figures.append((3, color))
                case 2:
                    square(size, int(startx + index * ((endx - startx) / (max_len - 1))), y + (levels - 1) * levelsize,
                           color)
                    figures.append((2, color))
                case 3:
                    circle(size, int(startx + index * ((endx - startx) / (max_len - 1))), y + (levels - 1) * levelsize,
                           color)
                    figures.append((1, color))

    last_y = y + levels * levelsize

    print(figures)

    true_conditions = []
    false_conditions = []
    impossible_conditions = []
    for _ in range(order_conditions):
        if random.random() <= true_probability:
            if randint(0, 1):
                match randint(0, 2):
                    case 0:
                        number = randint(1, len(figures))
                        true_conditions.append(f"бусина под номером {number} {colors.get(figures[number - 1][1])}")
                    case 1:
                        number = randint(1, len(figures))
                        true_conditions.append(f"бусина под номером {number} {types.get(figures[number - 1][0])}")
                    case 2:
                        number = randint(1, len(figures))
                        true_conditions.append(
                            f"бусина под номером {number} {colors.get(figures[number - 1][1])} {types.get(figures[number - 1][0])}")
            else:
                match randint(0, 2):
                    case 0:
                        number = randint(1, len(figures))
                        true_conditions.append(
                            f"бусина под номером {len(figures) - number + 1} с конца {colors.get(figures[number - 1][1])}")
                    case 1:
                        number = randint(1, len(figures))
                        true_conditions.append(
                            f"бусина под номером {len(figures) - number + 1} с конца {types.get(figures[number - 1][0])}")
                    case 2:
                        number = randint(1, len(figures))
                        true_conditions.append(
                            f"бусина под номером {len(figures) - number + 1} с конца {colors.get(figures[number - 1][1])} {types.get(figures[number - 1][0])}")

        else:
            if randint(0, 1):
                match randint(0, 2):
                    case 0:
                        number = randint(1, len(figures))
                        false_conditions.append(
                            f"бусина под номером {number} {colors.get(figures[randint(1, len(figures)) - 1][1])}")
                    case 1:
                        number = randint(1, len(figures))
                        false_conditions.append(
                            f"бусина под номером {number} {types.get(figures[randint(1, len(figures)) - 1][0])}")
                    case 2:
                        number = randint(1, len(figures))
                        false_conditions.append(
                            f"бусина под номером {number} {colors.get(figures[randint(1, len(figures)) - 1][1])} {types.get(figures[randint(1, len(figures)) - 1][0])}")
            else:
                match randint(0, 2):
                    case 0:
                        number = randint(1, len(figures))
                        false_conditions.append(
                            f"бусина под номером {len(figures) - number + 1} с конца {colors.get(figures[randint(1, len(figures)) - 1][1])}")
                    case 1:
                        number = randint(1, len(figures))
                        false_conditions.append(
                            f"бусина под номером {len(figures) - number + 1} с конца {types.get(figures[randint(1, len(figures)) - 1][0])}")
                    case 2:
                        number = randint(1, len(figures))
                        false_conditions.append(
                            f"бусина под номером {len(figures) - number + 1} с конца {colors.get(figures[randint(1, len(figures)) - 1][1])} {types.get(figures[randint(1, len(figures)) - 1][0])}")

    for _ in range(relative_order_conditions):
        if random.random() <= true_probability:
            number1 = randint(1, len(figures))
            number2 = number1
            while number2 == number1:
                number2 = randint(1, len(figures))
            if number2 > number1:
                if figures.count(figures[number1 - 1]) > 1:
                    impossible_conditions.append(
                        f"бусина под номером {abs(number1 - number2)} после {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
                else:
                    true_conditions.append(
                        f"бусина под номером {abs(number1 - number2)} после {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
            else:
                if figures.count(figures[number1 - 1]) > 1:
                    impossible_conditions.append(
                        f"бусина под номером {abs(number1 - number2)} перед {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
                else:
                    true_conditions.append(
                        f"бусина под номером {abs(number1 - number2)} перед {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
        else:
            number1 = randint(1, len(figures))
            number2 = number1
            while number2 == number1:
                number2 = randint(1, len(figures))
            if randint(0, 1) and number1 != len(figures):
                if figures.count(figures[number1 - 1]) > 1:
                    impossible_conditions.append(
                        f"бусина под номером {randint(1, abs(number1 - len(figures)))} после {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
                else:
                    false_conditions.append(
                        f"бусина под номером {randint(1, abs(number1 - len(figures)))} после {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
            elif number1 == 1:
                if figures.count(figures[number1 - 1]) > 1:
                    impossible_conditions.append(
                        f"бусина под номером {randint(1, abs(number1 - len(figures)))} после {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
                else:
                    false_conditions.append(
                        f"бусина под номером {randint(1, abs(number1 - len(figures)))} после {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
            else:
                if figures.count(figures[number1 - 1]) > 1:
                    impossible_conditions.append(
                        f"бусина под номером {randint(1, max(1, number1 - 1))} перед {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")
                else:
                    false_conditions.append(
                        f"бусина под номером {randint(1, max(1, number1 - 1))} перед {colors_third.get(figures[number1 - 1][1])} {types_third.get(figures[number1 - 1][0])} - {colors.get(figures[number2 - 1][1])} {types.get(figures[number2 - 1][0])}")

    for _ in range(content_conditions):
        unique_beads = set(figures)
        not_except_beads = all_beads.difference(unique_beads)
        # current_bead = not_except_beads.pop()
        if randint(0, 1):
            if random.random() <= true_probability or not not_except_beads:
                # bead_type = randint(1, 3)
                # color = (255, 255, 255)
                # while color==(255, 255, 255):
                #     color = (255*randint(0, 1), 255*randint(0, 1), 255*randint(0, 1))
                index = randint(0, len(figures) - 1)
                bead_type = figures[index][0]
                color = figures[index][1]
                # if (bead_type, color) in figures:
                true_conditions.append(f"цепочка содержит {types_second.get(bead_type)} {colors_second.get(color)} бусину")
            else:
                # unique_beads = set(figures)
                # not_except_beads = all_beads.difference(unique_beads)
                current_bead = not_except_beads.pop()
                if not_except_beads:
                    false_conditions.append(
                        f"цепочка содержит {types_second.get(current_bead[0])} {colors_second.get(current_bead[1])} бусину")
                else:
                    index = randint(0, len(figures) - 1)
                    bead_type = figures[index][0]
                    color = figures[index][1]
                    # if (bead_type, color) in figures:
                    true_conditions.append(
                        f"цепочка содержит {types_second.get(bead_type)} {colors_second.get(color)} бусину")
        else:
            if random.random() <= true_probability and not_except_beads:
                # unique_beads = set(figures)
                # not_except_beads = all_beads.difference(unique_beads)
                current_bead = not_except_beads.pop()
                if not_except_beads:
                    true_conditions.append(
                        f"цепочка не содержит {types_second.get(current_bead[0])} {colors_second.get(current_bead[1])} бусину")
                else:
                    index = randint(0, len(figures) - 1)
                    bead_type = figures[index][0]
                    color = figures[index][1]
                    # if (bead_type, color) in figures:
                    false_conditions.append(
                        f"цепочка не содержит {types_second.get(bead_type)} {colors_second.get(color)} бусину")

            else:
                index = randint(0, len(figures) - 1)
                bead_type = figures[index][0]
                color = figures[index][1]
                # if (bead_type, color) in figures:
                false_conditions.append(
                    f"цепочка не содержит {types_second.get(bead_type)} {colors_second.get(color)} бусину")

    for _ in range(equal_conditions):
        if random.random() <= true_probability:
            if randint(0, 1):
                number1 = randint(1, len(figures))
                if len(set(figures)) != len(figures):
                    while figures.count(figures[number1 - 1]) <= 1:
                        number1 = randint(1, len(figures))
                    number2 = randint(1, len(figures))
                    while figures[number2-1] != figures[number1-1]:
                        number2 = randint(1, len(figures))
                #         одинаковые
                    true_conditions.append(f"бусины с номерами {number1} и {number2} одинаковые")
                else:
                    number2 = randint(1, len(figures))
                    true_conditions.append(f"бусины с номерами {number1} и {number2} разные")
            else:
                number1 = randint(1, len(figures))
                number2 = number1
                while number2 == number1:
                    number2 = randint(1, len(figures))
                if figures[number1 - 1] != figures[number2 - 1]:
                    true_conditions.append(f"бусины с номерами {number1} и {number2} разные")
                else:
                    true_conditions.append(f"бусины с номерами {number1} и {number2} одинаковые")
        else:
            number1 = randint(1, len(figures))
            number2 = number1
            while number2 == number1:
                number2 = randint(1, len(figures))
            if figures[number1 - 1] != figures[number2 - 1]:
                false_conditions.append(f"бусины с номерами {number1} и {number2} одинаковые")
            else:
                false_conditions.append(f"бусины с номерами {number1} и {number2} разные")

    print(True, true_conditions)
    print(False, false_conditions)
    print("N", impossible_conditions)

    conditions = true_conditions + false_conditions + impossible_conditions
    shuffle(conditions)
    print(conditions)

    pages = 0
    index = 0
    while index < len(conditions):
        current_y = last_y
        while current_y + 40 < h - end and index < len(conditions):
            vertices = numpy.array([[bordersize, current_y-50], [bordersize + w - 2 * bordersize, current_y-50], [bordersize + w - 2 * bordersize, current_y +40], [bordersize, current_y +40]])
            cv2.polylines(array, [vertices], color=(0, 255, 0), thickness=3, isClosed=1)
            vertices = numpy.array([[bordersize, current_y-50], [bordersize + w - 2 * bordersize-100, current_y-50], [bordersize + w - 2 * bordersize-100, current_y +40], [bordersize, current_y +40]])
            cv2.polylines(array, [vertices], color=(0, 255, 0), thickness=3, isClosed=1)
            cv2.putText(array, conditions[index], (bordersize+20, current_y), font, 1.4 / 2280 * (w - 2 * bordersize), (0, 0, 0), 3)
            index+=1
            current_y+=130
        if index < len(conditions):
            cv2.imwrite("newimage.png", array)
            array = numpy.ones((h, w, 3), dtype=numpy.uint8) * 255
            new_page(pages)
            pages+=1
            last_y = offset


    cv2.imwrite("newimage.png", array)

    new_page(pages)

    answers = []

    for condition in conditions:
        if condition in true_conditions:
            answers.append("И")
        elif condition in false_conditions:
            answers.append("Л")
        else:
            answers.append("Н")

    print(answers)
    return answers

    # image1 = Image.open("newimage.png")
    # im1 = image1.convert('RGB')
    # image1.save("newimage.pdf")
    # image1.addPage("newimage.pdf")


# beads_processing(colornames = 1)
