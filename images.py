import os
import re
import shutil
import yaml

# Paths
posts_dir = r"D:\McBoss Blog Public\McBoss-Blog\content\posts"
attachments_dir = r"D:\Obsidian Vault - MCBOSS BLOG\McBoss Blog\attachments"
static_images_dir = r"D:\McBoss Blog Public\McBoss-Blog\static\images"

# Ensure static_images_dir exists
os.makedirs(static_images_dir, exist_ok=True)

def copy_image(image_name):
    """Copy image from attachments to static/images if exists."""
    # Remove any leading "images/" folder in reference
    image_filename = os.path.basename(image_name)
    src_path = os.path.join(attachments_dir, image_filename)
    if os.path.exists(src_path):
        shutil.copy(src_path, static_images_dir)
        print(f"Copied: {image_filename}")
    else:
        print(f"Warning: Image not found in attachments: {image_filename}")

# Process each Markdown file
for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue

    filepath = os.path.join(posts_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # --- 1. Front matter images ---
    fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if fm_match:
        front_matter_text = fm_match.group(1)
        try:
            fm_data = yaml.safe_load(front_matter_text)
            # images: list
            if "images" in fm_data and isinstance(fm_data["images"], list):
                for img in fm_data["images"]:
                    copy_image(img)
            # cover: image field
            if "cover" in fm_data and "image" in fm_data["cover"]:
                copy_image(fm_data["cover"]["image"])
        except Exception as e:
            print(f"Error parsing front matter in {filename}: {e}")

    # --- 2. Obsidian-style ![[image.png]] ---
    obsidian_images = re.findall(r'!\[\[([^\]]+\.(png|jpg|jpeg|gif))\]\]', content)
    for img_tuple in obsidian_images:
        copy_image(img_tuple[0])

    # --- 3. Markdown inline images /images/... or just filenames ---
    markdown_images = re.findall(r'!\[.*?\]\((.*?)\)', content)
    for img_path in markdown_images:
        copy_image(img_path)

print("All images processed and copied to static/images.")
