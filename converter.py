import os
import re
from pathlib import Path

# CSS and HTML template (previously defined in styles.css and the script)
# I will keep the CSS reference to use the existing styles.css
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eko-Kieszonkowe - Prezentacja</title>
    <link rel="stylesheet" href="css/styles.css">
    <style>
        .slide-nav {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
            display: flex;
            gap: 1rem;
        }}
        .slide-nav button {{
            background: #000;
            color: #fff;
            border: none;
            padding: 1rem 1.5rem;
            font-family: 'Inter', sans-serif;
            font-weight: 900;
            cursor: pointer;
            text-transform: uppercase;
        }}
        .infografika {{
            background: #fcfcfc;
            border: 2px solid #000;
            padding: 2rem;
            margin: 2rem 0;
            font-weight: 900;
            font-size: 1.4rem;
            text-transform: uppercase;
            letter-spacing: -0.02em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            text-align: left;
            font-size: 1.1rem;
        }}
        th {{
            background: #000;
            color: #fff;
            padding: 1rem;
            text-transform: uppercase;
            font-weight: 900;
        }}
        td {{
            padding: 1rem;
            border-bottom: 2px solid #000;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="presentation">
        {slides_html}
    </div>

    <div class="slide-nav">
        <button onclick="prevSlide()">Prev</button>
        <button onclick="nextSlide()">Next</button>
    </div>

    <script>
        const observerOptions = {{
            threshold: 0.5
        }};

        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                }} else {{
                    entry.target.classList.remove('visible');
                }}
            }});
        }}, observerOptions);

        document.querySelectorAll('.slide').forEach(slide => observer.observe(slide));

        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');

        function nextSlide() {{
            if (currentSlide < slides.length - 1) {{
                currentSlide++;
                slides[currentSlide].scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        function prevSlide() {{
            if (currentSlide > 0) {{
                currentSlide--;
                slides[currentSlide].scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === ' ') nextSlide();
            if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') prevSlide();
        }});
    </script>
</body>
</html>
"""

def parse_markdown_table(rows):
    if not rows:
        return ""
    
    html = "<table><thead><tr>"
    headers = [cell.strip() for cell in rows[0].split("|") if cell.strip()]
    for header in headers:
        html += f"<th>{header}</th>"
    html += "</tr></thead><tbody>"
    
    for row in rows[2:]: # skip header and separator
        cells = [cell.strip() for cell in row.split("|") if cell.strip()]
        if not cells: continue
        html += "<tr>"
        for cell in cells:
            html += f"<td>{cell}</td>"
        html += "</tr>"
    
    html += "</tbody></table>"
    return html

def parse_feedpages(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by Slajd X:
    slide_blocks = re.split(r'Slajd \d+:', content)[1:]
    processed_slides = []
    
    # Titles are the first part of the split before the next slide string if we used a more complex split
    # For now, let's just use the current split and identify titles manually if needed.
    # Re-reading: Slajd 1: Koncept Główny - EKO KIESZONKOWE -> Koncept Główny - EKO KIESZONKOWE is the title.
    
    titles = re.findall(r'Slajd \d+: (.*)', content)
    
    for i, block in enumerate(slide_blocks):
        slide = {"title": titles[i].strip(), "header": "", "content_parts": []}
        lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
        
        in_table = False
        table_rows = []
        
        for line in lines:
            if line.startswith("Nagłówek:"):
                slide["header"] = line.replace("Nagłówek:", "").strip()
            elif line.startswith("Infografika:"):
                # If we were in a table, close it
                if table_rows:
                    slide["content_parts"].append({"type": "table", "content": table_rows})
                    table_rows = []
                    in_table = False
                slide["content_parts"].append({"type": "info_title", "content": line.replace("Infografika:", "").strip()})
            elif line.startswith("➡️") or line.startswith("👧") or line.startswith("👦") or line.startswith("1️⃣"):
                 slide["content_parts"].append({"type": "infographic", "content": line})
            elif line.startswith("|"):
                in_table = True
                table_rows.append(line)
            elif in_table and line.startswith("|") == False: # End of table
                slide["content_parts"].append({"type": "table", "content": table_rows})
                table_rows = []
                in_table = False
            else:
                if in_table:
                    table_rows.append(line)
                else:
                    # Just normal paragraph
                    slide["content_parts"].append({"type": "text", "content": line})
        
        # Final table check
        if table_rows:
            slide["content_parts"].append({"type": "table", "content": table_rows})
            
        processed_slides.append(slide)
    
    return processed_slides

def generate_slide_html(slide):
    html = '<section class="slide">'
    html += '<div class="slide-content">'
    
    # Header area
    if slide["header"]:
        html += f'<h2>{slide["header"]}</h2>'
    
    html += f'<h1>{slide["title"]}</h1>'
    
    for part in slide["content_parts"]:
        if part["type"] == "text":
            html += f'<p>{part["content"]}</p>'
        elif part["type"] == "info_title":
            html += f'<h3>— {part["content"]} —</h3>'
        elif part["type"] == "infographic":
            html += f'<div class="infografika">{part["content"]}</div>'
        elif part["type"] == "table":
            html += parse_markdown_table(part["content"])
            
    html += '</div></section>'
    return html

def main():
    feedpages_path = "feedpages.md"
    if not os.path.exists(feedpages_path):
        feedpages_path = "c:/Users/marek/Documents/source/xxm/feedpages.md"
        
    slides_data = parse_feedpages(feedpages_path)
    slides_html = "".join([generate_slide_html(s) for s in slides_data])
    final_html = HTML_TEMPLATE.format(slides_html=slides_html)
    
    output_path = Path("c:/Users/marek/Documents/source/xxm/index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    main()
