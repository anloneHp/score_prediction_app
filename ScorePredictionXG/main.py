import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from comparison import ComparisonApp
from training import train_model_function
from prediction import PredictModel
from second_half import SecondHalfPrediction
from squadcomp import FirstElevenComparison
from first_eleven_predict import ScorePrediction2


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Score Prediction App")
        self.root.geometry("800x600")
        self.root.bind("<Configure>", self.resize_background)

        # Arka plan ve ana çerçeve
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.background_image = None
        self.main_frame = tk.Frame(self.canvas, bg="white", bd=2, relief=tk.RAISED)
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Butonlar
        self.create_buttons()

        # Ana sayfa görünümü
        self.show_home()

    def create_buttons(self):
        self.buttons = [
            ("Ana Sayfa", "#4caf50", self.show_home),
            ("Oyuncu Karşılaştır", "#4caf50", self.open_comparison_page),
            ("Modeli Eğit", "#2196f3", self.train_model),
            ("Tahmin Yap", "#f44336", self.open_prediction_page),
            ("Squad Karşılaştır", "#f44336", self.open_squadcomp_page),
            ("İlk 11 Tahmin", "#f44336", self.open_predict_page),
            ("İkinci Yarı Tahmin", "#ff9800", self.open_second_half_page),
        ]

        for idx, (text, color, command) in enumerate(self.buttons):
            tk.Button(
                self.main_frame,
                text=text,
                font=("Helvetica", 14),
                bg=color,
                fg="white",
                width=20,
                command=command,
            ).grid(row=idx, column=0, pady=10)

    def set_background(self, path):
        try:
            self.background_image = Image.open(path)
            self.update_background()
        except Exception as e:
            messagebox.showerror("Hata", f"Arka plan yüklenemedi: {e}")

    def resize_background(self, event=None):
        self.update_background()

    def update_background(self):
        if self.background_image:
            resized_image = self.background_image.resize(
                (self.root.winfo_width(), self.root.winfo_height()), Image.Resampling.LANCZOS
            )
            self.bg_image = ImageTk.PhotoImage(resized_image)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

    def show_home(self):
        for widget in self.main_frame.winfo_children():
            widget.grid_forget()

        tk.Label(
            self.main_frame,
            text="Score Prediction App",
            font=("Helvetica", 20, "bold"),
            bg="white",
        ).grid(row=0, column=0, pady=20)

        # Ana sayfa butonlarını tekrar göster
        for idx, (_, _, command) in enumerate(self.buttons):
            tk.Button(
                self.main_frame,
                text=self.buttons[idx][0],
                font=("Helvetica", 14),
                bg=self.buttons[idx][1],
                fg="white",
                width=20,
                command=command,
            ).grid(row=idx + 1, column=0, pady=10)

    def open_comparison_page(self):
        try:
            ComparisonApp(self.root)
        except Exception as e:
            messagebox.showerror("Hata", f"Oyuncu Karşılaştır sayfası açılamadı: {e}")

    def train_model(self):
        try:
            # Kullanıcıya hangi modeli eğitmek istediğini soralım
            model_types = {
                "Skor Tahmini": "score",
                "İkinci Yarı Tahmini": "second_half",
                "İlk 11 Tahmini": "first_eleven"
            }

            # Model seçim penceresi
            select_window = tk.Toplevel(self.root)
            select_window.title("Model Seçimi")
            select_window.geometry("300x200")

            selected_model = tk.StringVar(value="score")  # Varsayılan değer

            tk.Label(
                select_window,
                text="Eğitmek istediğiniz modeli seçin:",
                font=("Helvetica", 12)
            ).pack(pady=10)

            for text, value in model_types.items():
                tk.Radiobutton(
                    select_window,
                    text=text,
                    variable=selected_model,
                    value=value
                ).pack(pady=5)

            def start_training():
                model_type = selected_model.get()
                select_window.destroy()
                train_window = train_model_function(self.root, model_type=model_type)
                train_window.window.mainloop()
                messagebox.showinfo("Başarılı", f"{model_type} modeli başarıyla eğitildi!")

            tk.Button(
                select_window,
                text="Eğitimi Başlat",
                command=start_training,
                bg="#4caf50",
                fg="white"
            ).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Hata", f"Model eğitimi sırasında bir hata oluştu: {e}")

    def open_prediction_page(self):
        try:
            PredictModel(self.root)
        except Exception as e:
            messagebox.showerror("Hata", f"Tahmin sayfası açılamadı: {e}")

    def open_second_half_page(self):
        try:
            SecondHalfPrediction(self.root)
        except Exception as e:
            messagebox.showerror("Hata", f"İkinci Yarı Tahmin sayfası açılamadı: {e}")

    def open_squadcomp_page(self):
        try:
            FirstElevenComparison(self.root)
        except Exception as e:
            messagebox.showerror("Hata", f"Squad Karşılaştır sayfası açılamadı: {e}")

    def open_predict_page(self):
        try:
            ScorePrediction2(self.root)
        except Exception as e:
            messagebox.showerror("Hata", f"İlk 11 Tahmin sayfası açılamadı: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    app.set_background(r"assets/stad.jpg")
    root.mainloop()
