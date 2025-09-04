import os
import re
import shutil
import yaml
from urllib.parse import quote

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

def process_file_content(content):
    """Process and replace image references in content."""
    # Replace ![[image.png]] with ![](/images/image.png) with URL encoding
    def replace_exclaim_brackets(match):
        filename = match.group(1)
        encoded_filename = quote(filename)
        return f'![](/images/{encoded_filename})'
    
    # Replace [[image.png]] with ![](/images/image.png) with URL encoding  
    def replace_plain_brackets(match):
        filename = match.group(1)
        encoded_filename = quote(filename)
        return f'![](/images/{encoded_filename})'
    
    # Process ![[]] format first
    content = re.sub(
        r'!\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg))\]\]',
        replace_exclaim_brackets,
        content,
        flags=re.IGNORECASE
    )
    
    # Process [[]] format (not preceded by !)
    content = re.sub(
        r'(?<!\!)\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg))\]\]',
        replace_plain_brackets,
        content,
        flags=re.IGNORECASE
    )
    
    return content

# Process each Markdown file
for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue

    filepath = os.path.join(posts_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Store original content for comparison
    original_content = content

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

    # --- 2. Find and copy Obsidian-style images (both ![[]] and [[]]) ---
    # Find ![[image.png]] format - extract original filename for copying
    obsidian_images_exclaim = re.findall(r'!\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg))\]\]', content, re.IGNORECASE)
    for img_tuple in obsidian_images_exclaim:
        copy_image(img_tuple[0])  # img_tuple[0] is the filename

    # Find [[image.png]] format - extract original filename for copying
    obsidian_images_plain = re.findall(r'(?<!\!)\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg))\]\]', content, re.IGNORECASE)
    for img_tuple in obsidian_images_plain:
        copy_image(img_tuple[0])  # img_tuple[0] is the filename

    # --- 3. Markdown inline images /images/... or just filenames ---
    markdown_images = re.findall(r'!\[.*?\]\((.*?)\)', content)
    for img_path in markdown_images:
        # Skip if it's already a URL-encoded path or starts with /images/
        if not img_path.startswith('/images/') and '%' not in img_path:
            copy_image(img_path)

    # --- 4. Replace image references in content ---
    content = process_file_content(content)

    # Write back to file if content changed
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated image references in: {filename}")

print("All images processed and copied to static/images.")
print("All image references updated in markdown files.")
print("\n" + "="*60)
print("COMPLETE WORKFLOW FINISHED:")
print("1. ✅ Robocopy mirror: Obsidian posts → Hugo content/posts")
print("2. ✅ Image processing: Copy images and update references")
print("="*60)