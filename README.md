# Game Launcher
The Game Launcher is a Windows application that streamlines the management of your gaming library by using AI to detect games in a specified folder and allowing you to effortlessly add, remove, and launch games from a centralized location. It is packaged as a standalone executable for easy use and distribution.

## Features
- Add games to the launcher by selecting their executable files.
- Use AI to automatically detect and add games from specified folders.
- Remove unwanted games from the list with ease.
- Quickly launch your favorite games.

### Note:
- Deleting the `games.pkl` file would remove all the games from the launcher.
- Deleting the `icon.png` file would result in crashing of the launcher. To fix this:
	1. Copy and paste the `games.pkl` file somewhere safe.
	2. Re-install the *Game Launcher* app.
	3. Now move the copied `games.pkl` in the installed directory.

## Installing and Using the App
### Note:
The *Game Launcher* application is only available for Windows.

### Installation:
1. Download the latest setup from [here](https://github.com/pratham-jaiswal/game-launcher-app/releases/tag/Latest).
2. Double click on it to install *Game Launcher*.

### Usage:
1. Run the *Game Launcher* app.
2. Click the *Add Game* button to select and add your game's .exe file to the launcher. Make sure it's a correct **executable** file.
3. Select a game from the list, and click the *Remove Game* button to remove the selected game from the launcher.
4. Select a game from the list, and click the *Launch Game* button to start the selected game.

## Get Started with Code

#### 1. Ensure Python is Installed  
Make sure you have Python installed on your system. You can download and install it from [python.org](https://www.python.org/).

#### 2. Clone the Repository  
Clone the project repository to your local system using the following command:  
```sh
git clone https://github.com/pratham-jaiswal/game-launcher-app.git
```
Navigate into the project directory:  
```sh
cd game-launcher-app
```

#### 3. Create and Configure the `.env` File  
The application requires certain environment variables to function properly. Follow these steps to set them up:  

1. Copy the `.env.example` file and rename it to `.env`:  

2. Open the `.env` file in a text editor and replace `'Your API Key'` with the actual API keys from the respective providers.
```.env
COHERE_API_KEY='your-cohere-api-key'  # Obtain from https://cohere.com/
OPENAI_API_KEY='your-openai-api-key'  # Obtain from https://openai.com/
LLM_CHOICE='Cohere'  # Specify which language model to use (e.g., OpenAI or Cohere)
```

> **Note:** If you don’t have API keys, sign up on the respective platforms ([Cohere](https://dashboard.cohere.com/api-keys)/[OpenAI](https://platform.openai.com/api-keys)) and generate your API keys.

#### 4. Install Dependencies  
Install the required dependencies by running:  
```sh
pip install -r requirements.txt
```

#### 5. Run the Application  
Start the application using:  
```sh
python main.py
```

#### 6. Using the Game Launcher  
- The *Game Launcher* app will open.  
- Click the **Add Game** button to select and add your game's `.exe` file to the launcher. Ensure it is a valid **executable** file.  
- Select a game from the list and click the **Remove Game** button to delete it from the launcher.  
- Select a game from the list and click the **Launch Game** button to start it.

## Feedback and Contributions
I would love to hear your thoughts on Game Launcher! If you encounter any issues, have suggestions for improvements, or would like to contribute to its development, please don't hesitate to [open an issue](https://github.com/pratham-jaiswal/game-launcher-app/issues) on my GitHub repository. Your feedback is invaluable to me and will help me to make Game Launcher an even better application.

## License
This project is licensed under the [MIT License](LICENSE). You are free to use and modify the code for your own purposes.