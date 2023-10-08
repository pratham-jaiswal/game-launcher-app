# Game Launcher
Welcome to the Game Launcher app! It allows you to add, remove, and launch games with ease. The application is designed to simplify the process of accessing your games directly from one place. It is converted into a [standalone executable file](https://.com/pratham-jaiswal/game-launcher-app/releases/tag/Latest) for ease of use and distribution.

## Use Case
- Lets users organize and manage their collection of PC games.
- Quickly launch my favorite games without navigating through folders.
- Quickly access and test different game versions and builds.

## Features
- Add games to the launcher by selecting their executable files.
- Remove unwanted games from the list.
- Launch games quickly.
- Games that are uninstalled, deleted, or moved to another directory will automatically be removed from the launcher.

> **Note:**
> - Deleting the *games.pkl* would remove all the games from the launcher.
> - Deleting the *gamelauncher circle.png* would result in crashing of the launcher. Fix:
>   - Copy and paste the *games.pkl* file somewhere safe.
>   - Re-install the *Game Launcher* app.
>   - Now move the copied *games.pkl* in the installed directory.

## Installing and Using the App
> ***Note: This is a windows only application***
- Download the *Game Launcher V1 - Setup.exe* from [here](https://github.com/pratham-jaiswal/game-launcher-app/releases/tag/Latest).
- Double click on it to install *Game Launcher*.
- Run the *Game Launcher* app.
- Click the *Add Game* button to select and add your game's .exe file to the launcher. Make sure it's a correct **executable** file.
- Select a game from the list, and click the *Remove Game* button to remove the selected game from the launcher.
- Select a game from the list, and click the *Launch Game* button to start the selected game.

## Get Started with Code
- Make sure you have Python installed
- Clone the repository
    ```sh
    git clone https://github.com/pratham-jaiswal/game-launcher-app.git
    ```
- Install the dependencies
    ```sh
    pip install tkinter ttkthemes pickle
    ```
- Run the *main.py*
    ```sh
    python main.py
    ```
- The *Game Launcher* app will open.
- Click the *Add Game* button to select and add your game's .exe file to the launcher. Make sure it's a correct **executable** file.
- Select a game from the list, and click the *Remove Game* button to remove the selected game from the launcher.
- Select a game from the list, and click the *Launch Game* button to start the selected game.

## Feedback and Contributions
Your feedback is invaluable to me! If you encounter any issues, have suggestions for improvements, or want to contribute to the development of Game Launcher, please don't hesitate to [open an issue](https://github.com/pratham-jaiswal/game-launcher-app/issues) on my GitHub repository.

## License
This project is licensed under the MIT License. Feel free to use and modify the code for your own purposes.