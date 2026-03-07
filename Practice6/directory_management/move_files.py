from pathlib import Path
import shutil


base_dir = Path(__file__).parent
demo_dir = base_dir / "move_demo"
src_dir = demo_dir / "src"
dst_dir = demo_dir / "dst"

src_dir.mkdir(parents=True, exist_ok=True)
dst_dir.mkdir(parents=True, exist_ok=True)

src_file = src_dir / "note.txt"
with open(src_file, "w", encoding="utf-8") as f:
    f.write("Файл для перемещения и копирования\n")

copied_file = dst_dir / "note_copy.txt"
shutil.copy2(src_file, copied_file)

moved_file = dst_dir / "note_moved.txt"
shutil.move(str(src_file), str(moved_file))

print("SRC существует:", src_file.exists())
print("COPY существует:", copied_file.exists())
print("MOVED существует:", moved_file.exists())

print("Файлы в dst:", [p.name for p in dst_dir.iterdir()])
