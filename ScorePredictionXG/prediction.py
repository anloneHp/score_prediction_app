import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import joblib
import os
import traceback  # Hata ayıklama için

class PredictModel:
    def __init__(self, root):
        self.root = root
        self.model_type = "score"
        self.model_file = f"{self.model_type}_trained_model.xgb"
        self.window = tk.Toplevel(root)
        self.window.title("Skor Tahmini")
        self.window.geometry("600x400")

        # Form Alanı
        form_frame = tk.Frame(self.window, padx=10, pady=10)
        form_frame.pack(padx=10, pady=10, fill=tk.BOTH)

        tk.Label(form_frame, text="Takım 1 Dosyasını Seçin:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.team1_entry = tk.Entry(form_frame, width=50)
        self.team1_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(form_frame, text="Gözat", command=self.browse_team1).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(form_frame, text="Takım 2 Dosyasını Seçin:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.team2_entry = tk.Entry(form_frame, width=50)
        self.team2_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(form_frame, text="Gözat", command=self.browse_team2).grid(row=1, column=2, padx=10, pady=10)

        tk.Button(
            form_frame,
            text="Skoru Tahmin Et",
            command=self.predict_score,
            bg="#4caf50",
            fg="white",
        ).grid(row=2, column=1, padx=10, pady=20)

        # Sonuç Alanı
        self.result_label = tk.Label(self.window, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

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

    def predict_score(self):
         team1_path = self.team1_entry.get()
         team2_path = self.team2_entry.get()

         if not team1_path or not team2_path:
            messagebox.showwarning("Giriş Eksik", "Lütfen her iki takım dosyasını da seçin.")
            return

         try:
            # HTML dosyalarını oku ve parse et
            from utils.file_utils import read_html_to_soup, parse_team_data

            team1_soup = read_html_to_soup(team1_path)
            team2_soup = read_html_to_soup(team2_path)

            team1_data = parse_team_data(team1_soup)
            team2_data = parse_team_data(team2_soup)

            # Kategorilere göre farkları hesapla
            categories = [
                "Hzl", "Güç", "Day", "Pas", "Agre", "Öns", "Çev", "Den", "Ces", "Hkm", 
                "Kons", "Sğk", "Ort", "Kar", "Krr", "TSü", "Bit", "İKn", "Yet", "Elk", 
                "Kaf", "Zıp", "Ayk", "Lid", "Uzş", "Mar", "TzA", "Hız", "Poz", "Ref", 
                "Day", "Güç", "Tkp", "Toy", "Tek", "Taç", "ANİ", "Viz", "Çlş"
            ]

            # Sadece seçilen kategorilerde işlem yap
            differences = {}
            for category in categories:
                if category in team1_data.columns and category in team2_data.columns:
                    # Fark hesaplama
                    team1_sum = pd.to_numeric(team1_data[category], errors="coerce").sum()
                    team2_sum = pd.to_numeric(team2_data[category], errors="coerce").sum()
                    differences[category] = abs(team1_sum - team2_sum)

            if not differences:
                messagebox.showerror("Hata", "Seçilen kategorilere uygun veri bulunamadı.")
                return

            differences_df = pd.DataFrame([differences])

            # Modeli yükle ve tahmin yap
            if not os.path.exists(self.model_file):
                messagebox.showerror("Model Bulunamadı", "Eğitilmiş bir model bulunamadı.")
                return

            model = joblib.load(self.model_file)
            predicted_score_diff = model.predict(differences_df)[0]

            # Tahmini skora dönüştür
            possible_scores = self.generate_possible_scores(predicted_score_diff)

            # Tahmini sonuçları göster
            self.result_label.config(
                text=f"Tahmini Skor Farkı: {predicted_score_diff:.2f}\n"
                     f"Muhtemel Skorlar: {', '.join(possible_scores)}"
            )

         except Exception as e:
            traceback.print_exc()  # Konsolda hata detaylarını göster
            messagebox.showerror("Hata", f"Hata oluştu: {e}")

    def generate_possible_scores(self, score_diff):
        """
        Tahmin edilen skor farkına göre muhtemel skor kombinasyonlarını döndürür.
        """
        possible_scores = []
        max_score = 5  # Maksimum skor sınırı
        for team1_score in range(max_score + 1):
            for team2_score in range(max_score + 1):
                if abs(team1_score - team2_score) == round(score_diff):
                    possible_scores.append(f"{team1_score}-{team2_score}")
        return possible_scores