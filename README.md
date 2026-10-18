# Helldivers Wiki Archive

Description: A lightweight python script for downloading and archiving the entire [Helldivers Wiki (`wiki.gg`)](https://helldivers.wiki.gg/) into a local, offline-ready **Obsidian-compatible vault**. 


### Setup & Usage

 - Use conda to create the environment: `conda create -f env.yml`
 - Activate the conda environment: `conda activate wikigg`
 - Run the download script. This should take a few minutes: `python download.py`


### Notes

 - Current storage requirements for helldivers wiki is 20 GB.
     - Most of the storage comes from the `/helldivers_wiki_vault/media/` folder (~19 GB).
     - Running the `png_webp_convert.py` will take the `.png` images from `/helldivers_wiki_vault/media/` and convert them into `webp` (lossless version). This will reduce the strain from 19 GB to 13 GB but requires all image sources in the markdown files to re-route to `/helldivers_wiki_vault/media_webp/`. 


### TODO

 - Have SHA based hashing to check for updates to pages. May need to include some metadata tracker to keep track of most recent sha of each page (not markdown since the format conversion wont match hashes).
 - Rework the image conversion/compression so that everything is in the `download.py` script and add args to allow either use of `webp` or `png` and keep everything in the same `media` folder.