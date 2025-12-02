import os
import json
import hashlib
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel


console = Console()

def print_header(text):
    """Выводит заголовок"""
    console.print(Panel(text, border_style="cyan"))

def print_success(text):
    """Выводит сообщение об успехе"""
    console.print("[green]>[/green] " + text)

def print_error(text):
    """Выводит сообщение об ошибке"""
    console.print("[red]![/red] " + text)

def print_info(text):
    """Выводит информационное сообщение"""
    console.print("[blue]*[/blue] " + text)

def calculate_sha256(file_path):
    """Вычисляет SHA-256 хеш файла"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def scan_directory(root_dir):
    """Сканирует директорию и создает список с информацией о файлах"""
    files_data = []
    all_files = []
    

    print_info("составляем список файлов...")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root_dir)
            rel_path = rel_path.replace('\\', '/')
            all_files.append((full_path, rel_path))
    
    total_files = len(all_files)
    print_info(f"найдено файлов: {total_files}")
    

    with Progress(
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="cyan"),
        TaskProgressColumn(),
        TextColumn("[cyan]{task.fields[filename]}"),
    ) as progress:
        task = progress.add_task("сканирование", total=total_files, filename="")
        
        for index, (full_path, rel_path) in enumerate(all_files):
            try:
                progress.update(task, advance=1, filename=rel_path[:30])
                
                file_size = os.path.getsize(full_path)
                file_hash = calculate_sha256(full_path)
                
                files_data.append({
                    "file": rel_path,
                    "hash": file_hash,
                    "size": file_size
                })
                
            except Exception as e:
                progress.stop()
                print_error(f"ошибка при обработке файла {rel_path}: {e}")
    
    return files_data

def main():
    print_header("api.json | by raxed and semtab")
    
    game_files_dir = "files"
    output_file = "api.json"
    
    if not os.path.exists(game_files_dir):
        print_error(f"директория {game_files_dir} не найдена!")
        print_info("создайте папку 'files' и поместите в неё файлы игры")
        return
    
    print_info(f"сканирование директории {game_files_dir}...")
    files_data = scan_directory(game_files_dir)
    

    print_info(f"сохраняем информацию в {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(files_data, f, ensure_ascii=False, indent=4)
    
    print_success(f"готово! создан файл {output_file} с информацией о {len(files_data)} файлах.")
    print_info("этот файл нужно загрузить на сервер для работы лаунчера.")

if __name__ == "__main__":
    try:
        start_time = datetime.now()
        main()
        end_time = datetime.now()
        execution_time = end_time - start_time
        
        print_header("info")
        print_info(f"время выполнения: {execution_time}")
        print_info("для завершения нажмите любую клавишу...")
        input()
    except KeyboardInterrupt:
        print_error("\nпрервано пользователем!")
    except Exception as e:
        print_error(f"\nошибка: {e}")
        input("нажмите enter для выхода...")