# Helldivers Wiki Archive

Description: A lightweight python script for downloading and archiving the entire [Helldivers Wiki (`wiki.gg`)](https://helldivers.wiki.gg/) into a local, offline-ready **Obsidian-compatible vault**. 


### Setup & Usage

 - Use conda to create the environment: `conda create -f env.yml`
 - Activate the conda environment: `conda activate wikigg`
 - Run the download script. This should take a few minutes: `python download.py`


### Notes

 - Current storage requirements for helldivers wiki is 20 GB.


### TODO

 - Have SHA based hashing to check for updates to pages. May need to include some metadata tracker to keep track of most recent sha of each page (not markdown since the format conversion wont match hashes).