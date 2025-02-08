import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import pickle
import re
import subprocess
import win32api
import os
import webbrowser

class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Launcher")
        self.root.geometry("500x400")
        self.root.minsize(400, 300)

        self.games = []

        scrollbar = ttk.Scrollbar(root)
        self.game_treeview = ttk.Treeview(root, yscrollcommand=scrollbar.set, show="tree")
        scrollbar.configure(command=self.game_treeview.yview)

        scrollbar.pack(side="right", fill="y")
        self.game_treeview.pack(side="left", fill="both", expand=True)

        button_width = 15

        self.add_button = ttk.Button(root, text="Add Game", command=self.add_game, width=button_width)
        self.add_button.pack(padx=10, pady=5)

        self.remove_button = ttk.Button(root, text="Remove Game", command=self.remove_game, width=button_width)
        self.remove_button.pack(padx=10, pady=5)

        self.launch_button = ttk.Button(root, text="Launch Game", command=self.launch_game, width=button_width)
        self.launch_button.pack(pady=10)

        self.support_button = ttk.Button(root, text="Support", command=self.support_me, width=button_width)
        self.support_button.pack(pady=10)

        self.load_games()

    def support_me(self):
        url = "https://buymeacoffee.com/maxxdevs"

        webbrowser.open(url)

    def add_game(self):
        try:
            game_path = filedialog.askopenfilename(title="Select a game .exe file", filetypes=[("Executable files", "*.exe")])
            if game_path:
                if game_path not in self.games:
                    self.games.append(game_path)
                    self.update_game_treeview()
                else:
                    messagebox.showinfo("Game Already Added", "This game is already in the list.")

            self.save_games()
        except Exception as e:
            with open("error-logs.txt", "a") as log_file:
                log_file.write(f"Error: {str(e)}\n")

    def remove_game(self):
        try:
            selected_item = self.game_treeview.selection()
            if selected_item:
                try:
                    selected_index = int(self.game_treeview.index(selected_item))
                    del self.games[selected_index]
                    self.update_game_treeview()
                except ValueError as e:
                    pass
                    messagebox.showerror("Error", f"Something went wrong.\nPlease check the error logs and contact the developer.\n(Details in README.txt).")

            self.save_games()
        except Exception as e:
            with open("error-logs.txt", "a") as log_file:
                log_file.write(f"Error: {str(e)}\n")

    def launch_game(self):
        try:
            selected_item = self.game_treeview.selection()
            if selected_item:
                selected_index = self.game_treeview.index(selected_item)
                game_path = self.games[selected_index]
                subprocess.Popen(game_path)
        except Exception as e:
            with open("error-logs.txt", "a") as log_file:
                log_file.write(f"Error: {str(e)}\n")

    def update_game_treeview(self):
        self.game_treeview.delete(*self.game_treeview.get_children())
        for game in self.games:
            try:
                lang, codepage = win32api.GetFileVersionInfo(game, '\\VarFileInfo\\Translation')[0]
                gameDesc = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, "FileDescription")
                gameName = win32api.GetFileVersionInfo(game, gameDesc)
                if not gameName:
                    gameName = os.path.splitext(os.path.basename(game))[0]
                
                toRemove = ["_x64", "_x32", "x62", "x32", "Launcher"]
                pattern = "|".join(map(re.escape, toRemove))
                gameName = re.sub(pattern, "", gameName)
                self.game_treeview.insert("", "end", text=gameName.strip())

            except Exception as e:
                with open("error-logs.txt", "a") as log_file:
                    log_file.write(f"Error processing {game}: {str(e)}\n")

    @staticmethod
    def get_data_file(filename):
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, filename)
        return filename

    def load_games(self):
        try:
            with open(self.get_data_file("games.pkl"), "rb") as file:
                saved_games = pickle.load(file)
                self.games = [game for game in saved_games if os.path.exists(game)]
            self.update_game_treeview()
        except Exception as e:
            self.games = []
            with open("error-logs.txt", "a") as log_file:
                log_file.write(f"Error: {str(e)}\n")

    def save_games(self):
        try:
            existing_games = []
            for game in self.games:
                if os.path.exists(game):
                    existing_games.append(game)

            with open("games.pkl", "wb") as file:
                pickle.dump(existing_games, file)
        except Exception as e:
            with open("error-logs.txt", "a") as log_file:
                log_file.write(f"Error: {str(e)}\n")

if __name__ == "__main__":
    root = ThemedTk(theme='breeze')
    icon_image = tk.PhotoImage(file="icon.png")
    root.iconphoto(False, icon_image)
    app = GameLauncher(root)
    root.mainloop()