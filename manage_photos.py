import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class PhotoManager:
    def __init__(self, root):
        self.root = root
        self.root.title("사진 파일 관리")
        self.root.geometry("700x500")

        self.images_dir = 'images'  # 고정 폴더
        self.json_file = 'photos.json'
        self.photos = []

        # 기존 JSON 데이터 로드
        self.load_json()

        # UI 요소
        self.create_widgets()
        self.refresh_photos()

    def create_widgets(self):
        # 사진 리스트 프레임
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.list_frame, text="사진 파일 목록:").pack(anchor=tk.W)

        # 스크롤 가능한 캔버스
        self.canvas = tk.Canvas(self.list_frame)
        self.scrollbar = tk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 버튼들
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.save_btn = tk.Button(self.btn_frame, text="JSON 저장", command=self.save_json)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = tk.Button(self.btn_frame, text="새로고침", command=self.refresh_photos)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

    def load_json(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.photos = json.load(f)
            except Exception as e:
                messagebox.showerror("오류", f"JSON 로드 실패: {str(e)}")
                self.photos = []
        else:
            self.photos = []

    def refresh_photos(self):
        # 기존 위젯 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        if os.path.exists(self.images_dir):
            image_files = [f for f in os.listdir(self.images_dir) if f.lower().endswith(image_extensions)]
            for filename in image_files:
                self.create_photo_row(filename)
        else:
            os.makedirs(self.images_dir)
            tk.Label(self.scrollable_frame, text=f"{self.images_dir} 폴더를 생성했습니다. 사진 파일을 넣으세요.").pack()

    def create_photo_row(self, filename):
        src = f"{self.images_dir}/{filename}"

        # 기존 데이터 찾기
        existing = next((p for p in self.photos if p['src'] == src), None)
        if existing:
            current_title = existing.get('title', filename)
            current_category = existing.get('category', 'portrait')
            current_alt = existing.get('alt', filename)
            current_alt2 = existing.get('alt2', '')  # 설명2 추가
        else:
            current_title = filename
            current_category = 'portrait'
            current_alt = filename
            current_alt2 = ''

        # 행 프레임
        row_frame = tk.Frame(self.scrollable_frame)
        row_frame.pack(fill=tk.X, pady=5)

        # 파일명 라벨
        tk.Label(row_frame, text=filename, width=20, anchor='w').pack(side=tk.LEFT, padx=5)

        # 제목 라벨과 엔트리
        tk.Label(row_frame, text="제목:").pack(side=tk.LEFT, padx=5)
        title_entry = tk.Entry(row_frame)
        title_entry.insert(0, current_title)
        title_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # 카테고리 라벨과 콤보
        tk.Label(row_frame, text="카테고리:").pack(side=tk.LEFT, padx=5)
        category_var = tk.StringVar(value=current_category)
        category_combo = ttk.Combobox(row_frame, textvariable=category_var, width=15,
                                      values=["portrait", "landscape", "street", "nature", "architecture", "macro", "other"])
        category_combo.pack(side=tk.LEFT, padx=5)

        # 설명 라벨과 엔트리
        tk.Label(row_frame, text="설명:").pack(side=tk.LEFT, padx=5)
        alt_entry = tk.Entry(row_frame)
        alt_entry.insert(0, current_alt)
        alt_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # 설명2 라벨과 엔트리
        tk.Label(row_frame, text="설명2:").pack(side=tk.LEFT, padx=5)
        alt2_entry = tk.Entry(row_frame)
        alt2_entry.insert(0, current_alt2)
        alt2_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # 저장 버튼
        save_btn = tk.Button(row_frame, text="저장", command=lambda: self.save_photo_info(src, title_entry, category_var, alt_entry, alt2_entry, filename))
        save_btn.pack(side=tk.RIGHT, padx=5)

    def save_photo_info(self, src, title_entry, category_var, alt_entry, alt2_entry, filename):
        title = title_entry.get() or filename
        category = category_var.get()
        alt = alt_entry.get() or filename
        alt2 = alt2_entry.get()  # 설명2 추가

        # 기존에 있는지 확인
        existing = next((p for p in self.photos if p['src'] == src), None)
        if existing:
            existing['title'] = title
            existing['category'] = category
            existing['alt'] = alt
            existing['alt2'] = alt2  # 설명2 저장
        else:
            self.photos.append({
                "src": src,
                "title": title,
                "category": category,
                "alt": alt,
                "alt2": alt2  # 설명2 추가
            })

        messagebox.showinfo("성공", f"'{filename}' 정보가 저장되었습니다.")

    def save_json(self):
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.photos, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("성공", f"{self.json_file} 파일이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {str(e)}")

def main():
    root = tk.Tk()
    app = PhotoManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()