import os
import re
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import SeleniumURLLoader

START_URL = "https://www.xfinity.com/terms/web"
OUTPUT_FOLDER = "data_selenium" 
BASE_DOMAIN = "https://www.xfinity.com"  

visited_urls = set()
error_urls = []  

if not os.path.exists(OUTPUT_FOLDER):
   os.makedirs(OUTPUT_FOLDER)

def sanitize_filename(url):
   """Generate a clean filename by removing domain & replacing invalid characters."""
   #filename = url.replace(BASE_DOMAIN, "").strip("/")  # Remove domain
   filename = url.replace("/", "_")  
   filename = re.sub(r'[<>:"/\\|?*]', '', filename)  
   if filename == "":
       filename = "index"  # Default name for homepage
   return filename[:100].strip() + ".txt"
def extract_links(url):
   """Extract all valid internal links from the given page."""
   try:
       response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
       soup = BeautifulSoup(response.text, "html.parser")
       links = set()
       for a_tag in soup.find_all("a", href=True):
           sub_url = a_tag["href"]
           # Ignore navigation links (e.g., #section1)
           if "#" in sub_url:
               continue  
           # Convert relative URLs to absolute URLs
           if sub_url.startswith("/"):
               sub_url = BASE_DOMAIN + sub_url
           # Only allow links within Xfinity
           if sub_url.startswith(BASE_DOMAIN) and sub_url not in visited_urls:
               links.add(sub_url)
       return links
   except Exception as e:
       print(f"Error extracting links from {url}: {e}")
       return set()
def scrape_page(url):
   """Scrapes a page using SeleniumURLLoader, extracts links, and follows them recursively."""
   if url in visited_urls:
       return  # Stop if already visited
   print(f"Scraping: {url}")
   visited_urls.add(url)  # Mark as visited
   try:
      
       loader = SeleniumURLLoader(urls=[url])
       docs = loader.load()
       page_text = docs[0].page_content  
       file_name = sanitize_filename(url)
       file_path = os.path.join(OUTPUT_FOLDER, file_name)
    
       with open(file_path, "w", encoding="utf-8") as f:
           f.write(f"URL: {url}\n\n{page_text}")  

       print(f"Saved: {file_path}")
       sub_links = extract_links(url)
       for sub_link in sub_links:
           scrape_page(sub_link)
   except Exception as e:
       print(f" Error scraping {url}: {e}")
       error_urls.append(url)  # Log failed URLs

scrape_page(START_URL)
if error_urls:
   with open(os.path.join(OUTPUT_FOLDER, "failed_urls.txt"), "w") as f:
       f.write("\n".join(error_urls))
print("\n Scraping completed! All pages are saved inside the 'data_selenium' folder.")
print("Number of URLS visited : ", len(visited_urls))
print("Number of error URLs: ", len(error_urls))
print(visited_urls)