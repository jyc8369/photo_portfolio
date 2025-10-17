import os
import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class PhotoManagerV2:
    def __init__(self, root):
        self.root = root
        self.root.title("사진 파일 관리 v2 (전체화면 최적화)")
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Configure>', self.on_window_resize)

        self.image_cache = {}
        self.photo_frames = []
        self._resize_timer = None
        self._last_width = 0

        self.images_dir = 'images'
        self.json_file = 'photos.json'
        self.photos = []

        self.category_map = {
            "인물": "portrait",
            "풍경": "landscape",
            "스트릿": "street",
            "자연": "nature",
            "건축": "architecture",
            "추상": "abstract",
            "도시": "cityscape",
            "음식": "food",
            "야경": "night",
            "스포츠": "sports",
            "노을": "sunset",
            "기타": "other"
        }

        self.load_json()
        self.create_widgets()
        self.refresh_photos()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(main_frame, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="📸 사진 포트폴리오 관리자 v2",
                             font=('TkDefaultFont', 16, 'bold'), bg='#34495e', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        esc_label = tk.Label(header_frame, text="ESC: 전체화면 해제",
                           font=('TkDefaultFont', 9), bg='#34495e', fg='#bdc3c7')
        esc_label.pack(side=tk.RIGHT, padx=20, pady=15)

        self.list_frame = tk.Frame(main_frame, bg='#ecf0f1')
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        list_title = tk.Label(self.list_frame, text="사진 파일 목록 (격자형)",
                            font=('TkDefaultFont', 12, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        list_title.pack(anchor=tk.W, pady=(0, 15))

        self.canvas = tk.Canvas(self.list_frame, bg='#ecf0f1', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.list_frame, orient="vertical",
                                    command=self.canvas.yview, bg='#bdc3c7')
        self.scrollable_frame = tk.Frame(self.canvas, bg='#ecf0f1')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.btn_frame = tk.Frame(main_frame, bg='#34495e', height=70)
        self.btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.btn_frame.pack_propagate(False)

        button_container = tk.Frame(self.btn_frame, bg='#34495e')
        button_container.pack(expand=True)

        self.save_btn = tk.Button(button_container, text="💾 JSON 저장", font=('TkDefaultFont', 10, 'bold'),
                                command=self.save_json, bg='#27ae60', fg='white', relief=tk.FLAT,
                                padx=20, pady=8, activebackground='#2ecc71')
        self.save_btn.pack(side=tk.LEFT, padx=10)

        self.refresh_btn = tk.Button(button_container, text="🔄 새로고침", font=('TkDefaultFont', 10, 'bold'),
                                   command=self.refresh_photos, bg='#3498db', fg='white', relief=tk.FLAT,
                                   padx=20, pady=8, activebackground='#5dade2')
        self.refresh_btn.pack(side=tk.LEFT, padx=10)

        self.cleanup_btn = tk.Button(button_container, text="🧹 캐시 정리", font=('TkDefaultFont', 10, 'bold'),
                                   command=self.cleanup_cache, bg='#e74c3c', fg='white', relief=tk.FLAT,
                                   padx=20, pady=8, activebackground='#ec7063')
        self.cleanup_btn.pack(side=tk.RIGHT, padx=10)

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
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.photo_frames.clear()

        if os.path.exists(self.images_dir):
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
            image_files = [f for f in os.listdir(self.images_dir) if f.lower().endswith(image_extensions)]

            existing_srcs = {p['src'] for p in self.photos}
            new_photos = []
            for filename in image_files:
                src = f"{self.images_dir}/{filename}"
                if src not in existing_srcs:
                    new_photos.append({
                        "src": src,
                        "title": filename,
                        "category": ["portrait"],
                        "alt": filename,
                        "alt2": ""
                    })
            self.photos.extend(new_photos)

            canvas_width = self.canvas.winfo_width()
            if canvas_width <= 1:
                canvas_width = self.root.winfo_width() - 100

            card_width = 260
            available_columns = max(3, canvas_width // card_width)
            columns = min(available_columns, 8)

            valid_photos = []
            for photo in self.photos:
                filename = os.path.basename(photo['src'])
                if filename in image_files:
                    valid_photos.append(filename)

            for i, filename in enumerate(valid_photos):
                row = i // columns
                col = i % columns
                self.create_photo_card(filename, row, col)

            for col in range(columns):
                self.scrollable_frame.columnconfigure(col, weight=1)

            total_rows = (len(valid_photos) + columns - 1) // columns
            for row in range(total_rows):
                self.scrollable_frame.rowconfigure(row, weight=1)
        else:
            os.makedirs(self.images_dir)
            tk.Label(self.scrollable_frame, text=f"{self.images_dir} 폴더를 생성했습니다. 사진 파일을 넣으세요.",
                    font=('TkDefaultFont', 12)).pack(pady=50)

    def create_photo_card(self, filename, row, col):
        src = f"{self.images_dir}/{filename}"

        existing = next((p for p in self.photos if p['src'] == src), None)
        if existing:
            current_title = existing.get('title', filename)
            current_category_list = existing.get('category', ['portrait'])
            if isinstance(current_category_list, str):
                current_category_list = [current_category_list]
            current_alt = existing.get('alt', filename)
            current_alt2 = existing.get('alt2', '')
        else:
            current_title = filename
            current_category_list = ['portrait']
            current_alt = filename
            current_alt2 = ''

        card_frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, borderwidth=2, bg='#f8f9fa')
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
        self.photo_frames.append(card_frame)

        try:
            if src not in self.image_cache:
                img = Image.open(src)
                img.thumbnail((160, 160))
                self.image_cache[src] = ImageTk.PhotoImage(img)

            img_label = tk.Label(card_frame, image=self.image_cache[src], bg='#f8f9fa')
            img_label.pack(pady=(10, 5))
        except Exception as e:
            img_label = tk.Label(card_frame, text="[이미지]", width=20, height=12, bg='lightgray', fg='gray')
            img_label.pack(pady=(10, 5))

        filename_label = tk.Label(card_frame, text=filename[:20] + "..." if len(filename) > 20 else filename,
                                font=('TkDefaultFont', 11, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        filename_label.pack(pady=(0, 5))

        title_frame = tk.Frame(card_frame, bg='#f8f9fa')
        title_frame.pack(fill=tk.X, padx=6, pady=3)
        tk.Label(title_frame, text="제목:", font=('TkDefaultFont', 10), bg='#f8f9fa', fg='#34495e').pack(anchor=tk.W)
        title_entry = tk.Entry(title_frame, font=('TkDefaultFont', 10), relief=tk.FLAT, bg='#ecf0f1')
        title_entry.insert(0, current_title)
        title_entry.pack(fill=tk.X, ipady=3)

        category_frame = tk.Frame(card_frame, bg='#f8f9fa')
        category_frame.pack(fill=tk.X, padx=6, pady=3)

        tk.Label(category_frame, text="카테고리:", font=('TkDefaultFont', 10), bg='#f8f9fa', fg='#34495e').pack(anchor=tk.W)

        checkbox_frame = tk.Frame(category_frame, bg='#f8f9fa')
        checkbox_frame.pack(fill=tk.X)

        for col in range(2):
            checkbox_frame.columnconfigure(col, weight=1)

        card_category_vars = {}

        for i, (korean, english) in enumerate(list(self.category_map.items())):
            card_category_vars[english] = tk.BooleanVar(value=english in current_category_list)

            initial_bg = '#3498db' if card_category_vars[english].get() else '#f8f9fa'
            cb = tk.Checkbutton(checkbox_frame, text=korean, variable=card_category_vars[english],
                              font=('TkDefaultFont', 9), bg=initial_bg,
                              fg='#34495e', selectcolor='#3498db', indicatoron=False,
                              relief=tk.RAISED, bd=1, width=6, padx=4, pady=4)
            cb.grid(row=i//2, column=i%2, sticky='ew', padx=2, pady=2)

            card_category_vars[english].trace_add('write', 
                lambda *args, var=card_category_vars[english], btn=cb: 
                    btn.config(bg='#3498db' if var.get() else '#f8f9fa'))

        card_frame.category_vars = card_category_vars

        desc_frame = tk.Frame(card_frame, bg='#f8f9fa')
        desc_frame.pack(fill=tk.X, padx=6, pady=3)

        tk.Label(desc_frame, text="설명 1:", font=('TkDefaultFont', 10), bg='#f8f9fa', fg='#34495e').grid(row=0, column=0, sticky=tk.W)
        alt_entry = tk.Entry(desc_frame, font=('TkDefaultFont', 10), relief=tk.FLAT, bg='#ecf0f1')
        alt_entry.insert(0, current_alt)
        alt_entry.grid(row=0, column=1, sticky=tk.EW, padx=(5,0), ipady=3)

        tk.Label(desc_frame, text="설명 2:", font=('TkDefaultFont', 10), bg='#f8f9fa', fg='#34495e').grid(row=1, column=0, sticky=tk.W, pady=(5,0))
        alt2_entry = tk.Entry(desc_frame, font=('TkDefaultFont', 10), relief=tk.FLAT, bg='#ecf0f1')
        alt2_entry.insert(0, current_alt2)
        alt2_entry.grid(row=1, column=1, sticky=tk.EW, padx=(5,0), ipady=3, pady=(5,0))

        desc_frame.columnconfigure(1, weight=1)

        title_entry.bind('<FocusOut>', lambda e: self.auto_save_photo_info(src, title_entry, alt_entry, alt2_entry, card_category_vars, filename))
        alt_entry.bind('<FocusOut>', lambda e: self.auto_save_photo_info(src, title_entry, alt_entry, alt2_entry, card_category_vars, filename))
        alt2_entry.bind('<FocusOut>', lambda e: self.auto_save_photo_info(src, title_entry, alt_entry, alt2_entry, card_category_vars, filename))
        
        for widget in checkbox_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.config(command=lambda: self.auto_save_photo_info(src, title_entry, alt_entry, alt2_entry, card_category_vars, filename))

        desc_frame.columnconfigure(1, weight=1)

        button_frame = tk.Frame(card_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, padx=6, pady=(5, 12))

        save_btn = tk.Button(button_frame, text="수동 저장", font=('TkDefaultFont', 9, 'bold'),
                           command=lambda: self.save_photo_info(src, title_entry, alt_entry, alt2_entry, card_category_vars, filename),
                           bg='#95a5a6', fg='white', relief=tk.FLAT, padx=10, pady=3)
        save_btn.pack(side=tk.LEFT, padx=2)

        up_btn = tk.Button(button_frame, text="↑", font=('TkDefaultFont', 10, 'bold'),
                          command=lambda: self.move_up(src), bg='#3498db', fg='white', relief=tk.FLAT, padx=8, pady=3)
        up_btn.pack(side=tk.RIGHT, padx=2)

        down_btn = tk.Button(button_frame, text="↓", font=('TkDefaultFont', 10, 'bold'),
                           command=lambda: self.move_down(src), bg='#3498db', fg='white', relief=tk.FLAT, padx=8, pady=3)
        down_btn.pack(side=tk.RIGHT, padx=2)

    def auto_save_photo_info(self, src, title_entry, alt_entry, alt2_entry, category_vars, filename):
        title = title_entry.get() or filename
        category = [eng for eng, var in category_vars.items() if var.get()]
        if not category:
            category = ['other']
        alt = alt_entry.get() or filename
        alt2 = alt2_entry.get() or ""

        existing = next((p for p in self.photos if p['src'] == src), None)
        if existing:
            existing['title'] = title
            existing['category'] = category
            existing['alt'] = alt
            existing['alt2'] = alt2
        else:
            self.photos.append({
                "src": src,
                "title": title,
                "category": category,
                "alt": alt,
                "alt2": alt2
            })

    def save_photo_info(self, src, title_entry, alt_entry, alt2_entry, category_vars, filename):
        title = title_entry.get() or filename
        category = [eng for eng, var in category_vars.items() if var.get()]
        if not category:
            category = ['other']
        alt = alt_entry.get() or filename
        alt2 = alt2_entry.get() or ""

        existing = next((p for p in self.photos if p['src'] == src), None)
        if existing:
            existing['title'] = title
            existing['category'] = category
            existing['alt'] = alt
            existing['alt2'] = alt2
        else:
            self.photos.append({
                "src": src,
                "title": title,
                "category": category,
                "alt": alt,
                "alt2": alt2
            })

    def save_json(self):
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.photos, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("성공", f"{self.json_file} 파일이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {str(e)}")

    def move_up(self, src):
        index = next((i for i, p in enumerate(self.photos) if p['src'] == src), -1)
        if index > 0:
            self.photos[index], self.photos[index - 1] = self.photos[index - 1], self.photos[index]
            self.refresh_photos()

    def move_down(self, src):
        index = next((i for i, p in enumerate(self.photos) if p['src'] == src), -1)
        if index >= 0 and index < len(self.photos) - 1:
            self.photos[index], self.photos[index + 1] = self.photos[index + 1], self.photos[index]
            self.refresh_photos()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_window_resize(self, event):
        if event.widget == self.root:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)

            self._resize_timer = self.root.after(200, self._debounced_refresh)

    def _debounced_refresh(self):
        current_width = self.root.winfo_width()
        if abs(self._last_width - current_width) > 100:
            self.refresh_photos()
            self._last_width = current_width
        self._resize_timer = None

    def cleanup_cache(self):
        current_files = set()
        if os.path.exists(self.images_dir):
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
            current_files = {f"{self.images_dir}/{f}" for f in os.listdir(self.images_dir)
                           if f.lower().endswith(image_extensions)}

        to_remove = [src for src in self.image_cache if src not in current_files]
        for src in to_remove:
            del self.image_cache[src]

        if len(self.image_cache) > 50:
            items = list(self.image_cache.items())
            self.image_cache = dict(items[-50:])

        messagebox.showinfo("캐시 정리", f"이미지 캐시가 정리되었습니다. (현재 {len(self.image_cache)}개 유지)")

    def on_closing(self):
        try:
            self.image_cache.clear()
            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)
            self.photo_frames.clear()
        except:
            pass
        finally:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = PhotoManagerV2(root)
    root.mainloop()

if __name__ == "__main__":
    main()