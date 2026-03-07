from pathlib import Path


base_dir = Path(__file__).parent
sample_path = base_dir / "sample.txt"

if not sample_path.exists():
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write("Строка 1\n")
        f.write("Строка 2\n")
        f.write("Строка 3\n")

print("Файл:", sample_path.name)

with open(sample_path, "r", encoding="utf-8") as f:
    all_text = f.read()

print("read():")
print(all_text)

with open(sample_path, "r", encoding="utf-8") as f:
    first_line = f.readline()
    second_line = f.readline()

print("readline():")
print(first_line.rstrip("\n"))
print(second_line.rstrip("\n"))

with open(sample_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("readlines():")
print("Количество строк:", len(lines))
for line in lines:
    print(line.rstrip("\n"))
