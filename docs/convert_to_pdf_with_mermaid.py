
#!/usr/bin/env python3
"""
Convert Markdown to PDF with Mermaid diagrams rendered as images.
Uses mermaid.ink API to render diagrams.
Requires: pip install markdown2 weasyprint requests
"""

import sys
import re
import base64
import zlib
import requests
from pathlib import Path
from urllib.parse import quote

def check_dependencies():
    """Check if required packages are installed."""
    required = ['markdown2', 'weasyprint', 'requests']
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    return True

def encode_mermaid(mermaid_code):
    """Encode Mermaid code for mermaid.ink API."""
    # Remove extra whitespace and encode
    cleaned = mermaid_code.strip()
    # Encode to UTF-8, compress with zlib, then base64
    compressed = zlib.compress(cleaned.encode('utf-8'), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
    return encoded

def mermaid_to_image_url(mermaid_code):
    """Convert Mermaid code to image URL using mermaid.ink."""
    try:
        encoded = encode_mermaid(mermaid_code)
        # Use SVG format for better quality
        url = f"https://mermaid.ink/svg/{encoded}"
        return url
    except Exception as e:
        print(f"⚠️  Warning: Failed to encode Mermaid diagram: {e}")
        return None

def process_mermaid_diagrams(md_content):
    """Replace Mermaid code blocks with image tags."""
    # Pattern to match mermaid code blocks
    pattern = r'```mermaid\s*\n(.*?)```'

    diagram_count = 0

    def replace_with_image(match):
        nonlocal diagram_count
        diagram_count += 1
        mermaid_code = match.group(1)

        print(f"📊 Processing Mermaid diagram {diagram_count}...")

        # Get image URL
        image_url = mermaid_to_image_url(mermaid_code)

        if image_url:
            # Return HTML img tag with larger size
            return f'\n\n<div class="mermaid-diagram"><img src="{image_url}" alt="Mermaid Diagram {diagram_count}" style="width: 100%; height: auto; min-height: 400px;"/></div>\n\n'
        else:
            # Fallback to code block
            return f'\n\n<pre class="mermaid-fallback">```mermaid\n{mermaid_code}\n```</pre>\n\n'

    processed = re.sub(pattern, replace_with_image, md_content, flags=re.DOTALL)

    if diagram_count > 0:
        print(f"✅ Processed {diagram_count} Mermaid diagram(s)")

    return processed

def convert_md_to_pdf(input_file, output_file=None):
    """Convert markdown file to PDF with Mermaid diagrams rendered."""
    if not check_dependencies():
        sys.exit(1)

    import markdown2
    from weasyprint import HTML, CSS

    # Read markdown file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ File not found: {input_file}")
        sys.exit(1)

    print(f"📄 Reading {input_file}...")
    md_content = input_path.read_text(encoding='utf-8')

    # Process Mermaid diagrams
    print("🔄 Processing Mermaid diagrams...")
    processed_content = process_mermaid_diagrams(md_content)

    # Convert markdown to HTML
    print("🔄 Converting markdown to HTML...")
    html_body = markdown2.markdown(
        processed_content,
        extras=['fenced-code-blocks', 'tables', 'header-ids']
    )

    # Wrap in HTML with styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{input_path.stem}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
                line-height: 1.6;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                color: #24292e;
            }}
            h1, h2, h3, h4, h5, h6 {{
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
                page-break-after: avoid;
            }}
            h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
            h3 {{ font-size: 1.25em; }}
            code {{
                background-color: #f6f8fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 85%;
            }}
            pre {{
                background-color: #f6f8fa;
                padding: 16px;
                border-radius: 6px;
                overflow: auto;
                page-break-inside: avoid;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
                page-break-inside: avoid;
            }}
            th, td {{
                border: 1px solid #dfe2e5;
                padding: 6px 13px;
            }}
            th {{
                background-color: #f6f8fa;
                font-weight: 600;
            }}
            .mermaid-diagram {{
                text-align: center;
                margin: 20px 0;
                padding: 10px;
                page-break-inside: avoid;
            }}
            .mermaid-diagram img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                background-color: white;
            }}
            .mermaid-fallback {{
                background-color: #fff3cd;
                border: 1px solid #ffc107;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    # Determine output filename
    if output_file is None:
        output_file = input_path.with_suffix('.pdf')

    # Convert HTML to PDF
    print(f"📄 Generating PDF: {output_file}...")
    HTML(string=html_content).write_pdf(
        output_file,
        stylesheets=[CSS(string='@page { size: A4; margin: 2cm; }')]
    )

    print(f"✅ PDF created successfully: {output_file}")
    print(f"📊 Mermaid diagrams rendered as images via mermaid.ink")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_to_pdf_with_mermaid.py <input.md> [output.pdf]")
        print("\nExample:")
        print("  python convert_to_pdf_with_mermaid.py RESEARCH_AGENT_FLOW.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_md_to_pdf(input_file, output_file)
