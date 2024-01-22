import argparse
import json
import requests
import pandas as pd
from datetime import datetime
import os

# Helper function to create output directory
def create_output_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def set_to_read_only():
    get_user_profile();

# Step 1: Get User Profile Template
def get_user_profile(api_token, date_time, output_dir):
    url = 'https://nick-sandbox-rightstart.alationproserv.com/admin/export/all_user_profiles/'
    headers = {
        'TOKEN': api_token,
        'Cookie': 'csrftoken=VRL9i4mt8NLwwagqBzLAITkJr0NhbD7oTFIQvH9CzTQ6z7RNcAduJtbXHn0WXn5J; sessionid=53f5r4s5pgoeglqn5hkwvgv16h78v470'
    }
    response = requests.get(url, headers=headers)
    
    file_path = f"{output_dir}/original_user_profiles.csv"
    with open(file_path, 'w') as file:
        file.write(response.text)
    return file_path, date_time

# Step 2: Update User Profiles
def update_user_profiles(csv_path, date_time, except_users):
    df = pd.read_csv(csv_path)
    # Only update roles for users not in the except-users list
    df['role'] = df.apply(lambda row: 'VIEWER' if row['email'] not in except_users else row['role'], axis=1)
    updated_csv_path = f"./output/{date_time}/updated_user_profiles.csv"
    df.to_csv(updated_csv_path, index=False)
    return updated_csv_path


def parse_user_profile_changes(api_token, date_time, updated_csv_path, output_dir):
    # Extract filename from the path
    filename = os.path.basename(updated_csv_path)
    url = f'https://nick-sandbox-rightstart.alationproserv.com/admin/parse_user_profiles/?qqfile={filename}'
    headers = {
        'token': api_token,
        'authority': 'nick-sandbox-rightstart.alationproserv.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/octet-stream',
        'origin': 'https://nick-sandbox-rightstart.alationproserv.com',
        'referer': 'https://nick-sandbox-rightstart.alationproserv.com/admin/user_profiles/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-file-name': filename,
        'x-mime-type': 'text/csv',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    with open(updated_csv_path, 'rb') as file:
        response = requests.post(url, headers=headers, data=file)

    if response.status_code == 200:
        output_path = f"{output_dir}/parsed_user_profiles.json"
        with open(output_path, 'w') as json_file:
            json.dump(response.json(), json_file, indent=4)
        print("User profile changes parsed and saved to", output_path)
    else:
        print("Failed to parse user profile changes. Status Code:", response.status_code, "Response:", response.text)

# Step 4: Import User Profiles
def import_user_profiles(api_token, date_time, updated_csv_path):
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

def main():
    # Create arg parser
    parser = argparse.ArgumentParser(description='Script to manage Alation user profiles.')

    # Add arguments
    parser.add_argument(
        '--token',
        type=str,
        default=os.environ.get('ALATION_TOKEN', None),
        required=os.environ.get('ALATION_TOKEN', None) is None,
        help='Alation API Token'
    )

    parser.add_argument(
        '--except-users',
        nargs='*',
        type=str,
        default=[],
        help='A list of usernames (email addresses) for users that should not be changed to VIEWER'
    )

    parser.add_argument(
        '--undo-read-only',
        action='store_true',
        default=False,
        help='Undo read-only mode and put Alation back into write mode. Use in conjunction with the original-user-profile-file argument.'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='Runs the script in "dry run" mode and will not update anything.'
    )

    parser.add_argument(
        '--original-user-profile-file',
        type=str,
        help='Original user profile file that needs to be restored'
    )

    args = parser.parse_args()

    # Validate arg combos
    if args.undo_read_only and not args.original_user_profile_file:
        parser.error('--original-user-profile-file is required when --undo-read-only is set.')

    date_time = datetime.now().strftime("%Y_%d_%m_%H_%M_%S")
    api_token = args.token
    except_users = args.except_users if args.except_users is not None else []
    output_dir = f"./output/{date_time}"
    create_output_directory(output_dir)

    if not args.undo_read_only:
        # Read only mode:
        csv_path, date_time = get_user_profile(api_token, date_time, output_dir)
        updated_user_profile_csv_path = update_user_profiles(csv_path, date_time, except_users)
        parse_user_profile_changes(api_token, date_time, updated_user_profile_csv_path, output_dir)
        if not args.dry_run:
            import_user_profiles(api_token, date_time, updated_user_profile_csv_path)
    else:
        # Undo mode:
        if not args.dry_run:
            parse_user_profile_changes(api_token, date_time, args.original_user_profile_file, output_dir)
            import_user_profiles(api_token, date_time, args.original_user_profile_file)

if __name__ == "__main__":
    main()