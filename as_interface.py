import json
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from language_dict import LANG

SETTINGS_FILE = "auto_scroller_settings.json"
LANG_FLAGS = {
    "en": "united-kingdom.png",
    "el": "greece.png",
}


class Interface:

    def __init__(self, bundled_path, data_dir):
        self.bundled_path = bundled_path
        self.data_dir = data_dir
        self.settings_path = os.path.join(data_dir, SETTINGS_FILE)

        self.lang = LANG
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                self.active_lang = json.load(f).get("language", "en")
        except (json.JSONDecodeError, OSError):
            self.active_lang = "en"
        if self.active_lang not in self.lang:
            self.active_lang = "en"

        self.root = tk.Tk()
        self.root.title(self.lang[self.active_lang]["app_title"])
        self.root.geometry("350x420")
        self.root.minsize(350, 420)
        self.root.maxsize(350, 420)
        self.root.withdraw()

        self._setup_styles()
        self._setup_background()
        self._setup_widgets()
        self._load_settings()

        self.root.protocol("WM_DELETE_WINDOW", self.hide)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox", fieldbackground="#F8E7C9", background="#F8E7C9", borderwidth=0, relief="flat")
        style.map("TCombobox",
            borderwidth=[("readonly", 0)],
            background=[("readonly", "#F8E7C9"), ("pressed", "#F8E7C9"), ("focus", "#F8E7C9"), ("active", "#F8E7C9")],
        )
        style.configure("Save.TButton", background="#78613B", foreground="white")
        style.map("Save.TButton",
            background=[("active", "#CDBFA9"), ("pressed", "#4D4333")],
        )

    def _setup_background(self):
        bg_image = ImageTk.PhotoImage(Image.open(self.bundled_path("bg.png")).resize((350, 420)))
        bg_label = tk.Label(self.root, image=bg_image)
        bg_label.image = bg_image
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        flag_image = ImageTk.PhotoImage(Image.open(self.bundled_path(LANG_FLAGS[self.active_lang])).resize((18, 18)))
        self.flag_btn = tk.Button(self.root, image=flag_image, borderwidth=0, highlightthickness=0, cursor="hand2", command=self._cycle_language)
        self.flag_btn.image = flag_image
        self.flag_btn.place(x=6, y=6)

    def _setup_widgets(self):
        translated_variables = self.lang[self.active_lang]
        container = tk.Frame(self.root)
        container.place(relx=0.5, rely=0.5, anchor="center")

        def on_select(event):
            event.widget.selection_clear()
            self.root.focus()

        # Max click timer
        max_frame = tk.Frame(container)
        max_frame.pack(pady=8)
        self.max_label = tk.Label(max_frame, text=translated_variables["max_click_timer"], width=10, anchor="w")
        self.max_label.pack(side="left")
        self.max_var = tk.StringVar()
        max_combo = ttk.Combobox(max_frame, textvariable=self.max_var, values=list(range(20, 121)), width=4, state="readonly", exportselection=False, justify="center")
        max_combo.pack(side="left", padx=5)
        max_combo.bind("<<ComboboxSelected>>", on_select)

        # Min click timer
        min_frame = tk.Frame(container)
        min_frame.pack(pady=8)
        self.min_label = tk.Label(min_frame, text=translated_variables["min_click_timer"], width=10, anchor="w")
        self.min_label.pack(side="left")
        self.min_var = tk.StringVar()
        min_combo = ttk.Combobox(min_frame, textvariable=self.min_var, values=list(range(10, 40)), width=4, state="readonly", exportselection=False, justify="center")
        min_combo.pack(side="left", padx=5)
        min_combo.bind("<<ComboboxSelected>>", on_select)

        # Use sound instead
        self.use_sound_var = tk.IntVar()
        self.use_sound_check = tk.Checkbutton(container, text=translated_variables["use_sound_instead"], variable=self.use_sound_var, onvalue=1, offvalue=0)
        self.use_sound_check.pack(pady=8)

        # Timer limit
        timer_frame = tk.Frame(container)
        timer_frame.pack(pady=8)
        self.timer_label = tk.Label(timer_frame, text=translated_variables["timer_limit"], width=10, anchor="w")
        self.timer_label.pack(side="left")
        self.timer_var = tk.StringVar()
        timer_combo = ttk.Combobox(timer_frame, textvariable=self.timer_var, values=list(range(1, 121)), width=4, state="readonly", exportselection=False, justify="center")
        timer_combo.pack(side="left", padx=5)
        timer_combo.bind("<<ComboboxSelected>>", on_select)

        # Save button
        self.save_btn = ttk.Button(container, text=translated_variables["save"], style="Save.TButton", command=self._save_settings, cursor="hand2")
        self.save_btn.pack(pady=12)

    def _cycle_language(self):
        languages = list(self.lang.keys())
        next_index = (languages.index(self.active_lang) + 1) % len(languages)
        self.active_lang = languages[next_index]

        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except (json.JSONDecodeError, OSError):
            settings = {}
        settings["language"] = self.active_lang
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        translated_variables = self.lang[self.active_lang]
        self.root.title(translated_variables["app_title"])
        self.max_label.config(text=translated_variables["max_click_timer"])
        self.min_label.config(text=translated_variables["min_click_timer"])
        self.use_sound_check.config(text=translated_variables["use_sound_instead"])
        self.timer_label.config(text=translated_variables["timer_limit"])
        self.save_btn.config(text=translated_variables["save"])

        flag_image = ImageTk.PhotoImage(Image.open(self.bundled_path(LANG_FLAGS[self.active_lang])).resize((18, 18)))
        self.flag_btn.config(image=flag_image)
        self.flag_btn.image = flag_image

    def _load_settings(self):
        self.max_var.set("")
        self.min_var.set("")
        self.use_sound_var.set(False)
        self.timer_var.set("")
        if not os.path.exists(self.settings_path):
            return
        try:
            with open(self.settings_path, "r") as f:
                settings = json.load(f)
            if "max_click_timer" in settings:
                self.max_var.set(settings["max_click_timer"])
            if "min_click_timer" in settings:
                self.min_var.set(settings["min_click_timer"])
            if settings.get("use_sound") is not None:
                self.use_sound_var.set(1 if settings["use_sound"] else 0)
            if "timer_limit" in settings:
                self.timer_var.set(settings["timer_limit"])
        except (json.JSONDecodeError, OSError):
            pass

    def _save_settings(self):
        os.makedirs(self.data_dir, exist_ok=True)
        settings = {
            "max_click_timer": self.max_var.get(),
            "min_click_timer": self.min_var.get(),
            "use_sound": self.use_sound_var.get() == 1,
            "timer_limit": self.timer_var.get(),
        }
        with open(self.settings_path, "w") as f:
            json.dump(settings, f, indent=2)

    def reset(self):
        self.root.after(0, self._load_settings)

    def show(self):
        self.root.after(0, self._bring_to_front)

    def _bring_to_front(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(100, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def hide(self):
        self._load_settings()
        self.root.withdraw()