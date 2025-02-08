from langchain_cohere import ChatCohere
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from dotenv import load_dotenv, set_key
from idlelib.tooltip import Hovertip
import subprocess
import threading
import win32api
import webbrowser
from datetime import datetime
import pickle
import sys
import json
import re
import os

load_dotenv()

def get_file_description(file_path):
    """
    Gets the description of a given .exe file.

    Args:
        file_path (str): The path to the .exe file.

    Returns:
        str: The description of the given .exe file, or "No description available" if not found.
    """
    try:
        info = win32api.GetFileVersionInfo(file_path, "\\StringFileInfo\\040904b0\\FileDescription")
        return info if info else "No description available"
    except:
        return "No description available"

def getStandalone(root_path):
    """
    Scans the given root directory and its subdirectories for .exe files and extracts descriptions.

    Args:
        root_path (str): The path to the root directory to scan.

    Returns:
        dict: A dictionary where the keys are the paths of the directories containing .exe files and the values are dictionaries mapping the .exe names to their descriptions.
    """
    exe_map = {}

    for dirpath, _, filenames in os.walk(root_path):
        exes = {file: get_file_description(os.path.join(dirpath, file))
                for file in filenames if file.endswith('.exe') and not file.startswith('unin')}
        if exes:
            exe_map[dirpath] = exes

    return exe_map

def getGameStandalonesFromLLM(exe_data):
    """
    Extracts game standalones from the given data using the specified LLM.

    The LLM is given a JSON string of the following format:
    {
        "path1": {
            "exe1": "exe1 description",
            "exe2": "exe2 description",
            ...
        },
        "path2": {
            ...
        },
        ...
    }

    The LLM should return a JSON string of the following format:
    [
        {"name": "Game1 Name", "path": "Game1 Standalone Path"},
        {"name": "Game2 Name", "path": "Game2 Standalone Path"}
    ]

    If a game has a launcher then only add the launcher.

    Args:
        exe_data (dict): The data to extract game standalones from.

    Returns:
        list: A list of extracted game standalones, or an empty list if an error occurred.
    """
    llm_choice = os.getenv("LLM_CHOICE", "Cohere")
    api_key = os.getenv("COHERE_API_KEY") if llm_choice == "Cohere" else os.getenv("OPENAI_API_KEY")

    if not api_key:
        messagebox.showerror("Error", f"No API key found for {llm_choice}. Please configure it in settings.")
        return []

    try:
        if llm_choice == "Cohere":
            llm = ChatCohere(model="command-r-plus", temperature=0, max_retries=1)
        else:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        system_message = SystemMessage(content="""
            Extract game standalones from the given data.
            If a game has a launcher then only add the launcher.
            The final response format should be:
            [
                {"name": "Game1 Name", "path": "Game1 Standalone Path"},
                {"name": "Game2 Name", "path": "Game2 Standalone Path"}
            ]
            """)

        human_message = HumanMessage(content=json.dumps(exe_data, indent=4, ensure_ascii=False))
        response = llm.invoke([system_message, human_message])

        return json.loads(response.content.replace("```", "").replace(".json", "").replace("json", ""))

    except Exception as e:
        messagebox.showerror("Error", f"LLM request failed. Check API key and internet connection.\n{str(e)}")
        log_error(str(e))
        return []

def log_error(error_message):
    """Append an error message to a log file.
    
    The log file is in the same directory as the script and is named "error-logs.txt". Each entry is
    timestamped and includes the error message. The purpose of this function is to log errors that
    occur when the script is run, so that they can be reported to the developer.
    
    Parameters
    ----------
    error_message : str
        The error message to be logged.
    """
    with open("error-logs.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] - Error: {error_message}\n")

def log_launch_error(game, error_message):
    """Append an error message to a log file for a specific game.
    
    The log file is in the same directory as the script and is named "error-logs.txt". Each entry is
    timestamped and includes the game name and error message. The purpose of this function is to log
    errors that occur when a game is being processed, so that they can be reported to the developer.
    
    Parameters
    ----------
    game : str
        The name of the game that caused the error.
    error_message : str
        The error message to be logged.
    """
    with open("error-logs.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] - Error processing {game}: {error_message}\n")


class GameLauncher:
    def __init__(self, root):
        """
        Initialize the Game Launcher object.

        Parameters
        ----------
        root : tkinter.Tk
            The root window of the application.

        Attributes
        ----------
        root : tkinter.Tk
            The root window of the application.
        games : set
            Set of game paths.
        llm_choice : str
            The preferred language model to use.
        menubar : tkinter.Menu
            The menu bar of the application.
        scrollbar : ttk.Scrollbar
            The scrollbar of the game treeview.
        game_treeview : ttk.Treeview
            The treeview of games.
        add_button : ttk.Button
            The button to add a game.
        detect_button : ttk.Button
            The button to detect games using AI.
        remove_button : ttk.Button
            The button to remove a game.
        launch_button : ttk.Button
            The button to launch a game.
        """
        self.root = root
        self.root.title("Game Launcher")
        self.root.geometry("500x400")
        self.root.minsize(500, 400)

        self.games = set()
        self.llm_choice = os.getenv("LLM_CHOICE", "Cohere")

        menubar = tk.Menu(root)
        settings_option = tk.Menu(menubar, tearoff=0)
        menubar.add_command(label="Settings", command=self.open_settings)
        menubar.add_command(label="Help", command=self.open_help)
        menubar.add_command(label="Report an Issue", command=lambda: webbrowser.open("https://github.com/pratham-jaiswal/game-launcher-app/issues"))
        menubar.add_command(label="Support Me", command=lambda: webbrowser.open("https://buymeacoffee.com/maxxdevs"))
        root.config(menu=menubar)

        scrollbar = ttk.Scrollbar(root)
        self.game_treeview = ttk.Treeview(root, yscrollcommand=scrollbar.set, show="tree", selectmode="browse")
        scrollbar.configure(command=self.game_treeview.yview)

        scrollbar.pack(side="right", fill="y")
        self.game_treeview.pack(side="left", fill="both", expand=True)

        button_width = 20

        self.add_button = ttk.Button(root, text="Add Game", command=self.add_game, width=button_width)
        self.add_button.pack(padx=10, pady=5)

        self.detect_button = ttk.Button(root, text="Detect Games (AI)", command=self.detect_games, width=button_width)
        self.detect_button.pack(padx=10, pady=5)
        
        self.check_api_key()

        self.remove_button = ttk.Button(root, text="Remove Game", command=self.remove_game, width=button_width)
        self.remove_button.pack(padx=10, pady=5)

        self.launch_button = ttk.Button(root, text="Launch Game", command=self.launch_game, width=button_width)
        self.launch_button.pack(pady=10)

        self.load_games()

    def open_settings(self):
        """
        Opens the settings window for the user to configure their API keys and preferred LLM.

        The settings window is a separate window that allows the user to input their API keys and select which LLM to use.
        The window is displayed whenever the user clicks the "Settings" button in the menu bar.

        The window contains the following fields:
        - Cohere API Key: A text field where the user can enter their Cohere API key.
        - OpenAI API Key: A text field where the user can enter their OpenAI API key.
        - Select LLM: A dropdown menu where the user can select which LLM to use (Cohere or OpenAI).

        Once the user has filled in the fields, they can click the "Save" button to save their settings and close the window.
        If the user clicks the "Cancel" button, the window will close without saving any changes.
        """
        load_dotenv(override=True)
        
        settings_window = tk.Toplevel(self.root)
        icon_image = tk.PhotoImage(file="icon.png")
        settings_window.iconphoto(False, icon_image)
        
        settings_window.title("Settings")
        settings_window.geometry("350x250")
        settings_window.minsize(350, 300)

        tk.Label(settings_window, text="Cohere API Key:").pack()
        cohere_key = tk.Entry(settings_window)
        cohere_key.insert(0, os.getenv("COHERE_API_KEY", ""))
        cohere_key.pack()

        cohere_link = ttk.Button(settings_window, text="Get Cohere API Key", command=lambda: webbrowser.open("https://dashboard.cohere.com/api-keys"))
        cohere_link.pack(pady=5)

        tk.Label(settings_window, text="OpenAI API Key:").pack()
        openai_key = tk.Entry(settings_window, show="*")
        openai_key.insert(0, os.getenv("OPENAI_API_KEY", ""))
        openai_key.pack()

        openai_link = ttk.Button(settings_window, text="Get OpenAI API Key", command=lambda: webbrowser.open("https://platform.openai.com/api-keys"))
        openai_link.pack(pady=5)

        tk.Label(settings_window, text="Select LLM:").pack()
        llm_choice = ttk.Combobox(settings_window, values=["Cohere", "OpenAI"])
        llm_choice.set(self.llm_choice)
        llm_choice.pack()

        def save_settings():            
            """
            Saves the settings to the .env file and updates the LLM choice for the Game Launcher.

            Notes
            -----
            This function is called when the user clicks the "Save" button in the settings window.
            It saves the user's input (API keys and LLM choice) to the .env file and updates the LLM choice for the Game Launcher.
            After saving the settings, it closes the settings window.
            """
            set_key(".env", "COHERE_API_KEY", cohere_key.get())
            set_key(".env", "OPENAI_API_KEY", openai_key.get())
            set_key(".env", "LLM_CHOICE", llm_choice.get())

            self.llm_choice = llm_choice.get()

            self.check_api_key()
            settings_window.destroy()

        save_button = ttk.Button(settings_window, text="Save", command=save_settings)
        save_button.pack(pady=10)
        self.check_api_key()

    def open_help(self):
        """
        Opens a help window containing a guide on how to use the Game Launcher and some troubleshooting tips.

        Notes
        -----
        This function is called when the user clicks the "Help" button in the menu.
        It creates a new window with a text box containing the help guide and a close button.
        The close button closes the help window.
        """
        help_window = tk.Toplevel(self.root)
        icon_image = tk.PhotoImage(file="icon.png")
        help_window.iconphoto(False, icon_image)

        help_window.title("Help")
        help_window.geometry("500x400")
        help_window.minsize(500, 400)

        frame = ttk.Frame(help_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        help_text = """Game Launcher Help Guide

        How to Use:
        - Add Game: Click 'Add Game' and select a .exe file.
        - Detect Games: Click 'Detect Games' and choose a folder.
        - Remove Game: Select a game and click 'Remove Game'.
        - Launch Game: Select a game and click 'Launch Game'.
        - Settings: Configure API keys and AI model.

        Troubleshooting:
        - Check 'error-logs.txt' if an error occurs.
        - Ensure the game file exists before launching.
        - If AI detection fails, verify your API keys.

        Support:
        - Report bugs: Visit the GitHub Issues page.
        - Support the developer: Check out the support link in the menu.
        """

        text_widget = tk.Text(frame, wrap="word", height=20, width=60, font=("Arial", 10))
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled", yscrollcommand=scrollbar.set)
        text_widget.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=text_widget.yview)

        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)

    def check_api_key(self):
        """
        Checks the availability of the API key based on the selected LLM and updates the state of the detect button.

        This function loads the environment variables and verifies if an API key (Cohere or OpenAI) is set
        according to the user's selected LLM. If no API key is found, the detect button is disabled and a tooltip
        is added to inform the user. If an API key is available, the detect button is enabled.

        Attributes
        ----------
        detect_button : ttk.Button
            The button for detecting games, which is enabled or disabled based on API key availability.
        detect_button_tip : Hovertip, optional
            A tooltip that displays a message when the detect button is disabled due to missing API key.
        """

        load_dotenv(override=True)
        api_key = os.getenv("COHERE_API_KEY") if self.llm_choice == "Cohere" else os.getenv("OPENAI_API_KEY")

        if not api_key:
            self.detect_button.config(state="disabled")
            self.detect_button_tip = Hovertip(self.detect_button, "Add an OpenAI or Cohere API key in Settings to enable game detection.")
        else:
            self.detect_button.config(state="normal")
            if hasattr(self, 'detect_button_tip'):
                self.detect_button_tip.hidetip()

    def show_loading_popup(self):
        """
        Displays a loading popup window to indicate that game detection is in progress.

        This function creates a modal popup window with a "Detecting Games" message. 
        It disables interaction with certain buttons in the main application window 
        to prevent user actions during the game detection process.

        Attributes
        ----------
        loading_popup : tk.Toplevel
            A top-level window that displays the loading message.

        Notes
        -----
        The popup is non-resizable and transient, ensuring focus remains on the popup 
        until it is closed.
        """

        self.loading_popup = tk.Toplevel(self.root)
        self.loading_popup.title("Detecting Games")
        self.loading_popup.geometry("250x100")
        self.loading_popup.resizable(False, False)
        self.loading_popup.transient(self.root)
        self.loading_popup.grab_set()

        tk.Label(self.loading_popup, text="Detecting games...", font=("Arial", 12)).pack(pady=10)

        self.add_button.config(state="disabled")
        self.detect_button.config(state="disabled")
        self.remove_button.config(state="disabled")
        self.launch_button.config(state="disabled")
        self.support_button.config(state="disabled")

        self.root.update_idletasks()

    def hide_loading_popup(self):
        """
        Hides the loading popup window and re-enables all buttons.

        Attributes
        ----------
        loading_popup : tk.Toplevel
            A top-level window that displays the loading message.

        Notes
        -----
        This function is called when the loading popup needs to be closed.
        It destroys the popup window and re-enables interaction with the buttons.
        """
        if hasattr(self, 'loading_popup') and self.loading_popup:
            self.loading_popup.destroy()

        self.add_button.config(state="normal")
        self.detect_button.config(state="normal")
        self.remove_button.config(state="normal")
        self.launch_button.config(state="normal")
        self.support_button.config(state="normal")

    def add_game(self):
        """
        Prompts the user to select a game executable file and adds it to the game list if not already added.

        This function opens a file dialog for the user to select a `.exe` file. It normalizes the
        selected file path and checks if it is already in the game list. If not, it adds the path,
        updates the game treeview, and saves the game list. If the game is already added, it shows
        an informational message to the user. Handles exceptions by displaying an error message
        and logging the error.

        Exceptions
        ----------
        Exception
            If an error occurs during file selection or processing, an error message is displayed
            and the error is logged.
        """

        try:
            game_path = filedialog.askopenfilename(title="Select a game .exe file", filetypes=[("Executable files", "*.exe")])
            normalized_path = os.path.normpath(game_path)

            if normalized_path and normalized_path not in self.games:
                self.games.append(normalized_path)
                self.update_game_treeview()
                self.save_games()
            elif normalized_path in self.games:
                messagebox.showinfo("Game Already Added", "This game is already in the list.")
        except Exception as e:
            messagebox.showerror("Error", "Something went wrong.\nCheck the error logs.")
            log_error(str(e))

    def detect_games(self): 
        """
        Uses AI to detect games in a selected folder and adds them to the game list if not already added.

        This function asks the user to select a folder to detect games in. It uses the `getStandalone`
        function to process all `.exe` files in the selected folder and its subfolders, and then passes
        the processed data to `getGameStandalonesFromLLM` to detect games. The detected games are then
        added to the game list if not already added, and the game treeview is updated. Handles exceptions
        by displaying an error message and logging the error.

        Exceptions
        ----------
        Exception
            If an error occurs during folder selection or processing, an error message is displayed
            and the error is logged.
        """
        def detection_process():
            try:
                folder_selected = filedialog.askdirectory(title="Select a folder to detect games in")
                if folder_selected:
                    self.show_loading_popup()
                    exe_data = getStandalone(folder_selected)
                    detected_games = getGameStandalonesFromLLM(exe_data)
                    
                    for game in detected_games:
                        normalized_path = os.path.normpath(game['path'])
                        
                        if normalized_path not in self.games:
                            self.games.append(normalized_path)

                    self.update_game_treeview()
                    self.save_games()
                    self.hide_loading_popup()
            except Exception as e:
                self.hide_loading_popup()
                messagebox.showerror("Error", "Something went wrong.\nCheck the error logs.")
                log_error(str(e))
        
        threading.Thread(target=detection_process, daemon=True).start()

    def remove_game(self):
        """
        Removes the selected game from the game list and updates the game treeview.

        This function retrieves the currently selected item in the game treeview,
        deletes it from the game list if valid, and updates the display. If an error
        occurs during the removal process, it shows an error message to the user and
        logs the error. After a successful removal, the updated game list is saved.

        Exceptions
        ----------
        ValueError
            If an invalid index is encountered, an error message is displayed and
            the error is logged.
        """

        selected_item = self.game_treeview.selection()
        if selected_item:
            try:
                selected_index = int(self.game_treeview.index(selected_item))
                del self.games[selected_index]
                self.update_game_treeview()
            except ValueError as e:
                messagebox.showerror("Error", f"Something went wrong.\nPlease check the error logs and contact the developer.\n(Details in README.txt).")
                log_error(str(e))
        self.save_games()

    def launch_game(self):
        """
        Launches the selected game in the game treeview.

        This function retrieves the currently selected item in the game treeview,
        launches the associated game executable if valid, and handles any errors
        that may occur during the launching process. If an error occurs, it shows
        an error message to the user and logs the error.

        Exceptions
        ----------
        Exception
            If an error occurs during game launching, an error message is displayed
            and the error is logged.
        """
        try:
            selected_item = self.game_treeview.selection()
            if selected_item:
                selected_index = self.game_treeview.index(selected_item)
                game_path = self.games[selected_index]
                subprocess.Popen(game_path)
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong.\nPlease check the error logs and contact the developer.\n(Details in README.txt).")
            log_error(str(e))

    def update_game_treeview(self):
        """
        Updates the game treeview with the current list of games.

        This function clears the current items in the game treeview and
        repopulates it with the current list of games. For each game, it
        retrieves the game name from its executable file and inserts it
        into the game treeview. If an error occurs during the retrieval
        process, an error message is displayed to the user and the error
        is logged.

        Exceptions
        ----------
        Exception
            If an error occurs during game name retrieval, an error message
            is displayed to the user and the error is logged.
        """
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
                messagebox.showerror("Error", f"Something went wrong.\nPlease check the error logs and contact the developer.\n(Details in README.txt).")
                log_launch_error(game, str(e))

    @staticmethod
    def get_data_file(filename):
        """
        Retrieves the path to a data file, accommodating both development and
        PyInstaller environments.

        This function checks if the script is running in a PyInstaller bundled
        environment by examining the 'sys.frozen' attribute. If true, it constructs
        the file path using the temporary directory (_MEIPASS) created by PyInstaller.
        Otherwise, it returns the filename as is.

        Args:
            filename (str): The name of the file whose path is to be retrieved.

        Returns:
            str: The resolved file path, either within the PyInstaller directory or
            the original filename.
        """

        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, filename)
        return filename

    def load_games(self):
        """
        Loads the saved games from the 'games.pkl' file and updates the game treeview.

        This function attempts to load the saved games from the 'games.pkl' file and
        filters out any games that no longer exist. If successful, it updates the
        game treeview with the loaded games. If an error occurs during loading, it
        shows an error message, logs the error, and resets the game list to empty.
        """
        try:
            with open(self.get_data_file("games.pkl"), "rb") as file:
                saved_games = pickle.load(file)
                self.games = [game for game in saved_games if os.path.exists(game)]

            self.update_game_treeview()
        except Exception as e:
            self.games = []
            messagebox.showerror("Error", f"Something went wrong.\nPlease check the error logs and contact the developer.\n(Details in README.txt).")
            log_error(str(e))

    def save_games(self):
        """
        Saves the current list of games to the 'games.pkl' file.

        This function attempts to save the current list of games to the 'games.pkl'
        file. It filters out any games that no longer exist before saving. If an
        error occurs during saving, it shows an error message and logs the error.

        Exceptions
        ----------
        Exception
            If an error occurs during saving, an error message is displayed and
            the error is logged.
        """
        
        try:
            existing_games = []
            for game in self.games:
                if os.path.exists(game):
                    existing_games.append(game)

            with open("games.pkl", "wb") as file:
                pickle.dump(existing_games, file)
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong.\nPlease check the error logs and contact the developer.\n(Details in README.txt).")
            log_error(str(e))

if __name__ == "__main__":
    root = ThemedTk(theme='breeze')
    icon_image = tk.PhotoImage(file="icon.png")
    root.iconphoto(False, icon_image)
    app = GameLauncher(root)
    root.mainloop()