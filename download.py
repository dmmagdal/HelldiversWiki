# download.py
# Download and archive Helldivers Wiki pages into a local 
# Obsidian-compatible vault.
# Windows/MacOS/Linux
# Python 3.10


import os
import re
import urllib.parse
from typing import List

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


# Wiki configuration for Helldivers wiki.gg
BASE_DOMAIN = "helldivers.wiki.gg"
BASE_URL = f"https://{BASE_DOMAIN}"
API_URL = f"{BASE_URL}/api.php"

OUTPUT_DIR = "helldivers_wiki_vault"
MEDIA_DIR = os.path.join(OUTPUT_DIR, "media")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)

HEADERS = {
	"User-Agent": "HelldiversWikiDownloader/1.0 (Obsidian Archiver)"
}


def sanitize_filename(name: str) -> str:
	"""
	Sanitize title or URL paths for safe local filenames.
	@param: name (str) - The filename or URL path to sanitize.
	@return: str - The sanitized filename suitable for local storage.
	"""
	name = urllib.parse.unquote(name)
	name = name.replace("/", "_")
	return re.sub(r'[\\*?:"<>|]', "", name).strip()


def get_all_wiki_pages(max_pages: int = None) -> List[str]:
	"""
	Fetch main namespace pages from Wiki.gg using pagination.
	@param: max_pages (int) - Maximum number of pages to fetch.
	@return: List[str] - List of page titles.
	"""
	pages = []
	apcontinue = None

	print("Fetching list of pages from wiki...")
	while True:
		params = {
			"action": "query",
			"list": "allpages",
			"apnamespace": 0,  # Main namespace only (excludes talk, templates, category pages)
			"aplimit": min(500, max_pages - len(pages) if max_pages is not None else 500),
			"format": "json"
		}
		if apcontinue:
			params["apcontinue"] = apcontinue

		try: 
			res = requests.get(API_URL, params=params, headers=HEADERS)
			data = res.json()
		except Exception as e:
			print(f"  [!] Failed to fetch page: {e}")
			break

		batch = data.get("query", {}).get("allpages", [])
		for page in batch:
			pages.append(page["title"])

		# for page in data.get("query", {}).get("allpages", []):
		# 	pages.append(page["title"])
			if max_pages is not None and len(pages) >= max_pages:
				break

		print(f"  -> Discovered {len(pages)} pages so far...")

		continue_data = data.get("continue", {})
		if not continue_data or "continue" not in continue_data:
			break

		apcontinue = continue_data.get("apcontinue")

		# apcontinue = data.get("continue", {}).get("apcontinue")
		# if not apcontinue or (max_pages is not None and len(pages) >= max_pages):
		# 	break

	return pages

def download_media(src_url: str) -> str:
	"""
	Download local images/media and save them in the media folder.
	@param: src_url (str) - The URL of the media to download.
	@return: str - The local filename of the downloaded media.
	"""
	if src_url.startswith("//"):
		src_url = "https:" + src_url
	elif src_url.startswith("/"):
		src_url = BASE_URL + src_url

	# Strip Wiki.gg thumb parameters (e.g. 
	# /thumb/filename.png/300px-filename.png -> /filename.png).
	if "/thumb/" in src_url:
		parts = src_url.split("/thumb/")
		src_url = parts[0] + "/" + parts[1].rsplit("/", 1)[0]

	filename = os.path.basename(urllib.parse.urlparse(src_url).path)
	filename = sanitize_filename(filename)
	local_filepath = os.path.join(MEDIA_DIR, filename)

	if not os.path.exists(local_filepath):
		try:
			res = requests.get(src_url, headers=HEADERS, timeout=10)
			if res.status_code == 200:
				with open(local_filepath, "wb") as f:
					f.write(res.content)
		except Exception as e:
			print(f"  [!] Failed to download media {filename}: {e}")

	return filename


def process_page(title: str) -> None:
	"""
	Fetch parsed HTML, process links and images, then export to 
		Markdown.
	@param: title (str) - The title of the wiki page to process.
	@return: None.
	"""
	print(f"Downloading & Processing: {title}")
	
	params = {
		"action": "parse",
		"page": title,
		"format": "json",
		"prop": "text",
		"disablepp": True
	}

	try: 
		res = requests.get(API_URL, params=params, headers=HEADERS)
		data = res.json()
	except Exception as e:
		print(f"  [!] Failed to fetch page '{title}': {e}")
		return

	if "error" in data:
		print(f"  [!] Skipped '{title}': {data['error'].get('info')}")
		return

	html_content = data["parse"]["text"]["*"]
	soup = BeautifulSoup(html_content, "html.parser")

	# 1. Clean Wiki UI Clutter.
	for element in soup.select(".navbox, .mw-editsection, .printfooter, .catlinks, script, style"):
		element.decompose()

	# 2. Process Media / Images.
	for img in soup.find_all("img"):
		img_src = img.get("src") or img.get("data-src")
		if img_src:
			local_name = download_media(img_src)

			# Update image src to point to local media directory.
			img["src"] = f"media/{local_name}"

	# 3. Preserve Internal Connections (Convert Wiki Links to Obsidian 
	# Wikilinks).
	for a in soup.find_all("a", href=True):
		href = a["href"]

		# Check if the link is an internal Wiki page link.
		if href.startswith("/wiki/") and not ":" in href.replace("/wiki/", ""):
			target_title = href.replace("/wiki/", "").split("#")[0]
			target_title = urllib.parse.unquote(target_title)\
				.replace("_", " ")
			
			# Replace <a> tag with Obsidian [[Link]] inline markup.
			a.replace_with(f"[[{target_title}]]")

	# 4. Convert Cleaned HTML to Markdown.
	markdown = md(
		str(soup), 
		heading_style="ATX", 
		code_language="python"
	)

	# 5. Save output file.
	file_name = sanitize_filename(title) + ".md"
	file_path = os.path.join(OUTPUT_DIR, file_name)
	
	with open(file_path, "w", encoding="utf-8") as f:
		f.write(f"# {title}\n\n{markdown}")


def main():
	# Adjust max_pages limit as needed (Set higher to scrape more of 
	# the wiki).
	# pages = get_all_wiki_pages(max_pages=30) 
	pages = get_all_wiki_pages()
	print(f"Found {len(pages)} pages to fetch.")

	for title in pages:
		process_page(title)

	print(f"\nDone! Vault ready at: ./{OUTPUT_DIR}")


if __name__ == "__main__":
	main()
