import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from utils.file_utils import read_html_to_soup, parse_team_data
import pandas as pd

class ComparisonApp:
    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Oyuncu Karşılaştır")
        self.window.geometry("800x600")
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

        self.result_area = scrolledtext.ScrolledText(self.window, width=80, height=20)
        self.result_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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
            team1_soup = read_html_to_soup(team1_path)
            team2_soup = read_html_to_soup(team2_path)

            team1_diff = parse_team_data(team1_soup)
            team2_diff= parse_team_data(team2_soup)

            categories = ["Hzl", "Güç", "Day", "Pas","Agre","Öns",'Çev','Den','Ces','Hkm','Kons','Sğk','Ort','Kar','Krr','TSü','Bit','İKn','Yet','Elk','Kaf','Zıp','Ayk',
                         'Lid','Uzş','Mar','TzA','Hız','Poz','Ref','Day','Güç','Tkp','Toy','Tek','Taç','ANİ','Viz','Çlş'
                          ]
            total_differences = self.calculate_total_team_differences(team1_diff, team2_diff, categories)

            self.result_area.delete(1.0, tk.END)
            for category, total_diff in total_differences.items():
                self.result_area.insert(tk.END, f"{category} için toplam fark: {total_diff}\n")
        except Exception as e:
            messagebox.showerror("Hata", f"Hata oluştu: {e}")

    def calculate_total_team_differences(self, team1, team2, categories):
        total_differences = {}
        for category in categories:
            team1_scores = pd.to_numeric(team1[category], errors='coerce').dropna()
            team2_scores = pd.to_numeric(team2[category], errors='coerce').dropna()
            total_differences[category] = (team1_scores.sum() - team2_scores.sum())
        return total_differences
