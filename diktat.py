import cv2
import numpy
import sys


def black_in_range_check(from_x, to_x, from_y, to_y, white_thereshold):
    global cb_img, old_pos
    for y in range(from_y, to_y):
        for x in range(from_x, to_x):
            # print((cb_img[y][x]<=white_thereshold)*"123456789")
            if cb_img[y][x] <= white_thereshold:
                return 0
    return 255


def lines_finding():
    global ceils_data
    lines = []
    for y in range(len(ceils_data)):
        for x in range(len(ceils_data[0])):
            if y+1 < len(ceils_data):
                if ceils_data[y+1][x] != ceils_data[y][x]:
                    lines.append(((x, y), (x, y+1)))
            if x+1 < len(ceils_data[0]):
                if ceils_data[y][x+1] != ceils_data[y][x]:
                    lines.append(((x, y), (x+1, y)))
    return lines

def lines_grouping(lines):
    def find_pos(ceils_data):
        nonlocal lines_temp, old_pos, points, hard_pos
        if len(lines_temp) == 0:
            return (-1, -1)
        current = lines_temp.pop(0)
        x = min(current[0][0], current[1][0])
        y = min(current[0][1], current[1][1])
        if (x, y) in old_pos or (x, y) in hard_pos:
            return find_pos(ceils_data)
        points.append((x, y))
        return (x, y)

    def check_next_by_two_ceils(ceils_data, leftx, lefty, rightx, righty, leftbackx, leftbacky, rightbackx, rightbacky):
        # print(ceils_data[leftx][lefty], ceils_data[rightx][righty])
        # print(leftx, lefty, rightx, righty)
        if ceils_data[lefty][leftx] == ceils_data[rightbacky][rightbackx] == 255 and ceils_data[righty][rightx] == ceils_data[leftbacky][leftbackx] == 0:
            return 3
        if ceils_data[lefty][leftx] == ceils_data[rightbacky][rightbackx] == 0 and ceils_data[righty][rightx] == ceils_data[leftbacky][leftbackx] == 255:
            return 2
        if ceils_data[lefty][leftx]==ceils_data[righty][rightx]==0:
            return 1
        if ceils_data[lefty][leftx]==255 and ceils_data[righty][rightx]==0:
            return 0
        if ceils_data[lefty][leftx]==0 and ceils_data[righty][rightx]==255:
            return 1
        if ceils_data[lefty][leftx]==ceils_data[righty][rightx]==255:
            return 1

    def check_next_by_all_dir(ceils_data, x, y):
        nonlocal dirrection, algorithms, old_pos, hard_pos
        match dirrection:
            case 0:
                res=check_next_by_two_ceils(ceils_data, x-1,y-1,x,y-1, x-1, y, x, y)
            case 1:
                res=check_next_by_two_ceils(ceils_data, x,y-1,x,y, x-1, y-1, x-1, y)
            case 2:
                res=check_next_by_two_ceils(ceils_data, x,y,x-1,y, x, y-1, x-1, y-1)
            case 3:
                res=check_next_by_two_ceils(ceils_data, x-1,y,x-1,y-1, x, y, x, y-1)
        if res in (1, 2):
            # if res == 2:
            #     hard_pos.append((x, y))
            dirrection += 1
            dirrection = dirrection%4
            # print(x, y)
            try:
                x, y = check_next_by_all_dir(ceils_data, x, y)
            except RecursionError:return (None, None)
            return (x, y)
        else:
            match dirrection:
                case 0:
                    y-=1
                    res2=check_next_by_two_ceils(ceils_data, x-1,y-1,x,y-1, x-1, y, x, y)
                    if (x, y) in old_pos and res2 not in (2, 3):
                        return (None, None)
                    old_pos.append((x, y))
                    algorithms[-1].append("↑")
                case 1:
                    x+=1
                    res2=check_next_by_two_ceils(ceils_data, x,y-1,x,y, x-1, y-1, x-1, y)
                    if (x, y) in old_pos and res2 not in (2, 3):
                        return (None, None)
                    old_pos.append((x, y))
                    algorithms[-1].append("→")
                case 2:
                    y+=1
                    res2=check_next_by_two_ceils(ceils_data, x,y,x-1,y, x, y-1, x-1, y-1)
                    if (x, y) in old_pos and res2 not in (2, 3):
                        return (None, None)
                    old_pos.append((x, y))
                    algorithms[-1].append("↓")
                case 3:
                    x-=1
                    res2=check_next_by_two_ceils(ceils_data, x-1,y,x-1,y-1, x, y, x, y-1)
                    if (x, y) in old_pos and res2 not in (2, 3):
                        return (None, None)
                    old_pos.append((x, y))
                    algorithms[-1].append("←")
            # print(*algorithms[0], sep="  ")
            # print(algorithms)
            # print(len(algorithms))
            return (x,y)


    # def get_pos(line):



    #     12
    #     34

    #       0
    #     3   1
    #       2

    global ceils_data
    # actions = {[255, 255, 255, 0]:1,
    #            [255, 255, 0, 255]: 2,
    #            [255, 0, 255, 255]:0,
    #            [0, 255, 255, 255]: 3,
    #            [255, 255, 0, 0]:1,
    #            [0, 0, 255, 255]:3,
    #            [0, 255, 0, 255]:2,
    #            [255, 0, 255, 0]:0,
    #            [0, 0, 0, 255]: 2,
    #            [0, 0, 255, 0]: 3,
    #            [0, 255, 0, 0]: 1,
    #            [255, 0, 0, 0]: 0
    #            }
    # sys.setrecursionlimit(len(lines))
    dirrection = 0
    old_pos = []
    hard_pos = []
    lines_temp = lines.copy()
    points = []
    points_result=[]
    algorithms=[]
    old=()
    while len(lines_temp):
        algorithms.append([])
        x, y = find_pos(ceils_data)
        while x != -1:
            x,y = check_next_by_all_dir(ceils_data, x, y)
            if (x,y) == (None, None):
                x, y = find_pos(ceils_data)
                if algorithms[-1] == []:
                    old=points.pop(-1)
                    algorithms.pop(-1)
                else:
                    # print(old)
                    points_result.append(old)
                algorithms.append([])
            # position = get_pos(groups[-1][-1])
            # if lines_temp - no, to break
    if algorithms[-1] == []:
        algorithms.pop(-1)

    return (algorithms, points_result)

# def pathfinding()

# path = "image-2.png"

# path = "test.png"

# path = "d66e2aec5b534d4ab04c0749a3ab655f.jpg"

# path = "0dd92fff1858cfa5251adc7af48ada22.jpg"

# path = "0dd92fff1858cfa5251adc7af48ada22 (1).jpg"

# path = "64032-dlya-detey-2-3-let-shablony-krupnye-23.jpg"

# path = "image-1.png"

# path = "image.png"

# path = "12345.png"

path = "96653-dlya-detey-2-3-goda-29.jpg"

# path = "5412-coloring-white-mushrooms.png"

# path = "istockphoto-1433038575-612x612.jpg"

# path = "pi.png"

# path = "images.png"

# path = "img-DKBCw0.png"

# path = "squares.png"

# path = "3630.jpg"

# path = "tower.png"

white_thereshold_relative = 0.7
# white_thereshold_relative = 0.65



white_thereshold = 255*white_thereshold_relative



# image_size_horisontal = 54
# image_size_horisontal = 54
image_size_horisontal = 54




ceil_border_size_relative = 1
ceil_border_color = 200
text_color = 200


cycles = 1


ceil_border_size = int(10//ceil_border_size_relative)



cb_img = cv2.imread(path,0)



image_size_vertical = image_size_horisontal*len(cb_img)//len(cb_img[0])

print(image_size_horisontal, image_size_vertical)

print(f"horisontal: {len(cb_img[0])}, vertical: {len(cb_img)}")

# resize_k = image_size_horisontal/len(cb_img[0])
# print(resize_k)

ceil_size = len(cb_img[0])/image_size_horisontal
print(ceil_size)

rounded_ceil_size = int(ceil_size)
print(rounded_ceil_size)


# ceils_data = [[0]*image_size_horisontal]*image_size_vertical
ceils_data = [[255 for _ in range(image_size_horisontal)] for _ in range(image_size_vertical)]


ceils_field = [[255-(255-ceil_border_color)*(i%ceil_border_size==0 or i2%ceil_border_size==0) for i in range((image_size_horisontal+1)*ceil_border_size)] for i2 in range((image_size_vertical+1)*ceil_border_size)]


print(ceils_data)


# theresholding
# for i in range(len(cb_img)):
#     for i2 in range(len(cb_img[0])):
#         if cb_img[i][i2] >= white_thereshold:
#             cb_img[i][i2] = 255
#         else:
#             cb_img[i][i2] = 0




for y in range(1, image_size_vertical-1):
    for x in range(1, image_size_horisontal-1):
        # print(int(x*ceil_size), int((x+1)*ceil_size), int(y*ceil_size), int((y+1)*ceil_size))
        ceils_data[y][x]=black_in_range_check(int(x*ceil_size), int((x+1)*ceil_size), int(y*ceil_size), int((y+1)*ceil_size), white_thereshold)



for i in ceils_data:
    print(i)

# print(str(cb_img[24]))

print(ceils_data)

cv2.imwrite("newimage.png", numpy.array(ceils_data))


lines = lines_finding()
print(lines)
result, points=lines_grouping(lines)
print(points)
print(result)
max_len = 0
new_result = []
for i in range(len(result)):
    if len(result[i]) > max_len:max_len=len(result[i])
    string = str(result[i]).replace("\'", "").replace("[", "").replace("]", "").replace(",", "")
    for i2 in range(len(result[i])-1, 1, -1):
        string=string.replace(("↑ "*i2)[:-1], f"↑x{i2}")
        string=string.replace(("→ "*i2)[:-1], f"→x{i2}")
        string=string.replace(("↓ "*i2)[:-1], f"↓x{i2}")
        string=string.replace(("← "*i2)[:-1], f"←x{i2}")
    new_result.append(string)
    print(str(i+1)+".", string)


for i in range(len(points)):
    for y in range(ceil_border_size*points[i][1]-1, ceil_border_size*points[i][1]+2):
        for x in range(ceil_border_size*points[i][0]-1, ceil_border_size*points[i][0]+2):
            ceils_field[y][x]=text_color
    # ceils_field[ceil_border_size*i[1]][ceil_border_size*i[0]]=0

ceils_field=numpy.array(ceils_field)

# font = cv2.FONT_HERSHEY_SIMPLEX
# scale = 0.3


font = 5
scale = 0.6

cv2.imwrite("ceils_field.png", numpy.array(ceils_field))

img = cv2.imread("ceils_field.png")


for i in range(len(points)):
    cv2.putText(img, str(i+1), (ceil_border_size*points[i][0]+3, ceil_border_size*points[i][1]), font, scale, (text_color,text_color,text_color), 1)

max_len=10
if cycles:
    to_replace = []

    for x in range(-1*max_len, max_len+1):
        if x:
            for y in range(-1*max_len, max_len+1):
                if y:
                    arrows = ["↑", "→"]
                    if x<0:
                        arrows[1] = "←"
                    if y<0:
                        arrows[0] = "↓"
                    to_replace.append(f"{arrows[1]}{("x"+str(abs(x)))*(abs(x)!=1)} {arrows[0]}{("x"+str(abs(y)))*(abs(y)!=1)}")

    # print(to_replace)
    for i in range(len(new_result)):
        for replaceble in to_replace:
            for i2 in range(len(new_result[i])-1, 1, -1):
                # print((i2-1)*(replaceble+" ")+replaceble, f"({replaceble})x{i2}")
                new_result[i] = new_result[i].replace((i2-1)*(replaceble+" ")+replaceble+" ", f"({replaceble})x{i2} ")
print(to_replace)
print()
for i in range(len(new_result)):
    print(str(i+1)+".", new_result[i])

cv2.imwrite("ceils_field.png", img)