import os
import csv
import time
import io
from tqdm import tqdm
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog

# ───────────────────────────────────────────────
# Developed by Jacob Wilson - Version 0.1
# dfirvault@gmail.com
# ───────────────────────────────────────────────

def get_file_size(filename):
    return os.path.getsize(filename) / (1024 * 1024)

def count_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)

class CountingWriter:
    def __init__(self, file_handle):
        self.file_handle = file_handle
        self.byte_count = 0

    def write(self, data):
        encoded = data.encode('utf-8')
        self.byte_count += len(encoded)
        self.file_handle.write(data)

    def flush(self):
        self.file_handle.flush()

    def close(self):
        self.file_handle.close()

    def get_size_mb(self):
        return self.byte_count / (1024 * 1024)

def split_by_lines(input_file, output_prefix, lines_per_file, duplicate_header):
    start_time = time.time()
    total_lines = count_lines(input_file)
    if duplicate_header:
        total_lines -= 1

    split_files = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) if duplicate_header else None

        file_count = 1
        current_line = 0
        writer = None
        current_file = None

        with tqdm(total=total_lines, desc="Splitting by lines", unit="lines") as pbar:
            for row in reader:
                if current_line % lines_per_file == 0:
                    if current_file:
                        current_file.close()
                    output_file = f"{output_prefix}_{file_count}.csv"
                    current_file = open(output_file, 'w', newline='', encoding='utf-8')
                    split_files.append(output_file)
                    writer = csv.writer(current_file)
                    if duplicate_header and header:
                        writer.writerow(header)
                    file_count += 1
                writer.writerow(row)
                current_line += 1
                pbar.update(1)

            if current_file:
                current_file.close()

    print(f"\n✅ Done! Created {file_count - 1} files in {time.time() - start_time:.2f}s")
    return split_files

def split_by_size(input_file, output_prefix, max_size_mb, duplicate_header):
    start_time = time.time()
    total_size_mb = get_file_size(input_file)

    split_files = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) if duplicate_header else None

        file_count = 1
        processed_size = 0

        def open_new_file():
            nonlocal file_count
            output_file = f"{output_prefix}_{file_count}.csv"
            f = open(output_file, 'w', newline='', encoding='utf-8')
            counting_writer = CountingWriter(f)
            writer = csv.writer(counting_writer)
            if header:
                writer.writerow(header)
            file_count += 1
            split_files.append(output_file)
            return counting_writer, writer

        counting_writer, writer = open_new_file()

        with tqdm(total=total_size_mb, desc="Splitting by size", unit="MB") as pbar:
            for row in reader:
                temp_io = io.StringIO()
                temp_writer = csv.writer(temp_io)
                temp_writer.writerow(row)
                row_data = temp_io.getvalue()

                row_size_mb = len(row_data.encode('utf-8')) / (1024 * 1024)

                if counting_writer.get_size_mb() + row_size_mb > max_size_mb:
                    counting_writer.close()
                    counting_writer, writer = open_new_file()

                writer.writerow(row)
                processed_size += row_size_mb
                pbar.update(row_size_mb)

            counting_writer.close()

    print(f"\n✅ Done! Created {file_count - 1} files in {time.time() - start_time:.2f}s")
    return split_files

def verify_line_integrity(original_file, split_files, duplicate_header):
    original_lines = count_lines(original_file) - 1  # Exclude header
    split_total = 0

    for file in split_files:
        with open(file, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
            if duplicate_header:
                lines -= 1
            split_total += lines

    print("\n🧪 Verifying line integrity...")
    print(f"Original file lines (excluding header): {original_lines:,}")
    print(f"Total lines in split files:            {split_total:,}")

    if split_total == original_lines:
        print("✅ Line integrity check passed: all lines accounted for.")
    else:
        diff = original_lines - split_total
        print(f"❌ Line integrity check failed! Difference: {diff:+,} lines")

def main():
    print("\nDeveloped by Jacob Wilson - Version 0.1")
    print("dfirvault@gmail.com\n")

    # File picker
    tk.Tk().withdraw()
    input_file = filedialog.askopenfilename(
        title="Select CSV file to split",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not input_file:
        print("No file selected. Exiting.")
        return

    file_size_mb = get_file_size(input_file)
    total_lines = count_lines(input_file) - 1

    print(f"\n📄 Loaded file: {os.path.basename(input_file)}")
    print(f"Size: {file_size_mb:.2f} MB | Lines: {total_lines:,}")

    # Split method
    method = input("Split by (1) Size (MB) or (2) Number of lines? Enter 1 or 2: ").strip()
    if method == '1':
        try:
            max_size = float(input("Enter max size for each split file in MB (e.g., 500): ").strip())
        except ValueError:
            print("Invalid size input. Exiting.")
            return
        split_type = 'size'
    elif method == '2':
        try:
            max_lines = int(input("Enter max number of lines per split file (e.g., 100000): ").strip())
        except ValueError:
            print("Invalid line input. Exiting.")
            return
        split_type = 'lines'
    else:
        print("Invalid selection.")
        return

    duplicate_header = input("Duplicate header in each split file? (y/n): ").strip().lower() == 'y'

    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if not output_dir:
        print("No output directory selected. Exiting.")
        return

    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_path = os.path.join(output_dir, base_filename + "_split")

    try:
        if split_type == 'size':
            split_files = split_by_size(input_file, output_path, max_size, duplicate_header)
        else:
            split_files = split_by_lines(input_file, output_path, max_lines, duplicate_header)

        print(f"\n📁 Split files saved with prefix: {os.path.normpath(output_path)}_#.csv")
        verify_line_integrity(input_file, split_files, duplicate_header)

        def open_folder(path):
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux and others
                subprocess.run(["xdg-open", path])
        print("\nOpening output folder...")
        open_folder(output_dir)            
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
