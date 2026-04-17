"""
image_processor.py — Draws color-coded bounding boxes on the image.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def annotate_image(image_path: str, paragraphs: list, output_path: str) -> str:
    """
    Draw colored bounding boxes on the image, color-coded by language.
    Saves annotated image to output_path and returns output_path.
    """
    img = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for para in paragraphs:
        color_hex = para.get("lang", {}).get("color", "#6366f1")
        rgb = _hex_to_rgb(color_hex)
        x, y, w, h = para["x"], para["y"], para["w"], para["h"]

        # Draw semi-transparent fill
        draw.rectangle(
            [x, y, x + w, y + h],
            fill=(*rgb, 40),
            outline=(*rgb, 220),
            width=2
        )

        # Language label above box
        lang_name = para.get("lang", {}).get("name", "")
        if lang_name and lang_name != "Unknown":
            try:
                font = ImageFont.truetype("arial.ttf", max(10, min(h // 3, 14)))
            except Exception:
                font = ImageFont.load_default()

            # Label background
            bbox = draw.textbbox((x, y - 18), lang_name, font=font)
            draw.rectangle(bbox, fill=(*rgb, 200))
            draw.text((x, y - 18), lang_name, fill=(255, 255, 255, 255), font=font)

    # Merge overlay with original
    annotated = Image.alpha_composite(img, overlay).convert("RGB")
    annotated.save(output_path, "JPEG", quality=92)
    return output_path


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert #rrggbb to (r, g, b)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
