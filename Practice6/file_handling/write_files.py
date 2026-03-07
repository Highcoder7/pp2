from pathlib import Path


base_dir = Path(__file__).parent
sample_path = base_dir / "sample.txt"
only_once_path = base_dir / "only_once.txt"

print("Папка:", base_dir)

with open(sample_path, "w", encoding="utf-8") as f:
    f.write("Первая строка\n")
    f.write("Вторая строка\n")

print("Создан файл:", sample_path.name)

with open(sample_path, "a", encoding="utf-8") as f:
    f.write("Добавленная строка\n")

print("Добавлена строка в:", sample_path.name)

try:
    with open(only_once_path, "x", encoding="utf-8") as f:
        f.write("Этот файл создаётся только если его ещё нет\n")
    print("Создан файл в режиме x:", only_once_path.name)
except FileExistsError:
    print("Файл уже существует, режим x не сработал:", only_once_path.name)

with open(sample_path, "r", encoding="utf-8") as f:
    text = f.read()

print("Содержимое sample.txt:")
print(text)
