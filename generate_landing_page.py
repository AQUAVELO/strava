#!/usr/bin/env python3
"""
Landing Page Generator CLI
Generate promotional landing pages from the command line.
"""

import argparse
import json
import base64
import colorsys
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def parse_arguments():
    """Parse CLI arguments with argparse"""
    parser = argparse.ArgumentParser(
        description="Generate promotional landing pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python generate_landing_page.py \\
    --url "https://myapp.com" \\
    --title "MyApp" \\
    --headline "Work Smarter, Not Harder" \\
    --description "Join thousands of professionals"

  # With features
  python generate_landing_page.py \\
    --url "https://myapp.com" \\
    --title "MyApp" \\
    --headline "Amazing Product" \\
    --description "Transform your workflow" \\
    --features "Fast,Secure,Reliable"

  # Using config file
  python generate_landing_page.py --config landing_config.json
        """
    )

    # Required arguments
    parser.add_argument('--url',
                       help='Target URL (product/page being promoted)')
    parser.add_argument('--title',
                       help='HTML page title (appears in browser tab)')
    parser.add_argument('--headline',
                       help='Main hero headline')
    parser.add_argument('--description',
                       help='Supporting description/pitch')

    # Optional arguments
    parser.add_argument('--cta',
                       default='Learn More',
                       help='Call-to-action button text (default: "Learn More")')
    parser.add_argument('--output',
                       default='landing_page.html',
                       help='Output filename (default: landing_page.html)')
    parser.add_argument('--features',
                       help='Comma-separated features list')
    parser.add_argument('--logo',
                       help='Path to logo image (will be embedded as base64)')
    parser.add_argument('--gradient-start',
                       default='#0f0c29',
                       help='Gradient start color (default: #0f0c29)')
    parser.add_argument('--gradient-mid',
                       default='#302b63',
                       help='Gradient middle color (default: #302b63)')
    parser.add_argument('--gradient-end',
                       default='#24243e',
                       help='Gradient end color (default: #24243e)')
    parser.add_argument('--accent-color',
                       default='#667eea',
                       help='Primary accent color for buttons/links (default: #667eea)')
    parser.add_argument('--config',
                       help='Path to JSON config file')

    return parser.parse_args()


def load_config_file(config_path):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def encode_logo_base64(logo_path):
    """Convert logo image to base64 for embedding"""
    try:
        logo_file = Path(logo_path)

        if not logo_file.exists():
            print(f"Error: Logo file not found: {logo_path}")
            sys.exit(1)

        # Check file size and warn if large
        file_size = logo_file.stat().st_size
        if file_size > 100 * 1024:  # 100KB
            print(f"Warning: Logo file is large ({file_size / 1024:.1f}KB). This will increase HTML file size.")
            print("Consider using a smaller image or SVG format for better performance.")

        with open(logo_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            return encoded

    except Exception as e:
        print(f"Error encoding logo: {e}")
        sys.exit(1)


def validate_color(color):
    """Validate hex color codes"""
    if not color:
        return False

    if not color.startswith('#'):
        return False

    # Remove the # and check length
    hex_color = color[1:]
    if len(hex_color) not in [3, 6]:
        return False

    # Check if all characters are valid hex
    try:
        int(hex_color, 16)
        return True
    except ValueError:
        return False


def darken_color(hex_color, factor=0.7):
    """Darken a hex color by the given factor"""
    # Remove the # if present
    hex_color = hex_color.lstrip('#')

    # Convert to RGB
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])

    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Convert to HSV, darken, convert back
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    v = v * factor

    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def merge_config(args, config):
    """Merge CLI args with config file (args take precedence)"""
    # Start with config file values
    merged = config.copy()

    # Override with CLI arguments (if provided)
    arg_dict = vars(args)
    for key, value in arg_dict.items():
        # Skip None values (not provided via CLI)
        if value is not None:
            # Convert dash to underscore for consistency
            key_normalized = key.replace('-', '_')
            merged[key_normalized] = value

    return merged


def render_template(template_vars):
    """Render Jinja2 template with variables"""
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        template_dir = script_dir / 'templates'

        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('landing_page_template.html')

        return template.render(**template_vars)

    except Exception as e:
        print(f"Error rendering template: {e}")
        sys.exit(1)


def write_output(html_content, output_path):
    """Write generated HTML to file"""
    try:
        output_file = Path(output_path)

        # Create parent directories if they don't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write the HTML content
        output_file.write_text(html_content, encoding='utf-8')

        return output_file.absolute()

    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


def main():
    """Main execution flow"""
    args = parse_arguments()

    # Load config file if provided
    config = {}
    if args.config:
        config = load_config_file(args.config)

    # Merge configuration (CLI args override config file)
    final_config = merge_config(args, config)

    # Validate required fields
    required_fields = ['url', 'title', 'headline', 'description']
    missing_fields = [field for field in required_fields if not final_config.get(field)]

    if missing_fields:
        print(f"Error: Missing required fields: {', '.join(missing_fields)}")
        print("Use --help for usage information")
        sys.exit(1)

    # Validate colors
    colors_to_validate = ['gradient_start', 'gradient_mid', 'gradient_end', 'accent_color']
    for color_key in colors_to_validate:
        if color_key in final_config and not validate_color(final_config[color_key]):
            print(f"Error: Invalid color format for {color_key}: {final_config[color_key]}")
            print("Colors must be in hex format (e.g., #667eea or #fff)")
            sys.exit(1)

    # Process logo if provided
    if final_config.get('logo'):
        final_config['logo_base64'] = encode_logo_base64(final_config['logo'])

    # Process features (convert string to list if needed)
    if final_config.get('features'):
        if isinstance(final_config['features'], str):
            final_config['features'] = [f.strip() for f in final_config['features'].split(',')]

    # Generate darker accent color for gradient
    accent_color = final_config.get('accent_color', '#667eea')
    final_config['accent_color_dark'] = darken_color(accent_color, 0.7)

    # Prepare template variables
    template_vars = {
        'page_title': final_config['title'],
        'headline': final_config['headline'],
        'description': final_config['description'],
        'target_url': final_config['url'],
        'cta_text': final_config.get('cta', 'Learn More'),
        'gradient_start': final_config.get('gradient_start', '#0f0c29'),
        'gradient_mid': final_config.get('gradient_mid', '#302b63'),
        'gradient_end': final_config.get('gradient_end', '#24243e'),
        'accent_color': accent_color,
        'accent_color_dark': final_config['accent_color_dark'],
        'features': final_config.get('features'),
        'logo_base64': final_config.get('logo_base64'),
    }

    # Render template
    print("Generating landing page...")
    html = render_template(template_vars)

    # Write output file
    output_file = write_output(html, final_config.get('output', 'landing_page.html'))

    # Success message
    print(f"✓ Landing page generated successfully!")
    print(f"  Output: {output_file}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f}KB")
    print(f"\nOpen in browser:")
    print(f"  file://{output_file}")


if __name__ == '__main__':
    main()
