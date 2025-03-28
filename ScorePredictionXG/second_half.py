import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
import joblib
import xgboost as xgb

class SecondHalfPrediction:
    def __init__(self, root):
        self.root = root
        self.model_type = "second_half"
        self.model_file = f"{self.model_type}_trained_model.xgb"
        self.window = tk.Toplevel(root)
        self.window.title("İkinci Yarı Skor Tahmini")
        self.window.geometry("600x500")
        
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.window, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Veri Kaydetme Alanları
        tk.Label(frame, text="Takım 1 İlk Yarı xG:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.team1_xg_entry = tk.Entry(frame, width=20)
        self.team1_xg_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Takım 2 İlk Yarı xG:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.team2_xg_entry = tk.Entry(frame, width=20)
        self.team2_xg_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Maç Sonucu (Örn: 3-2):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.match_result_entry = tk.Entry(frame, width=20)
        self.match_result_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(frame, text="Veriyi Kaydet", command=self.save_data, bg="#4caf50", fg="white").grid(row=3, column=1, pady=10)

        # Model Eğitme ve Tahmin Yapma Alanı
        tk.Button(frame, text="Modeli Eğit", command=self.train_model, bg="#2196f3", fg="white").grid(row=4, column=1, pady=10)
        tk.Button(frame, text="Tahmin Yap", command=self.predict_score, bg="#4caf50", fg="white").grid(row=5, column=1, pady=10)

        # Sıfırlama Butonu
        tk.Button(frame, text="Sıfırla", command=self.reset_data, bg="#f44336", fg="white").grid(row=6, column=1, pady=10)

        self.result_label = tk.Label(frame, text="", font=("Arial", 14))
        self.result_label.grid(row=7, column=0, columnspan=2, pady=10)

    def save_data(self):
        # Kullanıcı verilerini kaydetme
        team1_xg = self.team1_xg_entry.get()
        team2_xg = self.team2_xg_entry.get()
        match_result = self.match_result_entry.get()

        if not (team1_xg and team2_xg and match_result):
            messagebox.showwarning("Eksik Veri", "Lütfen tüm alanları doldurun.")
            return

        data = {"Team1_xG": [float(team1_xg)], "Team2_xG": [float(team2_xg)], "Result": [match_result]}
        df = pd.DataFrame(data)

        # CSV'ye ekle
        file_exists = os.path.exists("match_data.csv")
        with open("match_data.csv", "a") as f:
            df.to_csv(f, header=not file_exists, index=False)

        messagebox.showinfo("Başarılı", "Veri kaydedildi!")

    def train_model(self):
        # Modeli eğitme
        if not os.path.exists("match_data.csv"):
            messagebox.showwarning("Veri Bulunamadı", "Önce veri ekleyin.")
            return

        df = pd.read_csv("match_data.csv")

        # Sonuç kolonunu ayır ve hedefe dönüştür
        df["Result"] = df["Result"].apply(lambda x: int(x.split("-")[0]) - int(x.split("-")[1]))

        X = df[["Team1_xG", "Team2_xG"]]
        y = df["Result"]

        model = xgb.XGBRegressor()
        model.fit(X, y)

        joblib.dump(model, self.model_file)
        messagebox.showinfo("Başarılı", "Model eğitildi!")

    def predict_score(self):
        team1_xg = self.team1_xg_entry.get()
        team2_xg = self.team2_xg_entry.get()

        if not team1_xg or not team2_xg:
            messagebox.showwarning("Eksik Veri", "Lütfen tüm alanları doldurun.")
            return

        if not os.path.exists(self.model_file):
            messagebox.showerror("Model Bulunamadı", "Model eğitilmedi.")
            return

        model = joblib.load(self.model_file)
        input_data = pd.DataFrame({"Team1_xG": [float(team1_xg)], "Team2_xG": [float(team2_xg)]})
        predicted_diff = model.predict(input_data)[0]

        # Olası skorları hesapla
        possible_scores = self.calculate_possible_scores(predicted_diff)
        
        # Sonuç penceresini oluştur
        result_window = tk.Toplevel(self.window)
        result_window.title("Tahmin Sonuçları")
        result_window.geometry("400x300")
        
        # Tahmin edilen skor farkını göster
        tk.Label(
            result_window,
            text=f"Tahmin Edilen Skor Farkı: {predicted_diff:.2f}",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)
        
        # Olası skorları listele
        tk.Label(
            result_window,
            text="Olası Skorlar:",
            font=("Helvetica", 12, "bold")
        ).pack(pady=5)
        
        # Scrollable frame for possible scores
        score_frame = tk.Frame(result_window)
        score_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(score_frame)
        scrollbar = tk.Scrollbar(score_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Olası skorları göster
        for score, probability in possible_scores:
            score_text = f"{score[0]} - {score[1]} (Olasılık: {probability:.2f}%)"
            tk.Label(
                scrollable_frame,
                text=score_text,
                font=("Helvetica", 10)
            ).pack(pady=2)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    def calculate_possible_scores(self, predicted_diff):
        # Skor farkına göre olası skorları hesapla
        possible_scores = []
        max_goals = 5  # Maksimum gol sayısı
        
        # Tahmin edilen farka en yakın skorları bul
        for team1_score in range(max_goals + 1):
            for team2_score in range(max_goals + 1):
                score_diff = team1_score - team2_score
                diff_distance = abs(score_diff - predicted_diff)
                
                # Olasılığı hesapla (farka olan uzaklığa göre)
                probability = 100 * (1 / (1 + diff_distance))
                
                if probability > 10:  # Sadece %10'dan yüksek olasılıklı skorları göster
                    possible_scores.append(((team1_score, team2_score), probability))
        
        # Olasılığa göre sırala
        possible_scores.sort(key=lambda x: x[1], reverse=True)
        return possible_scores[:10]  # En olası 10 skoru döndür

    def reset_data(self):
        # CSV dosyasını silme ve modeli sıfırlama
        if os.path.exists("match_data.csv"):
            os.remove("match_data.csv")
        
        if os.path.exists(self.model_file):
            os.remove(self.model_file)

        self.team1_xg_entry.delete(0, tk.END)
        self.team2_xg_entry.delete(0, tk.END)
        self.match_result_entry.delete(0, tk.END)
        self.result_label.config(text="")

        messagebox.showinfo("Başarılı", "Veriler ve model sıfırlandı!")
