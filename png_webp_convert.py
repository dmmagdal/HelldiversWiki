import os
from PIL import Image


# Configuration directories
SOURCE_DIR = "helldivers_wiki_vault/media"
OUTPUT_DIR = "helldivers_wiki_vault/media_webp"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def convert_pngs_to_webp():
	if not os.path.exists(SOURCE_DIR):
		print(f"Source directory '{SOURCE_DIR}' does not exist.")
		return

	files = sorted(
		[
			f for f in os.listdir(SOURCE_DIR) 
			if f.lower().endswith(".png")
		]
	)
	print(f"Found {len(files)} PNG images to convert...")

	for filename in files:
		src_path = os.path.join(SOURCE_DIR, filename)
		base_name = os.path.splitext(filename)[0]
		dest_path = os.path.join(OUTPUT_DIR, f"{base_name}.webp")

		try:
			with Image.open(src_path) as img:
				# WebP supports transparency natively (RGBA). 
				# quality=80 provides a great balance of size and visual fidelity.
				img.save(dest_path, "WEBP", quality=80, method=6, lossless=True)
			print(f"Converted: {filename} -> media_webp/{base_name}.webp")
		except Exception as e:
			print(f"  [!] Failed to convert {filename}: {e}")

	print("\nBatch conversion complete!")


if __name__ == "__main__":
	convert_pngs_to_webp()
