import os
from PIL import Image, ImageStat, UnidentifiedImageError


BORDER = 10


def get_n(max_n):
    while True:
        try:
            n = int(input(f"Сколько изображений в коллаже (1 - {max_n}): "))
        except ValueError:
            print("Ожидалось целое число")
            continue
        if 1 <= n <= max_n:
            return n
        print(f"Введите число от 1 до {max_n}")


def get_directory(prompt):
    while True:
        path = input(prompt)
        if os.path.isdir(path):
            return path
        print("Папка не найдена")


def get_image(prompt):
    while True:
        path = input(prompt)
        try:
            with Image.open(path) as im:
                im.verify()
            return path
        except FileNotFoundError:
            print("Файл не найден")
        except (UnidentifiedImageError, OSError):
            print("Это не изображение или повреждённый файл")

def list_images(directory):
    paths = []
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if not os.path.isfile(path):
            continue
        try:
            with Image.open(path) as im:
                im.verify()
            paths.append(path)
        except (UnidentifiedImageError, OSError):
            continue
    return paths

def average_color(img):
    mean = ImageStat.Stat(img.convert("RGB")).mean
    return tuple(int(c) for c in mean)


def color_distance(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def grid_shape(n):
    rows = int(n ** 0.5)
    while n % rows != 0:
        rows -= 1
    return rows, n // rows


def mix(colors):
    return tuple(int(sum(c[i] for c in colors) / len(colors)) for i in range(3))


def build_collage(paths, canvas_size, border_color):
    rows, cols = grid_shape(len(paths))
    w, h = canvas_size
    tile_w = (w - 2 * BORDER) // cols
    tile_h = (h - 2 * BORDER) // rows

    canvas = Image.new("RGB", (w, h), border_color)
    i = 0
    for r in range(rows):
        for c in range(cols):
            tile = Image.open(paths[i]).convert("RGB").resize((tile_w, tile_h))
            canvas.paste(tile, (BORDER + c * tile_w, BORDER + r * tile_h))
            i += 1
    return canvas


def main():
    directory = get_directory("Путь до папки с изображениями: ")
    target_path = get_image("Путь до целевого изображения: ")

    paths = list_images(directory)
    if not paths:
        print("В папке нет изображений")
        return

    n = get_n(len(paths))

    catalog = [(p, average_color(Image.open(p))) for p in paths]
    target_color = average_color(Image.open(target_path))

    catalog.sort(key=lambda item: color_distance(item[1], target_color))
    chosen = catalog[:n]
    chosen_paths = [p for p, _ in chosen]
    chosen_colors = [c for _, c in chosen]

    border_color = mix(chosen_colors)

    with Image.open(target_path) as target:
        canvas_size = target.size

    collage = build_collage(chosen_paths, canvas_size, border_color)
    collage.save("collage.png")
    collage.show()


main()
