import multiprocessing
import os
import shutil
import pyfiglet
import requests
import time
import re
from core.controllers import Controller
from core.arguments import parse_args

# Clear the terminal screen (cross-platform)
def clear_screen():
    if os.name == 'posix':  # For UNIX-based systems (Linux and macOS)
        os.system('clear')
    elif os.name == 'nt':  # For Windows
        os.system('cls')

# Function to display PyFiglet text
def display_pyfiglet():
    columns, rows = shutil.get_terminal_size()
    clear_screen()
    ascii_text = pyfiglet.figlet_format("GRIM Finder", font="slant")
    lines = ascii_text.split("\n")
    positions = []
    x = int(columns / 2 - len(max(lines, key=len)) / 2)
    for i in range(len(lines)):
        y = int(rows / 2 - len(lines) / 2 + i)
        positions.append(y)
    print("\033[1m\033[32m", end="")
    for i in range(len(lines)):
        print(f"\033[{positions[i]};{x}H{lines[i]}")
    print("\033[1m\033[35m", end="")
    print(f"\033[{positions[-1]+1};{x};{x}H[ Information ] : Remastered Edition Of H0nde Claimable Finder")
    print("\033[0m", end="")

# Display PyFiglet text initially
display_pyfiglet()

def get_content_from_sources():
    """
    Makes HTTP requests to the sources, retrieves the content, parses the content for
    proxy information, removes duplicates, and sorts the proxies.
    """
    # Add the URLs of the sources here
    sources = [
        
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt'


    ]

    # Make an HTTP request to each URL and retrieve the content
    content = []
    for url in sources:
        response = requests.get(url)
        content.append(response.text)

    # Parse the content for proxy information, remove duplicates, and sort the proxies
    proxies = []
    for text in content:
        regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
        proxies += re.findall(regex, text)
    proxies = list(set(proxies))
    proxies.sort()

    # Write the proxies to a file
    with open('proxies.txt', 'w') as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    return proxies


def get_proxies_option():
    while True:
        user_choice = input("Do you want to auto-scrape proxies from sources (1) or use proxies from 'proxies.txt' (2)? Enter 1 or 2: ")
        if user_choice in ['1', '2']:
            return int(user_choice)
        else:
            print("Invalid choice. Please enter 1 or 2.")

def create_proxies_file():
    with open('proxies.txt', 'w') as f:
        f.write('')  # Create an empty 'proxies.txt' file

# Check if 'proxies.txt' exists and create it if not
if not os.path.exists('proxies.txt'):
    create_proxies_file()

# Clear the screen after the file creation
clear_screen()

if __name__ == "__main__":
    choice = get_proxies_option()
    
    if choice == 1:
        proxies = get_content_from_sources()
    elif choice == 2:
        # Read proxies from 'proxies.txt'
        try:
            with open('proxies.txt', 'r') as file:
                proxies = [line.strip() for line in file]
        except FileNotFoundError:
            print("Error: 'proxies.txt' file not found. Please make sure the file exists with proxy data.")
            exit(1)
    
    # Display PyFiglet text again and "Finder started..."
    display_pyfiglet()
    print("Finder started...")

    multiprocessing.freeze_support()
    controller = Controller(arguments=parse_args())
    
    try:
        controller.join_workers()
    except KeyboardInterrupt:
        pass