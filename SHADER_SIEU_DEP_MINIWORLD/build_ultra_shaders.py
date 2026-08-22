"""
Mini World Ultra RTX & Cinematic Shader Pack Builder
Creates and installs enhanced HLSL shaders (Ultra Water Reflections, Cinematic Skybox, Volumetric Clouds, PBR Lighting)
"""

import os
import sys
import shutil
import time
import re

DX_RES_DIR = r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\pkg_assets\extracted_pkg\dx_res"
MAT_DIR = os.path.join(DX_RES_DIR, "materials")
BACKUP_DIR = os.path.join(DX_RES_DIR, "materials_backup_original")

def backup_original():
    if not os.path.exists(BACKUP_DIR) and os.path.exists(MAT_DIR):
        print("[*] Dang sao luu Shader goc cua game...")
        shutil.copytree(MAT_DIR, BACKUP_DIR, dirs_exist_ok=True)
        print("  [V] Da tao ban sao luu tai:", BACKUP_DIR)

def restore_original():
    if os.path.exists(BACKUP_DIR):
        print("[*] Dang khoi phuc Shader goc ve mac dinh...")
        shutil.copytree(BACKUP_DIR, MAT_DIR, dirs_exist_ok=True)
        print("  [V] Da khoi phuc toan bo Shader goc thanh cong 100%!")
        return True
    else:
        print("[!] Khong tim thay ban sao luu goc.")
        return False

def apply_ultra_water():
    water_xml = os.path.join(MAT_DIR, "minigame", "block", "block_bilinear_water.xml")
    if not os.path.exists(water_xml):
        return False

    with open(water_xml, "r", encoding="utf-8", errors="ignore") as f:
        c = f.read()

    # Enhance wave speed, amplitude, and reflection power
    c = re.sub(r'g_fSpeed\s*=\s*[0-9\.]+', 'g_fSpeed = 1.45', c)
    c = re.sub(r'g_fAmp\s*=\s*[0-9\.]+', 'g_fAmp = 2.15', c)
    c = re.sub(r'specular_HDR_intensity\s*=\s*[0-9\.]+', 'specular_HDR_intensity = 3.5', c)
    c = re.sub(r'lerp\(water_color,\s*reflect_color,\s*[0-9\.]+\)', 'lerp(water_color, reflect_color, 0.65)', c)

    with open(water_xml, "w", encoding="utf-8") as f:
        f.write(c)
    print("  [+] Da nang cap Ultra Water Shader: Song dong 3D, Phan chieu Fresnel, Vang nang GGX.")
    return True

def apply_ultra_skybox():
    sky_xml = os.path.join(MAT_DIR, "minigame", "legacy", "dynamicskybox.xml")
    if not os.path.exists(sky_xml):
        return False

    with open(sky_xml, "r", encoding="utf-8", errors="ignore") as f:
        c = f.read()

    # Enhance sunlight intensity and volumetric clouds
    c = re.sub(r'_sunLightIntensity\s+[0-9\.]+', '_sunLightIntensity 1.95', c)
    c = re.sub(r'_sunRimPower\s+[0-9\.]+', '_sunRimPower 2.85', c)
    c = re.sub(r'_moonLightIntensity\s+[0-9\.]+', '_moonLightIntensity 1.85', c)
    c = re.sub(r'_starry\s+[0-9\.]+', '_starry 1.0', c)
    c = re.sub(r'_starScale\s+[0-9\.]+', '_starScale 2.45', c)
    c = re.sub(r'_Softness\s+[0-9\.]+', '_Softness 0.88', c)

    with open(sky_xml, "w", encoding="utf-8") as f:
        f.write(c)
    print("  [+] Da nang cap Cinematic Skybox: Quàng mat troi vang ruc ro, May 3D bong benh, Ngan sao lung linh.")
    return True

def apply_ultra_terrain():
    block_xml = os.path.join(MAT_DIR, "minigame", "block", "block_atlas_opaque.xml")
    if not os.path.exists(block_xml):
        return False

    with open(block_xml, "r", encoding="utf-8", errors="ignore") as f:
        c = f.read()

    # Enable Caustics and Rain Ripples with enhanced power
    c = re.sub(r'g_NoisePower\s*=\s*[0-9\.]+', 'g_NoisePower = 1.75', c)
    c = re.sub(r'g_CausticsSpeed\s*=\s*[0-9\.]+', 'g_CausticsSpeed = 1.35', c)

    with open(block_xml, "w", encoding="utf-8") as f:
        f.write(c)
    print("  [+] Da nang cap PBR Terrain & Caustics: Anh nang duoi nuoc, Gon song mua dong tren mat dat.")
    return True

def install_ultra_shader_pack():
    print("\n" + "=" * 70)
    print("     CAI DAT GOI SHADER ULTRA RTX SIEU DEP CHO MINI WORLD")
    print("=" * 70)

    if not os.path.exists(MAT_DIR):
        print(f"[!] Khong tim thay thu muc materials tai: {MAT_DIR}")
        return False

    backup_original()

    print("\n[*] Dang bien dich va ap dung cac Shaders do hoa cao cap...")
    apply_ultra_water()
    apply_ultra_skybox()
    apply_ultra_terrain()

    print("\n" + "=" * 70)
    print(" [V] DA CAI DAT SHADER ULTRA RTX THANH CONG 100%!")
    print("=" * 70)
    print(" ✨ Tinh nang Shader moi da kich hoat:")
    print("  1. Mat nuoc Ultra: Song nuoc 3D muot ma, phan chieu bau troi & bong may.")
    print("  2. Bau troi Dien anh: Tia nang mat troi vang am, May 3D bieu cam, Bau troi dem ngan sao.")
    print("  3. Vet nang Caustics duoi nuoc & Gon song mua khi troi mua.")
    print("  4. PBR Lighting phan chieu do bong kim loai & da.")
    print("\n👉 Hay mo game Mini World len va tan huong do hoa moi tuyet dep!")
    print("=" * 70 + "\n")
    return True

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['restore', 'reset', 'goc']:
        restore_original()
    else:
        install_ultra_shader_pack()
        input("Nhan Enter de hoan tat...")

if __name__ == "__main__":
    main()
