#!/usr/bin/env python3
import subprocess
import sys

# List of required system commands
required_commands = ["ratbagctl", "notify-send"]
# Check for missing commands
missing_commands = [command for command in required_commands if subprocess.run(
    ["which", command], capture_output=True).returncode != 0]
if missing_commands:
    print("The following required system commands are missing:")
    for command in missing_commands:
        print(command)
        print("\nScript cannot proceed without aforementioned commands. Exiting")
        sys.exit(1)


def send_msg(title, msg):
    subprocess.run([
        "notify-send", "-u", "normal", "-t", "3000",
        title, str(msg)
        ], check=True)


def get_rat():
    result = subprocess.run(["ratbagctl", "list"],
                            capture_output=True, text=True, check=True)
    output_lines = result.stdout.splitlines()

    if len(output_lines) == 1:
        rat = output_lines[0].split(':')[0]
        return rat
    else:
        send_msg("ERROR",
                 "More than 1 mouse detected, exiting script")
        sys.exit(1)


def get_active_profile(rat):
    result = subprocess.run([
        "ratbagctl", rat, "profile", "active", "get"],
        capture_output=True, text=True, check=True)
    return result.stdout


def get_total_active_profiles(rat):
    result = subprocess.run([
        "ratbagctl", rat, "info"],
        capture_output=True, text=True, check=True)
    lines = result.stdout.split('\n')
    profile_count = 0
    for line in lines:
        if line.startswith("Profile") and "(disabled)" not in line:
            profile_count += 1
    if profile_count > 0:
        print(f'Number of active profiles detected: {profile_count}')
        return profile_count
    else:
        send_msg("ERROR",
                 "Something went horribly wrong with acquiring profiles")
        sys.exit(1)


def select_next_profile(cur_profile, nr_of_profiles):
    profile_list = [i for i in range(nr_of_profiles)]
    print(profile_list)
    try:
        current_index = profile_list.index(int(cur_profile.strip()))
        next_index = (current_index + 1) % len(profile_list)
        next_profile = profile_list[next_index]
        print(f'Current IX: {current_index},'
              f'next_index: {next_index}, '
              f'next_profile: {next_profile}')
        return next_profile
    except ValueError:
        send_msg("ERROR", "Current profile is not valid")
        sys.exit(1)


def activate_profile(rat, next_profile):
    result = subprocess.run([
        "ratbagctl", rat, "profile", "active", "set", str(next_profile)])
    if result.returncode != 0:
        print("Profile activation failed")
        send_msg("ERROR", f"Failed to activate profile: {next_profile}")
        sys.exit(1)


def map_profile_name(profile):
    if profile == 0:
        return "WORK"
    if profile == 1:
        return "GAMING"
    else:
        send_msg("WARNING", "UNDEFINED profile detected, please fix mapping")
        return "UNDEFINED"


def main():
    rat = get_rat()
    nr_of_profiles = get_total_active_profiles(rat)
    cur_profile = get_active_profile(rat)
    next_profile = select_next_profile(cur_profile, nr_of_profiles)
    activate_profile(rat, next_profile)

    cur_profile = next_profile
    cur_profile_name = map_profile_name(cur_profile)
    send_msg("SUCCESS", f'{cur_profile_name} profile activated')


if __name__ == "__main__":
    main()
