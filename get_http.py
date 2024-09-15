import requests
from bs4 import BeautifulSoup
import time
import os

# Base URL for the directory
base_url = "https://download.bls.gov/pub/time.series/ap/"
output_folder = "downloads"  # Directory for saving files

# List of files to download
file_list = [
    "ap.area",
    "ap.contacts",
    "ap.data.0.Current",
    "ap.data.1.HouseholdFuels",
    "ap.data.2.Gasoline",
    "ap.data.3.Food",
    "ap.footnote",
    "ap.item",
    "ap.period",
    "ap.seasonal",
    "ap.series",
    "ap.txt",
]

# Make sure the output directory exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Headers to mimic your browser's request
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "Referer": "https://download.bls.gov/",  # Referrer is important, mimicking the browser's navigation request.
}

# Fetch the HTML content from the base URL with headers.
response = requests.get(base_url, headers=headers)
response.raise_for_status()  # Ensure the request was successful (200 OK)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Find all <a> (anchor) tags in the HTML
links = soup.find_all("a")

# Loop through each known file from the file_list
for file_name in file_list:
    # Find the anchor tag where href ends with the file we want
    file_link = None
    for link in links:
        if link.get("href") and file_name in link.get("href"):
            file_link = link["href"]
            break

    if file_link:
        # Construct the full URL of the file to be downloaded
        file_url = base_url + file_name
        file_path = os.path.join(output_folder, file_name)
        
        try:
            print(f"Downloading {file_name} from {file_url} ...")
            # Download the file content with the same headers for each individual file
            file_response = requests.get(file_url, headers=headers)
            file_response.raise_for_status()  # Ensure the download request was successful

            # Save the file locally
            with open(file_path, "wb") as f:
                f.write(file_response.content)
            print(f"Successfully downloaded {file_name}")

        except Exception as e:
            print(f"Failed to download {file_name}. Error: {e}")

    else:
        print(f"File '{file_name}' not found on the page.")

    # Avoid rapid consecutive requests to the server
    time.sleep(3)

print("Download attempts completed.")
