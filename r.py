import glob
import os
from bs4 import BeautifulSoup

# Set this to the directory containing your HTML files
directory = "/root/bupkis.org/www.bupkis.org/index.php/recipes-2"

for html_file in glob.glob(os.path.join(directory, "*.html")):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Title
    title_tag = soup.find('h1', class_='entry-title')
    title = title_tag.get_text(strip=True) if title_tag else "No Title Found"

    # The main content area
    content_div = soup.find('div', class_='entry-content', itemprop='text')

    # Extract descriptive paragraphs before ingredients/directions
    # We'll consider all <p> tags that appear before the table and before "Directions:"
    paragraphs = []
    if content_div:
        # Get all paragraphs
        p_tags = content_div.find_all('p')
        for p in p_tags:
            text = p.get_text(strip=True)
            if not text:
                continue
            # If we hit "Directions:" we stop collecting paragraphs
            if "Directions:" in text:
                break
            # If this paragraph is right before the table and isn't directions, keep it
            paragraphs.append(text)

    # Extract ingredients from the table
    ingredients = []
    if content_div:
        table = content_div.find('table')
        if table:
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                # Expecting 3 columns: quantity, unit, name
                if len(tds) == 3:
                    qty = tds[0].get_text(strip=True)
                    unit = tds[1].get_text(strip=True)
                    name = tds[2].get_text(strip=True)
                    ingredients.append(f"{qty} {unit} {name}")

    # Extract directions
    directions = []
    if content_div:
        # Find the "Directions:" text
        directions_heading = content_div.find('strong', text=lambda t: t and "Directions:" in t)
        if directions_heading:
            # The directions might be in the next <ul> after the paragraph containing "Directions:"
            parent_p = directions_heading.find_parent('p')
            if parent_p:
                next_ul = parent_p.find_next_sibling('ul')
                if next_ul:
                    for li in next_ul.find_all('li'):
                        step = li.get_text(strip=True)
                        if step:
                            directions.append(step)

    # Create a corresponding .txt filename
    base_name = os.path.splitext(html_file)[0]
    txt_file = base_name + ".txt"

    with open(txt_file, "w", encoding="utf-8") as out:
        out.write(f"Title: {title}\n\n")
        
        if paragraphs:
            for p in paragraphs:
                out.write(p + "\n\n")

        out.write("Ingredients:\n")
        for ingr in ingredients:
            out.write("- " + ingr + "\n")
        
        out.write("\nDirections:\n")
        if directions:
            for step in directions:
                out.write("- " + step + "\n")
        else:
            out.write("No directions found.\n")

    print(f"Processed {html_file} -> {txt_file}")
