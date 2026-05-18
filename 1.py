from PIL import (
    Image, ImageDraw, ImageEnhance, ImageFont, ImageOps, ImageStat,
    UnidentifiedImageError,
)


def get_filename():
    while True:
        filename = input("Введите путь к изображению: ")
        try:
            with Image.open(filename) as im:
                im.verify()
            return filename
        except FileNotFoundError:
            print("Файл не найден")
        except (UnidentifiedImageError, OSError):
            print("Это не изображение или файл повреждён")


def ask_number(prompt, cast=float, predicate=None, predicate_msg=""):
    type_msg = "целое число" if cast is int else "число"
    while True:
        try:
            value = cast(input(prompt))
        except ValueError:
            print(f"Ожидалось {type_msg}")
            continue
        if predicate is None or predicate(value):
            return value
        print(predicate_msg or "Недопустимое значение")


def ask_choice(prompt, options):
    options_lower = {o.lower(): o for o in options}
    while True:
        raw = input(prompt).strip().lower()
        if raw in options_lower:
            return options_lower[raw]
        print(f"Доступно: {', '.join(options)}")


def ask_coords(prompt, expected_count):
    while True:
        raw = input(prompt).strip().replace(",", " ")
        try:
            values = [int(v) for v in raw.split()]
        except ValueError:
            print("Координаты должны быть целыми числами")
            continue
        if len(values) != expected_count:
            print(f"Нужно {expected_count} чисел, введено {len(values)}")
            continue
        return values


FLIPS = {
    "a": ("Отразить по вертикали",          Image.Transpose.FLIP_TOP_BOTTOM),
    "b": ("Отразить по горизонтали",        Image.Transpose.FLIP_LEFT_RIGHT),
    "c": ("Отразить по главной диагонали",  Image.Transpose.TRANSPOSE),
    "d": ("Отразить по побочной диагонали", Image.Transpose.TRANSVERSE),
}

PRIMITIVES = {
    "1": ("прямоугольник", "rectangle"),
    "2": ("эллипс",        "ellipse"),
    "3": ("линия",         "line"),
}


def flip(img, key):
    return img.transpose(FLIPS[key][1])


def sepia(img, intensity=0.8):
    gray = ImageOps.grayscale(img)
    tone = ImageOps.colorize(gray, black="#1b0d00", white="#ffe1b3")
    return Image.blend(img, tone, intensity)


def change_brightness(img, k):
    return ImageEnhance.Brightness(img).enhance(k)


def average_color(img):
    mean = ImageStat.Stat(img.convert("RGB")).mean
    return tuple(int(c) for c in mean)


def average_color_picture(img, size=(300, 300)):
    color = average_color(img)
    return Image.new("RGB", size, color), color


def add_text(img, x, y, text, size=48, fill="white"):
    out = img.copy()
    draw = ImageDraw.Draw(out)
    draw.text((x, y), text, fill=fill, font=ImageFont.load_default(size))
    return out


def add_primitive(img, kind, coords, outline="red", width=6):
    out = img.copy()
    draw = ImageDraw.Draw(out)
    if kind == "rectangle":
        draw.rectangle(coords, outline=outline, width=width)
    elif kind == "ellipse":
        draw.ellipse(coords, outline=outline, width=width)
    elif kind == "line":
        draw.line(coords, fill=outline, width=width)
    return out


def menu():
    print("\nМеню:")
    for key, (label, _) in FLIPS.items():
        print(f"  {key}) {label}")
    print("  e) Применить сепию")
    print("  f) Увеличить яркость")
    print("  g) Уменьшить яркость")
    print("  h) Расчитать и продемонстрировать средний цвет изображения")
    print("  i) Добавить текст изображения по координатам")
    print("  j) Добавить на изображение графический элемент (круг, квадрат, линия) по координатам")
    print("  q) Выйти")


def main():
    path = get_filename()
    img = Image.open(path).convert("RGB")
    w, h = img.size

    while True:
        menu()
        choice = input("> ").strip().lower()

        if choice == "q":
            break
        elif choice in FLIPS:
            result, label = flip(img, choice), FLIPS[choice][0]
        elif choice == "e":
            result, label = sepia(img), "Сепия"
        elif choice == "f":
            k = ask_number(
                "Введите коэффициент яркости (>1 для увеличения): ",
                predicate=lambda v: v > 1,
                predicate_msg="Коэффициент должен быть больше 1",
            )
            result, label = change_brightness(img, k), f"Яркость: {k}"
        elif choice == "g":
            k = ask_number(
                "Введите коэффициент яркости (0-1 для уменьшения): ",
                predicate=lambda v: 0 < v < 1,
                predicate_msg="Коэффициент должен быть между 0 и 1",
            )
            result, label = change_brightness(img, k), f"Яркость: {k}"
        elif choice == "h":
            result, color = average_color_picture(img)
            label = f"Средний цвет RGB{color}"
        elif choice == "i":
            print(f"Размер изображения: {w}×{h}")
            x = ask_number("x: ", cast=int,
                           predicate=lambda v: 0 <= v < w,
                           predicate_msg=f"x должен быть в диапазоне 0..{w-1}")
            y = ask_number("y: ", cast=int,
                           predicate=lambda v: 0 <= v < h,
                           predicate_msg=f"y должен быть в диапазоне 0..{h-1}")
            text = input("Текст: ")
            result, label = add_text(img, x, y, text), "Текст"
        elif choice == "j":
            print("Выберите примитив:")
            for num, (name, _) in PRIMITIVES.items():
                print(f"  {num}) {name}")
            key = ask_choice("> ", list(PRIMITIVES))
            name, kind = PRIMITIVES[key]
            print(f"Размер изображения: {w}×{h}")
            if kind == "line":
                p1 = ask_coords("Начальная точка (x y): ", 2)
                p2 = ask_coords("Конечная точка (x y): ", 2)
            else:
                p1 = ask_coords("Левый верхний угол (x y): ", 2)
                while True:
                    p2 = ask_coords("Правый нижний угол (x y): ", 2)
                    if p2[0] > p1[0] and p2[1] > p1[1]:
                        break
                    print(f"Правый нижний должен быть правее и ниже ({p1[0]}, {p1[1]})")
            result, label = add_primitive(img, kind, p1 + p2), f"Примитив: {name}"
        else:
            print("Неверный выбор")
            continue

        print(label)
        result.show()



main()
