# import cv2
# import numpy
from PIL import Image, ImageDraw, ImageFont
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters
import datetime
from beads import beads_processing
from processing import processing
from disk import disk
import json
import asyncio
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

max_size = 100
max_length = 1000

app = Flask(__name__)

# # Токен бота
# with open('config.json') as f:
#     config = json.load(f)
# TOKEN = config['telegram_bot_token']

TOKEN = os.getenv("TOKEN")
ADMINS = os.getenv('ADMINS')

disk.download("/log.txt", "log.txt", "log.txt")


# Текст помощи
help_text = """
Этот бот принимает изображение (предпочтительно в формате раскраски) и преобразует его в стрелочный диктант.

Доступные команды:
/size <значение> - установить размер итогового рисунка (по умолчанию 54)
/threshold <значение> - установить порог определения цвета (0-1, по умолчанию 0.65)
/ceilsize <значение> - установить размер клетки (по умолчанию 10)
/ceilcolor <цвет> - установить цвет границ клеток (0-255, по умолчанию 200)
/textcolor <цвет> - установить цвет текста (0-255, по умолчанию 200, при больших размерах рекомендуется 100 для читаемости)
/cycles <значение> - установить наличие циклов (0/1 (есть или нет) по умолчанию 1)
/help - показать это сообщение
/reset - сбросить параметры к значениям по умолчанию

Просто отправьте боту изображение для обработки стрелочного диктанта.

Чтобы сгенерировать задание с цепочками, можно написать /beads

/length <значение> - длина цепочки (по умолчанию 10)
/order <значение> - количество условий на порядок (0-100, по умолчанию 5)
/relative <значение> - количество условий на относительный порядок (0-100, по умолчанию 5)
/content <значение> - количество условий на содержание (0-100, по умолчанию 5)
/equal <значение> - количество условий на равенство (0-100, по умолчанию 5)
/true <значение> - доля истинных утверждений (0-1, по умолчанию 0.5)
/colornames <значение> - написание названий цветов ("режим дальтоника") (0/1 (есть или нет) по умолчанию 0)
/bordersize <значение> - размер границ (полей) (0-400, по умолчанию 100)
/offset <значение> - отступ сверху (0-1000, по умолчанию 200)
/end <значение> - отступ снизу (0-1000, по умолчанию 100)
/beadsize <значение> - размер бусины (0-500, по умолчанию 100)
/levelsize <значение> - размер уровня бусин (0-1000, по умолчанию 300)
/beads - генерация цепочки
"""

# Параметры по умолчанию
DEFAULT_PARAMS = {
    'size': 54,
    'threshold': 0.65,
    'ceilsize': 1,
    'ceilcolor': 200,
    'textcolor': 200,
    'cycles': 1,

    'length': 10,
    'order': 5,
    'relative': 5,
    'content': 5,
    'equal': 5,
    'true': 0.5,
    'colornames': 0,
    'bordersize': 100,
    'offset': 200,
    'end': 100,
    'beadsize': 100,
    'distance': 1,
    'levelsize': 300
}

# Глобальные параметры (будут изменяться командами)
# params = DEFAULT_PARAMS.copy()
params = {}


def set_self_params(user_id):
    global params, DEFAULT_PARAMS
    if user_id not in params.keys():
        params.update({user_id: DEFAULT_PARAMS.copy()})


async def new_params_send(context: ContextTypes.DEFAULT_TYPE, user_id, username=None):
    with open("log.txt", "a") as file:
        if username:
            file.write(f"{datetime.datetime.now()} id:{user_id}, username:@{username}, params update: {str(params)}\n")
            disk.upload("/log.txt", "log.txt", "log.txt")
            await log_send_to_admin(context,
                                    f"{datetime.datetime.now()} id:{user_id}, username:@{username}, params update: {str(params)}\n")
        else:
            file.write(f"{datetime.datetime.now()} id:{user_id}, params update: {str(params)}\n")
            disk.upload("/log.txt", "log.txt", "log.txt")
            await log_send_to_admin(context, f"{datetime.datetime.now()} id:{user_id}, params update: {str(params)}\n")


# async def apply_operations(image, current_params):
# """Применяет операции к изображению и возвращает 2 изображения и текст"""
# # Конвертируем в numpy array
# img_array = numpy.array(image)
#
# # Преобразуем в чёрно-белый
# gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
#
# # Применяем порог бинаризации
# _, binary = cv2.threshold(gray, current_params['threshold'], 255, cv2.THRESH_BINARY)
#
# # Изменяем размер
# resized = cv2.resize(binary, (current_params['size'], current_params['size']), interpolation=cv2.INTER_AREA)
#
# # Первое изображение - просто чёрно-белое
# image1 = Image.fromarray(resized)
#
# # Второе изображение - с сеткой
# image2 = image1.copy()
# draw = ImageDraw.Draw(image2)
#
# # Рисуем сетку
# ceil_size = current_params['ceilsize']
# width, height = image2.size
#
# # Цвет сетки
# grid_color = 0 if current_params['ceilcolor'] == 'black' else 255
#
# for x in range(0, width, ceil_size):
#     draw.line([(x, 0), (x, height)], fill=grid_color)
# for y in range(0, height, ceil_size):
#     draw.line([(0, y), (width, y)], fill=grid_color)
#
# # Генерируем текст с параметрами
# text = f"Параметры:\nРазмер: {current_params['size']}\nПорог: {current_params['threshold']}\n"
# text += f"Размер ячейки: {current_params['ceilsize']}\nЦвет ячейки: {current_params['ceilcolor']}\n"
# text += f"Цвет текста: {current_params['textcolor']}\nЦиклы: {current_params['cycles']}"

# return image1, image2, text


# async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    global params
    """Обрабатывает полученное изображение"""
    try:
        # Получаем изображение
        photo_file = await update.message.photo[-1].get_file()
        image_stream = io.BytesIO()
        await photo_file.download_to_memory(out=image_stream)
        image_stream.seek(0)
        image = Image.open(image_stream)

        # photo_file.file_path
        # image1, image2, text = processing(image, params['cycles'])
        image1, image2, text = processing(
            image,
            params[user_id]['size'],
            params[user_id]['threshold'],
            params[user_id]['ceilsize'],
            params[user_id]['ceilcolor'],
            params[user_id]['textcolor'],
            bool(params[user_id]['cycles'])
        )

        # image1, image2, text = processing(image, params['size'], params['thereshold'], params['ceilsize'], params['ceilcolor'], params['textcolor'], params['cycles'])

        # # Применяем операции несколько раз (по количеству cycles)
        # for _ in range(params['cycles']):
        #     image1, image2, text = await apply_operations(image, params)

        # Сохраняем изображения в буфер

        img1_bytes = io.BytesIO()
        image1.save(img1_bytes, format='PNG')
        img1_bytes.seek(0)

        img2_bytes = io.BytesIO()
        image2.save(img2_bytes, format='PNG')
        img2_bytes.seek(0)

        with open("log.txt", "a") as file:
            if update.message.from_user.username:
                file.write(
                    f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)}, photo path: {photo_file.file_path}\n")
                disk.upload("/log.txt", "log.txt", "log.txt")
                await log_send_to_admin(context,
                                        f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)}, photo path: {photo_file.file_path}\n")
            else:
                file.write(
                    f"{datetime.datetime.now()} id:{user_id}, params: {str(params)}, photo path: {photo_file.file_path}\n")
                disk.upload("/log.txt", "log.txt", "log.txt")
                await log_send_to_admin(context,
                                        f"{datetime.datetime.now()} id:{user_id}, params: {str(params)}, photo path: {photo_file.file_path}\n")

        # Отправляем результаты
        await update.message.reply_photo(photo=img1_bytes, caption="Шаблон")
        await update.message.reply_photo(photo=img2_bytes, caption="Предпросмотр")
        await update.message.reply_text(text)

        # Обновляем stream для следующей итерации
        image_stream = io.BytesIO()
        image2.save(image_stream, format='PNG')
        image_stream.seek(0)

    except Exception as e:
        with open("log.txt", "a") as file:
            if update.message.from_user.username:
                file.write(
                    f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)}, exeption: {str(e)}\n")
                disk.upload("/log.txt", "log.txt", "log.txt")
                await log_send_to_admin(context,
                                        f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)}, exeption: {str(e)}\n")
            else:
                file.write(f"{datetime.datetime.now()} id:{user_id}, params: {str(params)}, exeption: {str(e)}\n")
                disk.upload("/log.txt", "log.txt", "log.txt")
                await log_send_to_admin(context,
                                        f"{datetime.datetime.now()} id:{user_id}, params: {str(params)}, exeption: {str(e)}\n")

        await update.message.reply_text(f"Произошла ошибка: {str(e)}")


async def beads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)

    answers = str(beads_processing(
        params[user_id]['length'],
        params[user_id]['order'],
        params[user_id]['relative'],
        params[user_id]['content'],
        params[user_id]['equal'],
        params[user_id]['true'],
        params[user_id]['colornames'],
        params[user_id]['bordersize'],
        params[user_id]['offset'],
        params[user_id]['end'],
        params[user_id]['beadsize'],
        params[user_id]['distance'],
        params[user_id]['levelsize']
    )).replace("[", "").replace("]", "").replace(",", "").replace("\'", "")

    with open("log.txt", "a") as file:
        if update.message.from_user.username:
            file.write(f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)} beads\n")
            disk.upload("/log.txt", "log.txt", "log.txt")
            await log_send_to_admin(context,f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)} beads\n")
        else:
            file.write(f"{datetime.datetime.now()} id:{user_id}, params: {str(params)} beads\n")
            disk.upload("/log.txt", "log.txt", "log.txt")
            await log_send_to_admin(context,f"{datetime.datetime.now()} id:{user_id}, params: {str(params)} beads\n")


    with open("newimage.pdf", "rb") as file:
        await update.message.reply_document(
            document=file,
            filename="result.pdf",
            caption=f"Ответы: {answers}"
            # parse_mode='HTML'
        )

    # except Exception as e:
    #     with open("log.txt", "a") as file:
    #         if update.message.from_user.username:
    #             file.write(f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)}, exeption: {str(e)}\n")
    #             disk.upload("/log.txt", "log.txt", "log.txt")
    #             await log_send_to_admin(context,f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)}, exeption: {str(e)}\n")
    #         else:
    #             file.write(f"{datetime.datetime.now()} id:{user_id}, params: {str(params)}, exeption: {str(e)}\n")
    #             disk.upload("/log.txt", "log.txt", "log.txt")
    #             await log_send_to_admin(context,f"{datetime.datetime.now()} id:{user_id}, params: {str(params)}, exeption: {str(e)}\n")


# async def keep_alive():
#     while True:
#         try:
#             async with aiohttp.ClientSession() as session:
#                 # async with session.get('https://api.telegram.org/botYOUR_TOKEN/getMe') as resp:
#                 #     with open("log.txt", "rb") as file:
#                 #         await context.bot.send_document(
#                 #             chat_id=ADMINS[0],
#                 #             document=file,
#                 #             filename="log.txt"
#                 #             # parse_mode='HTML'
#                 #         )
#                     await asyncio.sleep(300)  # Каждые 5 минут
#         except:
#             await asyncio.sleep(60)

@app.route('/')
def health_check():
    return "Bot is alive", 200


def run_flask():
    app.run(host='0.0.0.0', port=5000)


async def set_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global max_size
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        size = int(context.args[0])
        if size < 5 or size > max_size:
            await update.message.reply_text(f"Размер должен быть между 5 и {max_size}")
            return
        params[user_id]['size'] = size
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Размер установлен: {size}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /size <число>")


async def set_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает порог"""
    try:
        threshold = float(context.args[0])
        if threshold < 0 or threshold > 1:
            await update.message.reply_text("Порог должен быть между 0 и 1")
            return
        params[user_id]['threshold'] = threshold
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Порог установлен: {threshold}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /threshold <дробное число от 0 до 1>")


async def set_ceilsize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер ячейки"""
    try:
        ceilsize = float(context.args[0])
        if ceilsize < 0.1 or ceilsize > 2:
            await update.message.reply_text("Размер ячейки должен быть между 0.1 и 2")
            return
        params[user_id]['ceilsize'] = ceilsize
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Размер ячейки установлен: {ceilsize}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /ceilsize <число>")


async def set_ceilcolor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает цвет ячеек"""
    try:
        color = int(context.args[0])
        if color < 0 or color > 255:
            await update.message.reply_text("Цвет должен быть между 0 и 255")
            return
        params[user_id]['ceilcolor'] = color
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Цвет ячеек установлен: {color}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /ceilcolor <число>")


async def set_textcolor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает цвет текста"""
    try:
        color = int(context.args[0])
        if color < 0 or color > 255:
            await update.message.reply_text("Цвет должен быть между 0 и 255")
            return
        params[user_id]['textcolor'] = color
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Цвет текста установлен: {color}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /textcolor <число>")


async def set_cycles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает количество циклов обработки"""
    try:
        cycles = int(context.args[0])
        if cycles not in (1, 0):
            await update.message.reply_text("Количество циклов должно быть 1 или 0")
            return
        params[user_id]['cycles'] = cycles
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Количество циклов установлено: {cycles}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /cycles <1|0>")


async def set_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global max_length
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        length = int(context.args[0])
        if length < 2 or length > max_length:
            await update.message.reply_text(f"Длина цепочки должна быть между 2 и {max_length}")
            return
        params[user_id]['length'] = length
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Длина цепочки установлена: {length}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /length <число>")


async def set_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        order = int(context.args[0])
        if order < 0 or order > 100:
            await update.message.reply_text(f"Количество условий на порядок должно быть между 0 и {100}")
            return
        params[user_id]['order'] = order
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Количество условий на порядок установлено: {order}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /order <число>")


async def set_relative(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        relative = int(context.args[0])
        if relative < 0 or relative > 100:
            await update.message.reply_text(f"Количество условий на относительный порядок должно быть между 0 и {100}")
            return
        params[user_id]['relative'] = relative
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Количество условий на относительный порядок установлено: {relative}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /relative <число>")


async def set_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        content = int(context.args[0])
        if content < 0 or content > 100:
            await update.message.reply_text(f"Количество условий на содержание должно быть между 0 и {100}")
            return
        params[user_id]['content'] = content
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Количество условий на содержание установлено: {content}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /content <число>")


async def set_equal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        equal = int(context.args[0])
        if equal < 0 or equal > 100:
            await update.message.reply_text(f"Количество условий на равенство должно быть между 0 и {100}")
            return
        params[user_id]['equal'] = equal
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Количество условий на равенство установлено: {equal}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /equal <число>")


async def set_true(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает порог истинности"""
    try:
        true = float(context.args[0])
        if true < 0 or true > 1:
            await update.message.reply_text("Доля истинности должна быть между 0 и 1")
            return
        params[user_id]['true'] = true
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Доля истинности установлена: {true}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /true <дробное число от 0 до 1>")


async def set_colornames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает количество циклов обработки"""
    try:
        colornames = int(context.args[0])
        if colornames not in (1, 0):
            await update.message.reply_text("Использование названий цветов должно быть 1 или 0")
            return
        params[user_id]['colornames'] = colornames
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Использование названий цветов установлено: {colornames}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /colornames <1|0>")


async def set_bordersize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        bordersize = int(context.args[0])
        if bordersize < 0 or bordersize > 400:
            await update.message.reply_text(f"Размер полей должен быть между 0 и {400}")
            return
        params[user_id]['bordersize'] = bordersize
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Размер полей установлен: {bordersize}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /bordersize <число>")


async def set_offset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        offset = int(context.args[0])
        if offset < 0 or offset > 1000:
            await update.message.reply_text(f"Отступ должен быть между 0 и {1000}")
            return
        params[user_id]['offset'] = offset
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Отступ установленен: {offset}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /offset  <число>")


async def set_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        end = int(context.args[0])
        if end < 0 or end > 1000:
            await update.message.reply_text(f"Отступ с конца должен быть между 0 и {1000}")
            return
        params[user_id]['end'] = end
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Отступ с конца установленен: {end}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /end <число>")


async def set_beadsize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        beadsize = int(context.args[0])
        if beadsize < 0 or beadsize > 500:
            await update.message.reply_text(f"Размер бусины должен быть между 0 и {500}")
            return
        params[user_id]['beadsize'] = beadsize
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Размер бусины установленен: {beadsize}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /beadsize <число>")


async def set_levelsize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Устанавливает размер изображения"""
    try:
        levelsize = int(context.args[0])
        if levelsize < 0 or levelsize > 1000:
            await update.message.reply_text(f"Размер уровня бусин должен быть между 0 и {1000}")
            return
        params[user_id]['levelsize'] = levelsize
        await new_params_send(context, user_id, update.message.from_user.username)
        await update.message.reply_text(f"Размер уровня бусин установленен: {levelsize}")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /levelsize <число>")


async def reset_params(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    """Сбрасывает параметры к значениям по умолчанию"""
    global params
    params[user_id] = DEFAULT_PARAMS.copy()
    await new_params_send(context, user_id, update.message.from_user.username)
    await update.message.reply_text("Параметры сброшены к значениям по умолчанию")


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_self_params(user_id)
    with open("log.txt", "a") as file:
        if update.message.from_user.username:
            file.write(
                f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)}, start\n")
            disk.upload("/log.txt", "log.txt", "log.txt")
            await log_send_to_admin(context,
                                    f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username}, params: {str(params)}, start\n")
        else:
            file.write(f"{datetime.datetime.now()} id:{user_id}, params: {str(params)}, start\n")
            disk.upload("/log.txt", "log.txt", "log.txt")
            await log_send_to_admin(context, f"{datetime.datetime.now()} id:{user_id}, params: {str(params)}, start\n")
    """Показывает справку"""
    await update.message.reply_text(help_text)


async def show_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMINS
    user_id = update.message.from_user.id
    # with open('config.json') as f:
    #     config = json.load(f)

    with open("log.txt", "a") as file:
        if update.message.from_user.username:
            file.write(
                f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username} admin log\n")
            disk.upload("/log.txt", "log.txt", "log.txt")
            await log_send_to_admin(context,
                                    f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username} admin log\n")
        else:
            file.write(f"{datetime.datetime.now()} id:{user_id} admin log\n")
            disk.upload("/log.txt", "log.txt", "log.txt")
            await log_send_to_admin(context, f"{datetime.datetime.now()} id:{user_id} admin log\n")
            # if user_id in config['admins']:

    if str(user_id) in ADMINS.split():
        with open("log.txt", "a") as file:
            if update.message.from_user.username:
                file.write(
                    f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username} admin success\n")
                disk.upload("/log.txt", "log.txt", "log.txt")
                await log_send_to_admin(context,
                                        f"{datetime.datetime.now()} id:{user_id}, username:@{update.message.from_user.username} admin success\n")
            else:
                file.write(f"{datetime.datetime.now()} id:{user_id} admin success\n")
                disk.upload("/log.txt", "log.txt", "log.txt")
                await log_send_to_admin(context, f"{datetime.datetime.now()} id:{user_id} admin success\n")

        with open("log.txt", "rb") as file:
            await update.message.reply_document(
                document=file,
                filename="log.txt",
                caption="log"
            )


async def log_send_to_admin(context: ContextTypes.DEFAULT_TYPE, message: str):
    try:
        # print(int(ADMINS.split()[0]))
        # await context.bot.send_message(
        #     chat_id=int(ADMINS.split()[0]),
        #     text=message,
        #     parse_mode='HTML'
        # )
        with open("log.txt", "rb") as file:
            await context.bot.send_document(
                chat_id=int(ADMINS.split()[0]),
                document=file,
                filename="log.txt",
                caption=message
                # parse_mode='HTML'
            )

        # await context.bot.send_message(
        #     chat_id=ADMINS[0],
        #     text=message,
        #     parse_mode='HTML'
        # )
    except Exception as e:
        print(e)


async def main():
    global TOKEN
    """Запускает бота"""
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("size", set_size))
    application.add_handler(CommandHandler("threshold", set_threshold))
    application.add_handler(CommandHandler("ceilsize", set_ceilsize))
    application.add_handler(CommandHandler("ceilcolor", set_ceilcolor))
    application.add_handler(CommandHandler("textcolor", set_textcolor))
    application.add_handler(CommandHandler("cycles", set_cycles))
    application.add_handler(CommandHandler("reset", reset_params))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CommandHandler("start", show_help))
    application.add_handler(CommandHandler("log", show_log))

    application.add_handler(CommandHandler("length", set_length))
    application.add_handler(CommandHandler("order", set_order))
    application.add_handler(CommandHandler("relative", set_relative))
    application.add_handler(CommandHandler("content", set_content))
    application.add_handler(CommandHandler("equal", set_equal))
    application.add_handler(CommandHandler("true", set_true))
    application.add_handler(CommandHandler("colornames", set_colornames))
    application.add_handler(CommandHandler("bordersize", set_bordersize))
    application.add_handler(CommandHandler("offset", set_offset))
    application.add_handler(CommandHandler("end", set_end))
    application.add_handler(CommandHandler("beadsize", set_beadsize))
    # application.add_handler(CommandHandler("distance", set_distance))
    application.add_handler(CommandHandler("levelsize", set_levelsize))
    application.add_handler(CommandHandler("beads", beads))

    # Обработчик изображений
    application.add_handler(MessageHandler(filters.PHOTO, process_image))

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # asyncio.create_task(keep_alive())

    # Запуск бота
    # application.run_polling()

    # Запуск бота
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # Для версий PTB 20.x+

    # Бесконечное ожидание
    await asyncio.Event().wait()

    # Остановка (этот код фактически никогда не выполнится)
    await application.updater.stop()
    await application.stop()


if __name__ == '__main__':
    asyncio.run(main())

