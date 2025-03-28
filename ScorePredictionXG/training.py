import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from utils.file_utils import read_html_to_soup, parse_team_data
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import mean_squared_error
import joblib
import os

# Karşılaştırma verilerini saklamak için dosya adı
# data_file = "comparison_results.csv"

class train_model_function:
    def __init__(self, root, model_type="score"):
        self.root = root
        self.model_type = model_type
        self.data_file = f"{model_type}_comparison_results.csv"
        self.window = tk.Toplevel(root)
        self.window.title("Oyuncu Karşılaştır ve Model Eğit")
        self.window.geometry("800x600")

        # Form Alanı
        form_frame = tk.Frame(self.window, bg="white", padx=10, pady=10)
        form_frame.pack(padx=10, pady=10, fill=tk.BOTH)

        tk.Label(form_frame, text="Takım 1 Dosyasını Seçin:", bg="white").grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        self.team1_entry = tk.Entry(form_frame, width=50)
        self.team1_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(form_frame, text="Gözat", command=self.browse_team1).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(form_frame, text="Takım 2 Dosyasını Seçin:", bg="white").grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.team2_entry = tk.Entry(form_frame, width=50)
        self.team2_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(form_frame, text="Gözat", command=self.browse_team2).grid(row=1, column=2, padx=10, pady=10)

        tk.Button(
            form_frame,
            text="Karşılaştır",
            command=self.compare_teams,
            bg="#4caf50",
            fg="white",
        ).grid(row=2, column=1, padx=10, pady=20)

        self.result_area = scrolledtext.ScrolledText(self.window, width=80, height=15)
        self.result_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Model Eğitim ve Sıfırlama Butonları
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        tk.Button(
            button_frame,
            text="Modeli Eğit",
            command=self.train_model,
            bg="#2196f3",
            fg="white",
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame,
            text="Modeli Sıfırla",
            command=self.reset_model,
            bg="#f44336",
            fg="white",
        ).grid(row=0, column=1, padx=10)

    def browse_team1(self):
        filepath = filedialog.askopenfilename(
            title="Takım 1 HTML Dosyasını Seçin",
            filetypes=(("HTML Dosyaları", "*.html;*.htm"), ("Tüm Dosyalar", "*.*")),
        )
        if filepath:
            self.team1_entry.delete(0, tk.END)
            self.team1_entry.insert(0, filepath)

    def browse_team2(self):
        filepath = filedialog.askopenfilename(
            title="Takım 2 HTML Dosyasını Seçin",
            filetypes=(("HTML Dosyaları", "*.html;*.htm"), ("Tüm Dosyalar", "*.*")),
        )
        if filepath:
            self.team2_entry.delete(0, tk.END)
            self.team2_entry.insert(0, filepath)

    def compare_teams(self):
        team1_path = self.team1_entry.get()
        team2_path = self.team2_entry.get()

        if not team1_path or not team2_path:
            messagebox.showwarning("Giriş Eksik", "Lütfen her iki takım dosyasını da seçin.")
            return

        try:
            # HTML dosyalarını oku ve verileri parse et
            team1_soup = read_html_to_soup(team1_path)
            team2_soup = read_html_to_soup(team2_path)

            team1_data = parse_team_data(team1_soup)
            team2_data = parse_team_data(team2_soup)

            # Kategoriler
            categories = ["Hzl", "Güç", "Day", "Pas","Agre","Öns",'Çev','Den','Ces','Hkm','Kons','Sğk','Ort','Kar','Krr','TSü','Bit','İKn','Yet','Elk','Kaf','Zıp','Ayk',
                         'Lid','Uzş','Mar','TzA','Hız','Poz','Ref','Day','Güç','Tkp','Toy','Tek','Taç','ANİ','Viz','Çlş'
                          ]
            total_differences = self.calculate_total_team_differences(team1_data, team2_data, categories)

            # Sonuçları ekranda göster
            self.result_area.delete(1.0, tk.END)
            for category, total_diff in total_differences.items():
                self.result_area.insert(tk.END, f"{category} için toplam fark: {total_diff}\n")

            # Sonuçları CSV dosyasına kaydet
            self.save_comparison_results(total_differences)

        except Exception as e:
            messagebox.showerror("Hata", f"Hata oluştu: {e}")

    def calculate_total_team_differences(self, team1_df, team2_df, categories):
        total_differences = {}
        for category in categories:
            team1_scores = pd.to_numeric(team1_df[category], errors='coerce').dropna()
            team2_scores = pd.to_numeric(team2_df[category], errors='coerce').dropna()
            total_differences[category] = abs(team1_scores.sum() - team2_scores.sum())
        return total_differences

    def save_comparison_results(self, results):
     try:
        # Kullanıcıdan skor farkını iste
        score_diff = tk.simpledialog.askstring("Skor Farkı", "Lütfen bu karşılaştırma için maç skor farkını girin:")
        if not score_diff or not score_diff.isdigit():
            messagebox.showwarning("Eksik Veri", "Lütfen geçerli bir skor farkı girin.")
            return

        # Skor farkını sonuçlara ekle
        results["SkorFarki"] = float(score_diff)

        # DataFrame oluştur ve CSV'ye yaz
        df = pd.DataFrame([results])
        if os.path.exists(self.data_file):
            df.to_csv(self.data_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.data_file, index=False)

        messagebox.showinfo("Kaydedildi", "Karşılaştırma sonuçları kaydedildi.")
     except Exception as e:
        messagebox.showerror("Hata", f"Sonuçları kaydederken bir hata oluştu: {e}")

    def train_model(self):
     if not os.path.exists(self.data_file):
        messagebox.showwarning("Veri Eksik", "Modeli eğitmek için karşılaştırma sonuçlarına ihtiyacınız var.")
        return

     try:
        # CSV verisini oku ve doğrula
        df = pd.read_csv(self.data_file)
        if "SkorFarki" not in df.columns:
            messagebox.showerror("Eksik Veri", "Veri dosyasındaki SkorFarki sütunu eksik.")
            return

        X = df.drop("SkorFarki", axis=1)
        y = df["SkorFarki"]

        if X.empty or y.empty:
            messagebox.showerror("Veri Hatası", "Eğitim için yeterli veri bulunamadı.")
            return

        # Eğitim ve test verisine ayır
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Modeli oluştur ve eğit
        model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=1000, learning_rate=0.05)
        model.fit(X_train, y_train)

        # Modeli kaydet
        model_filename = f"{self.model_type}_trained_model.xgb"
        joblib.dump(model, model_filename)
        messagebox.showinfo("Eğitim Tamamlandı", "Model başarıyla eğitildi ve kaydedildi.")

        # Performans değerlendirme
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = mse ** 0.5
        messagebox.showinfo("Eğitim Tamamlandı", f"Model eğitildi. RMSE: {rmse}")


        # CSV dosyasını temizle
        with open(self.data_file, "w") as file:
            file.write("")  # Dosya içeriğini temizler

        messagebox.showinfo("Temizleme Tamamlandı", "Karşılaştırma sonuçları temizlendi ve model eğitildi.")

     except Exception as e:
        messagebox.showerror("Hata", f"Model eğitilirken bir hata oluştu: {e}")

    def reset_model(self):
     try:
        # Modeli sıfırlama işlemi, eski modeli silme
        model_filename = f"{self.model_type}_trained_model.xgb"
        if os.path.exists(model_filename):
            os.remove(model_filename)
            messagebox.showinfo("Model Sıfırlandı", "Model başarıyla sıfırlandı.")
        else:
            messagebox.showwarning("Model Bulunamadı", "Eğitilmiş bir model bulunamadı.")

        # CSV dosyasını sıfırlama işlemi
        csv_file = self.data_file
        if os.path.exists(csv_file):
            os.remove(csv_file)
            messagebox.showinfo("CSV Dosyası Silindi", "Karşılaştırma sonuçları CSV dosyası başarıyla silindi.")
        else:
            messagebox.showwarning("CSV Dosyası Bulunamadı", "Karşılaştırma sonuçları CSV dosyası bulunamadı.")

     except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {e}")
