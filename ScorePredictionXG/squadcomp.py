import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from bs4 import BeautifulSoup
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import mean_squared_error

class FirstElevenComparison:
    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        self.model_type = "first_eleven"
        self.data_file = f"{self.model_type}_comparison_results.csv"
        self.model_file = f"{self.model_type}_trained_model.xgb"
        self.window.title("İlk 11 Karşılaştır")
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
            text="İlk 11 Seç ve Karşılaştır",
            command=self.compare_first_eleven,
            bg="#4caf50",
            fg="white",
        ).grid(row=2, column=0, pady=20)

        tk.Button(
            form_frame,
            text="Modeli Eğit",
            command=self.train_model,
            bg="#2196f3",
            fg="white",
        ).grid(row=2, column=1, pady=20)

        self.result_area = tk.Text(self.window, height=15, wrap=tk.WORD)
        self.result_area.pack(padx=10, pady=10, fill=tk.BOTH)

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

    def compare_first_eleven(self):
        try:
            if not self.team1_file or not self.team2_file:
                raise ValueError("Her iki takım dosyasını da seçmelisiniz!")

            # Takım verilerini yükle
            team1_data = self.parse_html(self.team1_file)
            team2_data = self.parse_html(self.team2_file)

            # Kullanıcıdan oyuncu isimlerini al
            team1_names = simpledialog.askstring(
                "Takım 1 Oyuncuları", "Lütfen Takım 1 için İlk 11 oyuncu isimlerini virgülle ayırarak girin:"
            ).split(',')
            team2_names = simpledialog.askstring(
                "Takım 2 Oyuncuları", "Lütfen Takım 2 için İlk 11 oyuncu isimlerini virgülle ayırarak girin:"
            ).split(',')

            # İlk 11'i seç
            team1_first_eleven = self.get_first_eleven(team1_data, team1_names)
            team2_first_eleven = self.get_first_eleven(team2_data, team2_names)

            # Kategorileri tanımla
            categories = ["Hzl", "Güç", "Day", "Pas","Agre","Öns",'Çev','Den','Ces','Hkm','Kons','Sğk','Ort','Kar','Krr','TSü','Bit','İKn','Yet','Elk','Kaf','Zıp','Ayk',
                         'Lid','Uzş','Mar','TzA','Hız','Poz','Ref','Day','Güç','Tkp','Toy','Tek','Taç','ANİ','Viz','Çlş'
                          ]

            # Özellik farklarını hesapla
            differences = self.calculate_team_differences(team1_first_eleven, team2_first_eleven, categories)

            # Sonuçları göster
            self.result_area.delete(1.0, tk.END)
            for category, diff in differences.items():
                self.result_area.insert(tk.END, f"{category}: {diff}\n")

            # Kullanıcıdan skor farkını al ve CSV'ye kaydet
            score_diff = float(simpledialog.askstring("Skor Farkı", "Lütfen maç skor farkını girin:"))
            differences["SkorFarki"] = score_diff
            self.save_to_csv(differences)

            messagebox.showinfo("Başarılı", "Karşılaştırma tamamlandı ve sonuçlar kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def parse_html(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        return self.parse_team_data(soup)

    def parse_team_data(self, soup):
        rows = soup.find_all('tr')
        columns = [col.get_text().strip() for col in rows[0].find_all('th')]
        data = [[cell.get_text().strip() for cell in row.find_all('td')] for row in rows[1:]]
        return pd.DataFrame(data, columns=columns)

    def get_first_eleven(self, df, names):
        selected_players = df[df['İsim'].isin(names)]
        if selected_players.empty:
            raise ValueError("Girdiğiniz isimler için oyuncular bulunamadı.")
        return selected_players

    def calculate_team_differences(self, team1_df, team2_df, categories):
        team1_totals = team1_df[categories].apply(pd.to_numeric, errors="coerce").sum()
        team2_totals = team2_df[categories].apply(pd.to_numeric, errors="coerce").sum()
        return (team1_totals - team2_totals).to_dict()

    def save_to_csv(self, data):
        df = pd.DataFrame([data])
        if os.path.exists(self.data_file):
            df.to_csv(self.data_file, mode="a", header=False, index=False)
        else:
            df.to_csv(self.data_file, index=False)

    def train_model(self):
        if not os.path.exists(self.data_file):
            messagebox.showwarning("Veri Eksik", "Modeli eğitmek için karşılaştırma sonuçlarına ihtiyacınız var.")
            return

        try:
            df = pd.read_csv(self.data_file)
            if "SkorFarki" not in df.columns:
                raise ValueError("Veri dosyasında SkorFarki sütunu bulunamadı.")

            X = df.drop("SkorFarki", axis=1)
            y = df["SkorFarki"]

            # Verileri böl
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Modeli oluştur ve eğit
            model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100, learning_rate=0.1)
            model.fit(X_train, y_train)

            # Modeli kaydet
            joblib.dump(model, self.model_file)

            # Performans değerlendirme
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = mse ** 0.5

            messagebox.showinfo("Model Eğitildi", f"Model başarıyla eğitildi.\nRMSE: {rmse:.2f}")
        except Exception as e:
            messagebox.showerror("Hata", f"Model eğitimi sırasında bir hata oluştu: {e}")
