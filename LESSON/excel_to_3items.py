import os
import pandas as pd
from gtts import gTTS
import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Hàm chọn file Excel
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

# Hàm lấy tên bài học từ tên file
def get_lesson_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

# Hàm tạo âm thanh và file mapping JSON
def create_audio_and_mapping(df, lesson_name):
    output_dir = f"audio_{lesson_name}"
    os.makedirs(output_dir, exist_ok=True)

    words_col0 = df.iloc[:, 0].dropna().astype(str).tolist()
    words_col3 = df.iloc[:, 3].dropna().astype(str).tolist()

    audio_mapping = []
    for idx, (word0, word3) in enumerate(zip(words_col0, words_col3)):
        # Chuẩn hóa dấu nháy
        word0 = word0.replace("’", "'").replace("“", '"').replace("”", '"')
        word3 = word3.replace("’", "'").replace("“", '"').replace("”", '"')

        # Âm thanh cột 0
        filename0 = f"{output_dir}/audio_{lesson_name}_{idx + 1}_col0.mp3"
        tts0 = gTTS(word0, lang="en")
        tts0.save(filename0)
        audio_mapping.append({"text": word0, "file": filename0})

        # Âm thanh cột 3
        filename3 = f"{output_dir}/audio_{lesson_name}_{idx + 1}_col3.mp3"
        tts3 = gTTS(word3, lang="en")
        tts3.save(filename3)
        audio_mapping.append({"text": word3, "file": filename3})

    mapping_file = f"mapping_{lesson_name}.json"
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(audio_mapping, f, ensure_ascii=False, indent=4)

    return output_dir, mapping_file

# Hàm tạo file JSON 6 cột
def create_lesson_json(df, lesson_name):
    # Chuẩn hóa dữ liệu: Chuyển tất cả giá trị thành chuỗi và thay thế dấu nháy cong thành dấu nháy thẳng
    df = df.applymap(lambda x: str(x).replace("’", "'") if isinstance(x, str) else str(x))

    # Chuyển đổi dữ liệu thành danh sách
    data = df.iloc[:, :6].fillna("").values.tolist()

    # In dữ liệu JSON ra console để kiểm tra
    print(json.dumps(data, ensure_ascii=False, indent=4))  

    # Tạo file JSON
    lesson_json = f"{lesson_name}.json"
    with open(lesson_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return lesson_json

# Hàm xử lý chính khi bấm nút "Tạo Tất Cả"
def generate_all():
    file_path = entry_file.get()
    if not file_path:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
        return
    
    try:
        df = pd.read_excel(file_path)
        lesson_name = get_lesson_name(file_path)

        # Kiểm tra số cột
        if df.shape[1] < 6:
            messagebox.showerror("Lỗi", "File Excel phải có ít nhất 6 cột!")
            return

        # 1. Tạo âm thanh và mapping
        output_dir, mapping_file = create_audio_and_mapping(df, lesson_name)

        # 2. Tạo file JSON 6 cột
        lesson_json = create_lesson_json(df, lesson_name)

        messagebox.showinfo(
            "Hoàn tất",
            f"Đã tạo thành công:\n- Thư mục âm thanh: {output_dir}\n- Mapping JSON: {mapping_file}\n- Lesson JSON: {lesson_json}"
        )
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi thực hiện: {str(e)}")

# Giao diện GUI
root = tk.Tk()
root.title("Chương Trình 3 Trong 1: Audio - Mapping - Lesson JSON")
root.geometry("550x250")

# Label + Entry để chọn file Excel
tk.Label(root, text="File Excel:").pack(pady=5)
frame_file = tk.Frame(root)
frame_file.pack()
entry_file = tk.Entry(frame_file, width=60)
entry_file.pack(side=tk.LEFT, padx=5)
btn_select = tk.Button(frame_file, text="Chọn File", command=select_file)
btn_select.pack(side=tk.LEFT)

# Nút thực hiện tất cả
btn_generate = tk.Button(root, text="Tạo Tất Cả", command=generate_all, bg="green", fg="white")
btn_generate.pack(pady=20)

# Chạy giao diện
root.mainloop()
