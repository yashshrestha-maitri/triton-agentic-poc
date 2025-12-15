#!/usr/bin/env python3
"""
Convert Markdown to PDF with Mermaid diagram support.
Requires: pip install markdown2 weasyprint pymermaid
"""

import sys
import subprocess
import re
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required = ['markdown2', 'weasyprint']
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

def convert_md_to_pdf(input_file, output_file=None):
    """Convert markdown file to PDF."""
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

    # Convert markdown to HTML
    print("🔄 Converting markdown to HTML...")
    html_body = markdown2.markdown(
        md_content,
        extras=['fenced-code-blocks', 'tables', 'header-ids']
    )

    # Wrap in HTML with Mermaid support
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
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
            }}
            th, td {{
                border: 1px solid #dfe2e5;
                padding: 6px 13px;
            }}
            th {{
                background-color: #f6f8fa;
                font-weight: 600;
            }}
            .mermaid {{
                text-align: center;
                margin: 20px 0;
                padding: 10px;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                background-color: #f6f8fa;
            }}
        </style>
    </head>
    <body>
        {html_body}
        <p style="page-break-after: always;"></p>
        <div style="text-align: center; color: #666; margin-top: 50px;">
            <small>⚠️ Mermaid diagrams are shown as code blocks in this PDF.<br>
            For interactive diagrams, use VS Code Markdown Preview Enhanced or visit the HTML version.</small>
        </div>
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
    print(f"\n📊 Note: Mermaid diagrams are rendered as code blocks.")
    print(f"   For best diagram rendering, use:")
    print(f"   - VS Code: Markdown Preview Enhanced → Export PDF")
    print(f"   - Node.js: md-to-pdf (npm install -g md-to-pdf)")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_to_pdf.py <input.md> [output.pdf]")
        print("\nExample:")
        print("  python convert_to_pdf.py RESEARCH_AGENT_FLOW.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_md_to_pdf(input_file, output_file)
