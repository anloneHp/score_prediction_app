import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import pandas as pd
import joblib
from bs4 import BeautifulSoup
import os

class ScorePrediction2:
    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        self.model_type = "first_eleven"  # Model tipini belirt
        self.model_file = f"{self.model_type}_trained_model.xgb"  # Model dosyasını belirt
        self.window.title("ilk 11 tahmini")
        self.window.geometry("800x600")

        # Takım HTML Dosyalarını Seçmek için Giriş
        self.team1_file = None
        self.team2_file = None

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
            text="Tahmin Yap",
            command=self.predict_score,
            bg="#4caf50",
            fg="white",
        ).grid(row=2, column=1, pady=20)

        self.result_label = tk.Label(self.window, text="", font=("Helvetica", 14), fg="#333")
        self.result_label.pack(pady=10)

    def browse_team1(self):
        filepath = filedialog.askopenfilename(
            title="Takım 1 HTML Dosyasını Seçin",
            filetypes=(("HTML Dosyaları", "*.html;*.htm"), ("Tüm Dosyalar", "*.*")),
        )
        if filepath:
            self.team1_entry.delete(0, tk.END)
            self.team1_entry.insert(0, filepath)
            self.team1_file = filepath

    def browse_team2(self):
        filepath = filedialog.askopenfilename(
            title="Takım 2 HTML Dosyasını Seçin",
            filetypes=(("HTML Dosyaları", "*.html;*.htm"), ("Tüm Dosyalar", "*.*")),
        )
        if filepath:
            self.team2_entry.delete(0, tk.END)
            self.team2_entry.insert(0, filepath)
            self.team2_file = filepath

    def predict_score(self):
        team1_path = self.team1_entry.get()
        team2_path = self.team2_entry.get()

        if not team1_path or not team2_path:
            messagebox.showwarning("Eksik Veri", "Lütfen her iki takım için de dosya seçin.")
            return

        try:
            # HTML dosyalarını oku ve verileri parse et
            team1_soup = self.read_html_to_soup(team1_path)
            team2_soup = self.read_html_to_soup(team2_path)

            team1_data = self.parse_team_data(team1_soup)
            team2_data = self.parse_team_data(team2_soup)

            # Kullanıcıdan oyuncu isimlerini al
            team1_names = simpledialog.askstring(
                "Takım 1 Oyuncuları", 
                "Lütfen Takım 1 için İlk 11 oyuncu isimlerini virgülle ayırarak girin:"
            )
            if not team1_names:
                return
            team1_names = team1_names.split(',')

            team2_names = simpledialog.askstring(
                "Takım 2 Oyuncuları", 
                "Lütfen Takım 2 için İlk 11 oyuncu isimlerini virgülle ayırarak girin:"
            )
            if not team2_names:
                return
            team2_names = team2_names.split(',')

            # Seçilen oyuncuları filtrele
            team1_selected = team1_data[team1_data['İsim'].isin(team1_names)]
            team2_selected = team2_data[team2_data['İsim'].isin(team2_names)]

            if len(team1_selected) == 0 or len(team2_selected) == 0:
                messagebox.showerror("Hata", "Girilen oyuncu isimleri bulunamadı!")
                return

            # Kategoriler
            categories = ["Hzl", "Güç", "Day", "Pas", "Agre", "Öns", 'Çev', 'Den', 'Ces', 'Hkm', 'Kons', 'Sğk', 'Ort',
                         'Kar', 'Krr', 'TSü', 'Bit', 'İKn', 'Yet', 'Elk', 'Kaf', 'Zıp', 'Ayk', 'Lid', 'Uzş', 'Mar',
                         'TzA', 'Hız', 'Poz', 'Ref', 'Day', 'Güç', 'Tkp', 'Toy', 'Tek', 'Taç', 'ANİ', 'Viz', 'Çlş']

            differences = {}
            for category in categories:
                team1_scores = pd.to_numeric(team1_selected[category], errors='coerce').dropna()
                team2_scores = pd.to_numeric(team2_selected[category], errors='coerce').dropna()
                differences[category] = (team1_scores.sum() - team2_scores.sum())

            differences_df = pd.DataFrame([differences])

            if not os.path.exists(self.model_file):
                messagebox.showerror("Model Bulunamadı", "Eğitilmiş bir model bulunamadı.")
                return

            model = joblib.load(self.model_file)
            predicted_diff = model.predict(differences_df)[0]

            # Olası skorları hesapla
            possible_scores = self.calculate_possible_scores(predicted_diff)

            # Sonuç penceresini oluştur
            result_window = tk.Toplevel(self.window)
            result_window.title("Tahmin Sonuçları")
            result_window.geometry("400x500")

            # Takım bilgilerini göster
            tk.Label(
                result_window,
                text=f"Takım 1: {os.path.basename(team1_path)}",
                font=("Helvetica", 10)
            ).pack(pady=5)

            tk.Label(
                result_window,
                text=f"Takım 2: {os.path.basename(team2_path)}",
                font=("Helvetica", 10)
            ).pack(pady=5)

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

            # Takım karşılaştırma detaylarını göster
            tk.Label(
                result_window,
                text="Önemli İstatistikler:",
                font=("Helvetica", 12, "bold")
            ).pack(pady=5)

            # En önemli farkları göster
            important_stats = sorted(differences.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
            for stat, diff in important_stats:
                tk.Label(
                    result_window,
                    text=f"{stat}: {diff:+.2f}",
                    font=("Helvetica", 10)
                ).pack(pady=2)

        except Exception as e:
            messagebox.showerror("Hata", f"Tahmin yapılırken bir hata oluştu: {e}")

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

    def read_html_to_soup(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        return soup

    def parse_team_data(self, soup):
        rows = soup.find_all('tr')
        columns = [col.get_text().strip() for col in rows[0].find_all('th')]
        data = [[cell.get_text().strip() for cell in row.find_all('td')] for row in rows[1:]]
        return pd.DataFrame(data, columns=columns)
