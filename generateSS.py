import os
import json
import sys
from PIL import Image, ImageDraw, ImageFont

class ImageGenerator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.defaults = self.config['defaults']

    def get_font(self, size, bold=False, custom_path=None):
        if custom_path:
            font_path = custom_path
        else:
            font_path = self.defaults['bold_font_path'] if bold else self.defaults['font_path']
        
        try:
            return ImageFont.truetype(font_path, size)
        except IOError:
            # Try fallback if custom fails
            try:
                return ImageFont.truetype(self.defaults['font_path'], size)
            except IOError:
                return ImageFont.load_default()

    def wrap_text(self, text, font, max_width):
        lines = []
        words = text.split()
        while words:
            line = words.pop(0)
            while words:
                test_line = line + ' ' + words[0]
                bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                if width <= max_width:
                    line = test_line
                    words.pop(0)
                else:
                    break
            lines.append(line)
        return lines

    def generate(self, template_id, date_time, title, description, app_name, icon_file, banner_file, output_path):
        template = self.config['templates'].get(str(template_id))
        if not template:
            print(f"Error: Template {template_id} not found.")
            return

        canvas_size = tuple(template['canvas_size'])
        bg_config = template.get('background', "#000000")

        if bg_config.startswith('#'):
            img = Image.new('RGBA', canvas_size, color=bg_config)
        else:
            try:
                img = Image.open(bg_config).convert('RGBA').resize(canvas_size, Image.Resampling.LANCZOS)
            except FileNotFoundError:
                img = Image.new('RGBA', canvas_size, color="#CCCCCC")

        draw = ImageDraw.Draw(img)
        
        # Parse date_time if possible (e.g., "Jan 15, 12:50")
        display_date = date_time
        display_clock = ""
        if ',' in date_time:
            parts = date_time.rsplit(',', 1)
            display_date = parts[0].strip()
            display_clock = parts[1].strip()
        elif ' ' in date_time:
            parts = date_time.rsplit(' ', 1)
            display_date = parts[0].strip()
            display_clock = parts[1].strip()

        # Build data dictionary for replacement
        data = {
            "app_name": app_name,
            "title": title,
            "description": description,
            "date_time": date_time,
            "display_date": display_date,
            "display_clock": display_clock,
            "icon_path": icon_file,
            "banner_path": banner_file
        }

        # --- 1. UNIFIED PRE-CALCULATE LAYOUT ---
        all_elements = []
        
        # Collect everything
        if 'rectangles' in template:
            for i, rect in enumerate(template['rectangles']):
                all_elements.append({'type': 'rect', 'id': i, 'cfg': rect, 'pos': list(rect['pos'])})
        
        if 'icons' in template:
            for key, icon in template['icons'].items():
                all_elements.append({'type': 'icon', 'id': key, 'cfg': icon, 'pos': list(icon['pos'])})
        
        if 'banners' in template:
            for key, banner in template['banners'].items():
                all_elements.append({'type': 'banner', 'id': key, 'cfg': banner, 'pos': list(banner['pos'])})
        
        if 'texts' in template:
            for key, text_cfg in template['texts'].items():
                all_elements.append({'type': 'text', 'id': key, 'cfg': text_cfg, 'pos': list(text_cfg['pos'])})

        # Sort by Y position to handle top-to-bottom shifting
        all_elements.sort(key=lambda x: x['pos'][1])

        y_shift = 0
        content_bottom = 0
        layouts = {'rect': {}, 'icon': {}, 'banner': {}, 'text': {}}

        # We'll use this to resolve relative positions
        resolved_elements = {}

        for el in all_elements:
            etype = el['type']
            eid = el['id']
            cfg = el['cfg']
            pos = el['pos']
            
            # 1. Apply vertical shift for card elements
            if pos[1] >= 175:
                pos[1] += y_shift

            # 2. Resolve relative horizontal positioning
            x = pos[0]
            if cfg.get('relative_to_x'):
                target_id = cfg['relative_to_x']
                if target_id in resolved_elements:
                    target = resolved_elements[target_id]
                    spacing = cfg.get('spacing', 10)
                    x = target['pos'][0] + target['w'] + spacing
            
            # Resolve relative vertical centering if needed (for icons/text alignment)
            y = pos[1]
            if cfg.get('align_y_to'):
                target_id = cfg['align_y_to']
                if target_id in resolved_elements:
                    target = resolved_elements[target_id]
                    # Center self vertically against target
                    self_h = cfg['size'][1] if 'size' in cfg else cfg.get('font_size', 16)
                    y = target['pos'][1] + (target['h'] - self_h) // 2
            
            pos = [x, y]
            h = 0
            w = 0

            if etype == 'rect':
                w = cfg['size'][0]
                h = cfg['size'][1]
                layouts['rect'][eid] = {'pos': pos, 'size': list(cfg['size'])}
            
            elif etype == 'icon':
                w = cfg['size'][0]
                h = cfg['size'][1]
                path = data.get(f"{eid}_path", cfg.get('path'))
                layouts['icon'][eid] = {'pos': pos, 'path': path}
            
            elif etype == 'banner':
                path = data.get(f"{eid}_path", cfg.get('path'))
                if path:
                    w = cfg['size'][0]
                    h = cfg['size'][1]
                    layouts['banner'][eid] = {'pos': pos, 'path': path}
            
            elif etype == 'text':
                content = data.get(eid, cfg.get('content', ""))
                if content:
                    font = self.get_font(cfg['font_size'], cfg.get('bold', False), cfg.get('font_path'))
                    max_width = cfg.get('max_width', canvas_size[0] - pos[0] * 2)
                    lines = self.wrap_text(content, font, max_width)
                    
                    # --- Truncate to max 2 lines with ellipsis ---
                    if eid in ['title', 'description'] and len(lines) > 2:
                        lines = lines[:2]
                        last_line = lines[-1]
                        while last_line:
                            bbox = draw.textbbox((0, 0), last_line + "...", font=font)
                            if (bbox[2] - bbox[0]) <= max_width:
                                lines[-1] = last_line + "..."
                                break
                            last_line = last_line[:-1]
                    # ---------------------------------------------
                    
                    line_spacing = cfg.get('line_spacing', 10)
                    line_h = 0
                    max_line_w = 0
                    for line in lines:
                        bbox = draw.textbbox((0, 0), line, font=font)
                        line_h = max(line_h, bbox[3] - bbox[1])
                        max_line_w = max(max_line_w, bbox[2] - bbox[0])
                        h += (bbox[3] - bbox[1]) + line_spacing
                    
                    w = max_line_w
                    layouts['text'][eid] = {'pos': pos, 'lines': lines, 'font': font, 'h': h, 'w': w}
                    
                    # Handle centering (re-calculate x if centered)
                    if cfg.get('center'):
                        pos[0] = (canvas_size[0] - w) // 2
                    elif cfg.get('center_on_x'):
                        target_x, target_w = cfg['center_on_x']
                        pos[0] = target_x + (target_w - w) // 2

                    # If this is a growing text field, add its expansion to the shift
                    if eid in ['title', 'description'] and len(lines) > 1:
                        standard_h = line_h + line_spacing
                        y_shift += (h - standard_h)

            # Store in resolved for subsequent elements
            resolved_elements[eid] = {'pos': pos, 'w': w, 'h': h}

            # Update area content bottom for card expansion
            if pos[1] >= 175:
                content_bottom = max(content_bottom, pos[1] + h)

        # Final pass for white card expansion
        if 'rect' in layouts:
            for rid, rect in layouts['rect'].items():
                cfg = next(r for i, r in enumerate(template['rectangles']) if i == rid)
                if cfg.get('color', '').upper() == '#FFFFFF' and content_bottom > (rect['pos'][1] + rect['size'][1]):
                    rect['size'][1] = content_bottom - rect['pos'][1]

        # --- 2. DRAW EVERYTHING IN ORDER (PAINTER'S ALGORITHM) ---

        # A. Rectangles
        if 'rectangles' in template:
            for rid, layout in layouts['rect'].items():
                cfg = template['rectangles'][rid]
                pos = layout['pos']
                size = layout['size']
                draw.rounded_rectangle(
                    (pos[0], pos[1], pos[0] + size[0], pos[1] + size[1]),
                    radius=cfg.get('radius', 0),
                    fill=cfg.get('color', "#FFFFFF")
                )

        # B. Icons
        if 'icons' in template:
            for iid, layout in layouts['icon'].items():
                cfg = template['icons'][iid]
                if not layout['path']: continue
                try:
                    icon = Image.open(layout['path']).convert('RGBA').resize(tuple(cfg['size']), Image.Resampling.LANCZOS)
                    if cfg.get('rounded'):
                        mask = Image.new('L', icon.size, 0)
                        mask_draw = ImageDraw.Draw(mask)
                        mask_draw.ellipse((0, 0) + icon.size, fill=255)
                        icon.putalpha(mask)
                    img.paste(icon, tuple(layout['pos']), icon)
                except Exception as e: print(f"Icon error: {e}")

        # C. Banners
        if 'banners' in template:
            for bid, layout in layouts['banner'].items():
                cfg = template['banners'][bid]
                if not layout['path']: continue
                try:
                    banner = Image.open(layout['path']).convert('RGBA').resize(tuple(cfg['size']), Image.Resampling.LANCZOS)
                    if cfg.get('radius', 0) > 0:
                        mask = Image.new('L', banner.size, 0)
                        mask_draw = ImageDraw.Draw(mask)
                        mask_draw.rounded_rectangle((0, 0) + banner.size, radius=cfg['radius'], fill=255)
                        banner.putalpha(mask)
                    img.paste(banner, tuple(layout['pos']), banner)
                except Exception as e: print(f"Banner error: {e}")

        # D. Texts
        for tid, layout in layouts['text'].items():
            cfg = template['texts'][tid]
            y_offset = layout['pos'][1]
            x = layout['pos'][0]
            for line in layout['lines']:
                draw.text((x, y_offset), line, fill=cfg['color'], font=layout['font'])
                bbox = draw.textbbox((0, 0), line, font=layout['font'])
                y_offset += (bbox[3] - bbox[1]) + cfg.get('line_spacing', 10)

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        final_path = os.path.join(output_dir, output_path)
        img.convert('RGB').save(final_path)
        print(f"Successfully generated: {final_path}")

if __name__ == "__main__":
    if len(sys.argv) < 8:
        print("Usage: python3.15 generateSS.py <Template ID> <Date Time> <Title> <Description> <AppName> <IconFile> <BannerFile>")
        sys.exit(1)

    template_id = sys.argv[1]
    date_time = sys.argv[2]
    title = sys.argv[3]
    description = sys.argv[4]
    app_name = sys.argv[5]
    icon_file = sys.argv[6]
    banner_file = sys.argv[7]

    gen = ImageGenerator('config/templates.json')
    output_filename = f"generated_t{template_id}.png"
    gen.generate(template_id, date_time, title, description, app_name, icon_file, banner_file, output_filename)
