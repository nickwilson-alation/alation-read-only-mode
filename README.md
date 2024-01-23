# Alation Read-Only Mode Management Script
This Python script is designed to manage user profiles in Alation, specifically for toggling between read-only and write modes. It allows you to update user roles, parse user profile changes, and import user profiles back into the application.

# Features
* Get and save user profiles in CSV format.
* Update user profiles to read-only mode (VIEWER role).
* Parse changes in user profiles.
* Import updated user profiles back to Alation.
* Option to undo read-only mode by restoring original user profiles.

# Requirements
* Python 3.x

# Installation
Before running the script, ensure you have Python 3 installed on your system. You can install the required libraries using:

```bash
pip install -r requirements.txt
```

# Arguments
* --token: Your Alation API token. Required.
* --undo-read-only: Flag to undo read-only mode and put Alation back into write mode.
* --original-user-profile-file: Path to the original user profile file that needs to be restored. Required if --undo-read-only is set.
* --except-users: A list of usernames (email addresses) for users whose roles should not be changed to VIEWER. Optional but required if --undo-read-only is False.
* --dry-run: Runs the script in "dry run" mode. No actual changes will be made.

# Usage
The script can be run from the command line with various arguments. Below are some usage examples:

## Basic Usage
To run the script in read-only mode and update all user profiles:

```bash
python main.py --token YOUR_API_TOKEN
```

## Exclude Specific Users from Read-Only Mode
To update all users except for specified ones:

```bash
python main.py --token YOUR_API_TOKEN --except-users "user1@example.com" "user2@example.com"
```

## Undo Read-Only Mode
To undo the read-only mode and restore original profiles:

```bash
python main.py --token YOUR_API_TOKEN --undo-read-only --original-user-profile-file "./output/YYYY_MM_DD_HH_MM_SS/original_user_profiles.csv"
```
Replace YYYY_MM_DD_HH_MM_SS with the actual date and time directory that contains the original user profiles.

## Dry Run
To execute a dry run (no actual changes will be made):

```bash
python main.py --token YOUR_API_TOKEN --dry-run
```

# Disclaimer

This project and all the code contained within this repository is provided "as is" without warranty of any kind, either expressed or implied, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. The entire risk as to the quality and performance of the project is with you.

The author, including Alation, shall not be responsible for any damages whatsoever, including direct, indirect, special, incidental, or consequential damages, arising out of or in connection with the use or performance of this project, even if advised of the possibility of such damages.

Please understand that this project is provided for educational and informational purposes only. Always ensure proper testing, validation and backup before implementing any code or program in a production environment.

By using this project, you accept full responsibility for any and all risks associated with its usage.