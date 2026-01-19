# Image Creation Template

A Python-based notification screenshot generator that creates mobile notification mockups with customizable templates.

## Features

- Multiple notification templates (4 templates included)
- Customizable text, icons, and banner images
- Automatic text wrapping and truncation
- Rounded corners and masking support
- Aspect-preserving image cropping
- Dynamic layout with card expansion

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. **Download the project**
   
   **Option A: Using Git (if you have Git installed)**
   ```bash
   git clone https://github.com/hbtuabhishek/image-creation-template.git
   cd image-creation-template
   ```
   
   **Option B: Download ZIP (no Git required)**
   - Go to https://github.com/hbtuabhishek/image-creation-template
   - Click the green "Code" button
   - Select "Download ZIP"
   - Extract the ZIP file
   - Open terminal/command prompt and navigate to the extracted folder:
     ```bash
     cd path/to/image-creation-template
     ```

2. **Install dependencies**
   ```bash
   pip install Pillow
   ```
   
   Or if using Python 3.13 specifically:
   ```bash
   pip3.13 install Pillow
   ```

## Usage

### Generate a Single Template

```bash
python3 generateSS.py <template_id> <date_time> <title> <description> <app_name> <icon_file> <banner_file>
```

**Example:**
```bash
python3 generateSS.py 1 "Jan 15, 12:50" "Breaking News" "This is a test notification" "My App" "assets/icons/bell-icon.png" "assets/banners/sample.jpg"
```

**Parameters:**
- `template_id`: Template number (1-4)
- `date_time`: Display date/time (e.g., "Jan 15, 12:50")
- `title`: Notification title
- `description`: Notification description
- `app_name`: Application name
- `icon_file`: Path to app icon image
- `banner_file`: Path to banner image

### Generate All Templates

To generate all 4 templates at once with predefined content:

```bash
python3 generate_all.py
```

This will create 4 images in the `output/` directory:
- `generated_t1.png`
- `generated_t2.png`
- `generated_t3.png`
- `generated_t4.png`

## Project Structure

```
image-creation-template/
├── assets/
│   ├── backgrounds/     # Background images
│   ├── banners/         # Banner images
│   ├── fonts/           # Font files
│   └── icons/           # Icon images
├── config/
│   └── templates.json   # Template configurations
├── output/              # Generated images (created automatically)
├── generateSS.py        # Main generation script
├── generate_all.py      # Batch generation script
└── README.md
```

## Customization

### Modifying Templates

Edit `config/templates.json` to customize:
- Canvas size
- Background colors/images
- Rectangle positions and sizes
- Icon positions
- Banner dimensions
- Text positions, fonts, and colors

### Adding New Images

Place your images in the appropriate directories:
- App icons: `assets/icons/`
- Banner images: `assets/banners/`
- Background images: `assets/backgrounds/`

## Output

Generated images are saved to the `output/` directory with the naming convention:
- `generated_t{template_id}.png`

## Troubleshooting

**Issue: "ModuleNotFoundError: No module named 'PIL'"**
- Solution: Install Pillow using `pip install Pillow`

**Issue: "FileNotFoundError" for images**
- Solution: Ensure image paths are correct and files exist in the specified directories

**Issue: Font rendering issues**
- Solution: Ensure font files exist in `assets/fonts/` directory

## License

This project is open source and available for personal and commercial use.

## Contributing

Feel free to submit issues and pull requests for improvements.
