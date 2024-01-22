import json
import requests
import pandas as pd
from datetime import datetime
import os

# Helper function to create output directory
def create_output_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Step 1: Get User Profile Template
def get_user_profile(api_token):
    url = 'https://nick-sandbox-rightstart.alationproserv.com/admin/export/all_user_profiles/'
    headers = {
        'TOKEN': api_token,
        'Cookie': 'csrftoken=VRL9i4mt8NLwwagqBzLAITkJr0NhbD7oTFIQvH9CzTQ6z7RNcAduJtbXHn0WXn5J; sessionid=53f5r4s5pgoeglqn5hkwvgv16h78v470'
    }
    response = requests.get(url, headers=headers)
    date_time = datetime.now().strftime("%Y-%d-%m_%H:%M:%S")
    output_dir = f"./output/{date_time}"
    create_output_directory(output_dir)
    file_path = f"{output_dir}/original_user_profiles.csv"
    with open(file_path, 'w') as file:
        file.write(response.text)
    return file_path, date_time

# Step 2: Update User Profiles
def update_user_profiles(csv_path, date_time):
    df = pd.read_csv(csv_path)
    df['role'] = 'VIEWER'  # Set all roles to VIEWER
    updated_csv_path = f"./output/{date_time}/updated_user_profiles.csv"
    df.to_csv(updated_csv_path, index=False)
    return updated_csv_path

def parse_user_profile_changes(api_token, date_time, updated_csv_path):
    # Assuming the API requires the updated CSV file as input
    # Read the updated CSV and prepare data for the request
    with open(updated_csv_path, 'rb') as file:
        files = {'file': file}
        url = 'https://nick-sandbox-rightstart.alationproserv.com/api/parse_changes/'
        headers = {
            'TOKEN': api_token,
            # Add other necessary headers here
        }
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            # Assuming the API returns the expected JSON response
            output_path = f"./output/{date_time}/parsed_user_profiles.json"
            with open(output_path, 'w') as json_file:
                json.dump(response.json(), json_file, indent=4)
        else:
            print("Failed to parse user profile changes. Status Code:", response.status_code)

# Step 4: Import User Profiles
def import_user_profiles(api_token, updated_csv_path, date_time):
    # Read the updated CSV file
    df = pd.read_csv(updated_csv_path)

    # Convert the DataFrame into the required format for the payload
    # The exact conversion depends on how your API expects the data
    # Here's a basic implementation assuming the API needs JSON data
    payload = {
        "fields": ["user", "display_name", "email", "title", "role"],
        "bad_rows": "",
        "new_users": [],
        "changed_users": df.to_dict(orient='records'),
        "unchanged_users": [],  # Add logic if needed
        "skipped_rows": ""
    }

    # Format the payload as 'application/x-www-form-urlencoded'
    formatted_payload = f"csrfmiddlewaretoken=WISrYX3tCCCBJFAj2ewraJce05zxMQ9BtoiYeJyzZCKstj8qj0Lf4U6pnQ9z5Jsi&payload={json.dumps(payload)}&overwrite=yes"

    url = 'https://nick-sandbox-rightstart.alationproserv.com/admin/import_user_profiles/'
    headers = {
        'TOKEN': api_token,
        # Add other necessary headers here
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        # Include other headers as per your cURL command
    }

    response = requests.post(url, headers=headers, data=formatted_payload)
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Failed to import user profiles. Status Code:", response.status_code)

# Replace '{{MY_API_TOKEN}}' with your actual API token
api_token = '{{MY_API_TOKEN}}'

# Execute the steps
csv_path, date_time = get_user_profile(api_token)
updated_csv_path = update_user_profiles(csv_path, date_time)
parse_user_profile_changes(api_token, date_time)
import_user_profiles(api_token, updated_csv_path)
