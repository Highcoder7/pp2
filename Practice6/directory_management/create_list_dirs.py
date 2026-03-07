import os
from pathlib import Path


base_dir = Path(__file__).parent
work_dir = base_dir / "demo_dirs"
nested_dir = work_dir / "a" / "b" / "c"

os.makedirs(nested_dir, exist_ok=True)

single_dir = work_dir / "single"
if not single_dir.exists():
    os.mkdir(single_dir)

with open(work_dir / "one.txt", "w", encoding="utf-8") as f:
    f.write("one\n")
with open(work_dir / "two.py", "w", encoding="utf-8") as f:
    f.write("print('two')\n")
with open(work_dir / "three.md", "w", encoding="utf-8") as f:
    f.write("three\n")

start_cwd = os.getcwd()
print("os.getcwd():", start_cwd)

os.chdir(work_dir)
print("os.chdir() -> cwd:", os.getcwd())

items = os.listdir(".")
print("os.listdir():", items)

txt_files = [name for name in items if name.endswith(".txt")]
print("Файлы .txt:", txt_files)

os.chdir(start_cwd)
print("Возврат cwd:", os.getcwd())

empty_dir = work_dir / "empty_to_remove"
os.makedirs(empty_dir, exist_ok=True)
os.rmdir(empty_dir)
print("os.rmdir() удалил:", empty_dir.name)
