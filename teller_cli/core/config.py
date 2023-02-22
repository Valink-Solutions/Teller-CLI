import os
import configparser
import keyring

def create_or_load_config_file(config_file_path):
    config = configparser.ConfigParser()

    # Check if the configuration file exists
    if os.path.exists(config_file_path):
        config.read(config_file_path)
    else:
        # Create a new configuration file with default values
        config['API'] = {
            'API_URL': 'http://localhost:8080',
            'TELLER_LITE_API_TOKEN': ''
        }

        # Prompt the user to enter the API URL and API token
        api_url = input('Enter the API URL: ')
        api_token = input('Enter the API token: ')

        # Store the encrypted API token in the system's keyring
        keyring.set_password('API', 'TELLER_LITE_API_TOKEN', api_token)

        # Update the configuration file with the user's values
        config['API']['API_URL'] = api_url
        config['API']['TELLER_LITE_API_TOKEN'] = '****'

        # Write the configuration file to disk
        with open(config_file_path, 'w') as config_file:
            config.write(config_file)

    # Retrieve the API URL and decrypted API token from the configuration file
    api_url = config['API']['API_URL']
    api_token = keyring.get_password('API', 'TELLER_LITE_API_TOKEN')

    return api_url, api_token
