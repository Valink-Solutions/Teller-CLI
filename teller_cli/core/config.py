import os
import configparser
import keyring
from rich import print
from rich.prompt import Prompt


def get_minecraft_saves_folder() -> str:
    if os.name == "posix":  # Unix-based systems (Linux, macOS, etc.)
        return os.path.expanduser("~/.minecraft/saves")
    elif os.name == "nt":  # Windows
        return os.path.join(os.getenv("APPDATA"), ".minecraft", "saves")
    else:
        raise OSError("Unsupported operating system")


def create_or_load_config_file(config_file_path):
    config = configparser.ConfigParser()

    # Check if the configuration file exists
    if os.path.exists(config_file_path):
        config.read(config_file_path)
    else:
        # Create a new configuration file with default values
        config["API"] = {
            "API_URL": "http://localhost:8080",
            "TELLER_LITE_API_TOKEN": "",
        }

        config["DEFAULTS"] = {"SAVES_FOLDER": ""}

        try:
            saves_folder = get_minecraft_saves_folder()
        except OSError:
            print("> [bold red]TELLER-CLI DOES NOT RUN ON YOUR OPERATING SYSTEM :(")
            exit()

        # Prompt the user to enter the API URL and API token
        api_url = Prompt.ask("> Enter the API URL", default="http://localhost:8080")
        api_token = Prompt.ask("> Enter the API token")
        default_saves_folder = Prompt.ask(
            "> Enter a default saves folder.", default=saves_folder
        )

        # Store the encrypted API token in the system's keyring
        keyring.set_password("CHUNKVAULT_API", "TELLER_LITE_API_TOKEN", api_token)

        # Update the configuration file with the user's values
        config["API"]["API_URL"] = api_url
        config["API"]["TELLER_LITE_API_TOKEN"] = "****"
        config["DEFAULTS"]["SAVES_FOLDER"] = default_saves_folder

        # Write the configuration file to disk
        with open(config_file_path, "w") as config_file:
            config.write(config_file)

    # Retrieve the API URL and decrypted API token from the configuration file
    api_url = config["API"]["API_URL"]
    api_token = keyring.get_password("CHUNKVAULT_API", "TELLER_LITE_API_TOKEN")
    default_saves_folder = config["DEFAULTS"]["SAVES_FOLDER"]

    return api_url, api_token, default_saves_folder


def edit_config(config_file_path):
    config = configparser.ConfigParser()

    # Check if the configuration file exists
    if os.path.exists(config_file_path):
        config.read(config_file_path)
    else:
        create_or_load_config_file(config_file_path)
        exit()

    api_url = Prompt.ask("> Enter an API url", default=config["API"]["API_URL"])
    api_token = Prompt.ask(
        "> Enter an API token [grey](leave blank to keep old token)",
        default=keyring.get_password("CHUNKVAULT_API", "TELLER_LITE_API_TOKEN"),
        show_default=False,
    )

    default_saves_folder = Prompt.ask(
        "> Enter a default save location", default=config["DEFAULTS"]["SAVES_FOLDER"]
    )

    keyring.set_password("CHUNKVAULT_API", "TELLER_LITE_API_TOKEN", api_token)

    # Update the configuration file with the user's values
    config["API"]["API_URL"] = api_url
    config["API"]["TELLER_LITE_API_TOKEN"] = "****"
    config["DEFAULTS"]["SAVES_FOLDER"] = default_saves_folder

    # Write the configuration file to disk
    with open(config_file_path, "w") as config_file:
        config.write(config_file)

    print("> [green]Successfully updated config")

    return
