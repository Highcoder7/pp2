from pathlib import Path
import shutil


base_dir = Path(__file__).parent
src_path = base_dir / "to_copy.txt"
backup_dir = base_dir / "backup"
backup_dir.mkdir(exist_ok=True)
backup_path = backup_dir / "to_copy_backup.txt"

with open(src_path, "w", encoding="utf-8") as f:
    f.write("Данные для копирования\n")

shutil.copy2(src_path, backup_path)

print("Исходный файл:", src_path)
print("Копия:", backup_path)
print("Копия существует:", backup_path.exists())

target_to_delete = src_path
safe_dir = base_dir.resolve()

if target_to_delete.exists() and target_to_delete.resolve().parent == safe_dir:
    target_to_delete.unlink()
    print("Удалён файл:", target_to_delete.name)
else:
    print("Удаление пропущено:", target_to_delete)

print("Исходный файл существует:", src_path.exists())
