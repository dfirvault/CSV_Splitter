# CSV Splitter (Terminal-Based, Size or Line-Based)

A fast, terminal-based Python tool to split large CSV files by **file size (MB)** or **line count** — with automatic file size tracking, progress bar, and post-split data integrity check.

---

## Features

- 📁 **File selection dialog** — no need to type full paths
- 📦 **Split by size or number of lines**
- 📊 **Accurate size splitting** — no file exceeds your limit
- 🔍 **Data integrity check** — confirms all rows are preserved
- 📜 **Progress bar (tqdm)** for live feedback
<img width="1078" height="400" alt="image" src="https://github.com/user-attachments/assets/bf733005-6a1d-481e-927d-9578e8b9cc96" />

---

## How It Works

After selecting your CSV, choose:
- `size` → set max file size in MB (e.g., 500)
- `lines` → set max lines per file (excluding header)

Each output file will be named like:

- yourfile_split_1.csv
- yourfile_split_2.csv


After splitting, the script re-counts all rows across all split files and compares with the original. You'll be notified if any rows are lost.

---

## Usage

```bash
python csv_splitter.py
```
You’ll be prompted to:

- Select your input .csv
- Choose an output folder
- Choose split type: size or lines
- Provide a value (MB or line count)

## Requirements
Python 3.7+

tqdm for progress bar

Install dependencies:

```bash
pip install tqdm
```

## Example
Splitting a 611MB CSV into 500MB parts:
```bash
Split by: size
Max size: 500 MB
Split files saved as: mydata_split_1.csv, mydata_split_2.csv
✅ All rows verified: No data lost.
```

##Notes
- Output files retain the header (optional)
- File sizes are accurately tracked using real byte counts
- Fully terminal-based with modern file dialog (no GUI dependencies)

