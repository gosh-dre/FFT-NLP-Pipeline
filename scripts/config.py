import yaml
import os

config_path = os.path.join(os.getcwd(), "config.yaml")

with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)

app_data_path = os.path.join(config_data['default']['app_data_path'], "app_data.yaml")
with open(app_data_path, 'r') as file:
    app_data = yaml.safe_load(file)

rgx_list = [r"\d{2}/\d{2}/\d{4}", r"\d{2}-\d{2}-\d{4}"]
