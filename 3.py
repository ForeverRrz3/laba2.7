import os
from PIL import Image, ImageStat


def get_dir():
    while True:
        path = input("Путь до папки с изображениями бренда: ")
        if os.path.isdir(path):
            return path
        print("Папка не найдена")


def count_colors(img):
    counts = {}
    for pixel in img.convert("RGB").getdata():
        key = tuple(c // 32 * 32 for c in pixel)
        counts[key] = counts.get(key, 0) + 1
    return counts


def contrast(img):
    return ImageStat.Stat(img.convert("L")).stddev[0]


def label(value):
    if value < 30:
        return "низкий"
    if value < 60:
        return "средний"
    return "высокий"


def temperature(img):
    r, g, b = ImageStat.Stat(img.convert("RGB")).mean
    if r >= g and r >= b:
        return "тёплый"
    if b >= r and b >= g:
        return "холодный"
    return "нейтральный"


def solid(color):
    return Image.new("RGB", (500, 200), color)


def palette(colors):
    band, h = 100, 200
    canvas = Image.new("RGB", (band * len(colors), h))
    for i, color in enumerate(colors):
        canvas.paste(Image.new("RGB", (band, h), color), (i * band, 0))
    return canvas


def main():
    directory = get_dir()
    paths = sorted(os.path.join(directory, n) for n in os.listdir(directory))
    images = [Image.open(p) for p in paths]

    total = {}
    for img in images:
        for color, count in count_colors(img).items():
            total[color] = total.get(color, 0) + count
    top = [c for c, _ in sorted(total.items(), key=lambda x: -x[1])[:5]]

    solid(top[0]).show()

    avg = sum(contrast(img) for img in images) / len(images)
    print(f"Контрастность: {label(avg)}")

    groups = {"тёплый": [], "нейтральный": [], "холодный": []}
    for path, img in zip(paths, images):
        groups[temperature(img)].append(os.path.basename(path))
    print("Группы по температуре:")
    for name, names in groups.items():
        print(f"  {name}: {', '.join(names) if names else '—'}")

    palette(top).show()


main()
