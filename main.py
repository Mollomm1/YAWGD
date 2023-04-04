# Set the website to download
website = input("type website url like (http://example.com/game) > ")

# Import required modules
import asyncio
import os
import requests
from urllib.parse import urlparse
from pathlib import Path
from playwright.async_api import Playwright, async_playwright

# Define a function to intercept and handle all requests
async def catch_all_requests(playwright: Playwright):
    # Launch a headful Firefox browser
    browser = await playwright.firefox.launch(headless=False)
    # Create a new page
    page = await browser.new_page()

    async def intercept_request(route, request):
        # Print the URL of the requested resource
        print(f"Downloading: {request.url}")
        # Make a request to the URL using the requests module
        received = requests.get(request.url, headers=request.headers, timeout=2)
        # Parse the URL to get the file name
        url = urlparse(request.url)
        filename = url.path.split("/")[-1]
        if not filename:
            filename = "index.html"
        
        # Create the directory path for the file
        domain = url.netloc.split(".")[0]
        path=str(Path(url.path)).replace("\\", "/")
        try:
            path2 = path[0:-len(path.split("/")[-1])]
        except:
            path2=path
        if os.path.basename(request.url) == None:
            directory = Path(f"./downloads/{url.hostname}{path2}")
        else:
            if "html" in received.headers["Content-Type"].split('/')[-1]:
                directory = Path(f"./downloads/{url.hostname}{path}")
            else:
                directory = Path(f"./downloads/{url.hostname}{path2}")
        # Create the directory if it doesn't exist
        directory.mkdir(parents=True, exist_ok=True)
        
        # Save the file to disk
        if str(path).replace("\\", "/")[-1] == "/":
            savepath=str(path).replace("\\", "/")+"/index.html"
        else:
            if "html" in received.headers["Content-Type"].split('/')[-1]:
                savepath=str(path).replace("\\", "/")+"/index.html"
            else:
                savepath=str(path).replace("\\", "/")
        with open((f"./downloads/{url.hostname}"+savepath), "wb") as f:
            f.write(received.content)

        # Continue the request
        await route.continue_()

    # Route all requests to the intercept_request function
    await page.route("**", intercept_request)
    # Navigate to the website
    
    await page.goto(website)

    # Wait indefinitely for requests
    while True:
        await asyncio.sleep(1)

# Define the main function to run the script
async def main():
    async with async_playwright() as playwright:
        await catch_all_requests(playwright)

# Run the script
asyncio.run(main())
