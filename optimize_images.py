"""
Script d'optimisation des images pour le projet Nina Carducci
- Convertit les images en WebP
- Compresse les images
- Redimensionne les images selon leur type
- Conserve les originaux intacts
- Affiche un résumé des gains obtenus

Utilisation :
    1. Placer ce script à la racine du projet (là où se trouve le dossier assets/)
    2. Installer Pillow : pip install Pillow
    3. Lancer : py optimize_images.py
"""

from PIL import Image
import os

# ── Configuration ──────────────────────────────────────────────────────────────
IMAGES_DIR = "assets/images"       # Dossier source
OUTPUT_DIR = "assets/images-webp"  # Dossier de sortie (créé automatiquement)
QUALITY = 80                        # Qualité WebP (0-100), 80 est un bon compromis
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")  # Extensions à traiter

# Largeur max par dossier (hauteur calculée automatiquement pour garder les proportions)
MAX_WIDTHS = {
    "slider":     2000,
    "gallery":     900,
    "portraits":   900,
    "concerts":    900,
    "entreprise":  900,
    "mariage":     900,
    "default":     900,
}

# Largeur max pour les images à la racine (nina.png, camera.png, instagram.png)
ROOT_IMAGES = {
    "nina":       600,
    "camera":     500,
    "instagram":   40,
}
# ───────────────────────────────────────────────────────────────────────────────


def format_size(size_bytes):
    if size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.1f} Mo"
    return f"{size_bytes / 1_000:.1f} Ko"


def get_max_width(filepath, filename):
    base_name = os.path.splitext(filename)[0].lower()
    for key, width in ROOT_IMAGES.items():
        if key in base_name:
            return width
    for folder, width in MAX_WIDTHS.items():
        if folder in filepath.lower():
            return width
    return MAX_WIDTHS["default"]


def resize_image(img, max_width):
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)
    return img


def optimize_images():
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ Dossier introuvable : {IMAGES_DIR}")
        print("Lancer ce script depuis la racine du projet.")
        return

    total_original = 0
    total_optimized = 0
    count = 0
    errors = []

    print(f"📁 Dossier source  : {IMAGES_DIR}")
    print(f"📁 Dossier sortie  : {OUTPUT_DIR}")
    print(f"🎚  Qualité WebP    : {QUALITY}")
    print("-" * 60)

    for root, dirs, files in os.walk(IMAGES_DIR):
        for filename in files:
            if not filename.lower().endswith(EXTENSIONS):
                continue

            input_path = os.path.join(root, filename)
            relative_path = os.path.relpath(root, IMAGES_DIR)
            output_folder = os.path.join(OUTPUT_DIR, relative_path)
            os.makedirs(output_folder, exist_ok=True)

            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, base_name + ".webp")

            try:
                original_size = os.path.getsize(input_path)
                total_original += original_size

                with Image.open(input_path) as img:
                    original_dims = f"{img.width}x{img.height}"

                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")

                    max_width = get_max_width(root, filename)
                    img = resize_image(img, max_width)
                    new_dims = f"{img.width}x{img.height}"

                    img.save(output_path, "WEBP", quality=QUALITY, method=6)

                optimized_size = os.path.getsize(output_path)
                total_optimized += optimized_size
                gain = original_size - optimized_size
                gain_pct = (gain / original_size) * 100

                dims_info = f"{original_dims} → {new_dims}" if original_dims != new_dims else original_dims

                print(f"✅ {filename}")
                print(f"   Dimensions : {dims_info}")
                print(f"   Poids      : {format_size(original_size)} → {format_size(optimized_size)}  "
                      f"(économie : {format_size(gain)} / -{gain_pct:.0f}%)")
                count += 1

            except Exception as e:
                errors.append((filename, str(e)))
                print(f"❌ Erreur sur {filename} : {e}")

    print("-" * 60)
    print(f"🖼  {count} image(s) traitée(s)")
    print(f"📦 Taille totale originale  : {format_size(total_original)}")
    print(f"📦 Taille totale optimisée  : {format_size(total_optimized)}")
    if total_original > 0:
        gain_total = total_original - total_optimized
        gain_pct_total = (gain_total / total_original) * 100
        print(f"💾 Gain total               : {format_size(gain_total)} (-{gain_pct_total:.0f}%)")

    if errors:
        print(f"\n⚠️  {len(errors)} erreur(s) :")
        for name, err in errors:
            print(f"   - {name} : {err}")

    print(f"\n✔️  Images WebP sauvegardées dans : {OUTPUT_DIR}/")
    print("   Les originaux sont conservés dans assets/images/ (inchangés).")


if __name__ == "__main__":
    optimize_images()
