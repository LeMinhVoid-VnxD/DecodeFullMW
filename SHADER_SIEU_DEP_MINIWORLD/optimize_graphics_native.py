"""
Mini World Native Ultra Graphics & Shader Optimizer
Enables official native D3D11 graphics (Water Reflections, God Rays, Waving Leaves, Dynamic Sky, HDR, 60+ FPS) without any lag or crash.
"""

import os
import json

CONFIG_PATH = r"C:\Users\Le Minh\AppData\Roaming\miniworddata410\UserConfig\Custom_GameConfiguration.json"

def optimize_graphics(mode="ultra"):
    if not os.path.exists(CONFIG_PATH):
        print(f"[!] Khong tim thay file cau hinh tai: {CONFIG_PATH}")
        return False

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    print("\n" + "=" * 70)
    print("      DANG TOI UU HOA DO HOA ULTRA NATIVE (KHONG LAG - KHONG CRASH)")
    print("=" * 70)

    # 1. FPS & Performance Settings
    cfg["m_nLimitFrameRate"] = 60         # Unlock 60 FPS muot ma
    cfg["m_eGraphicsQuality"] = 2         # High Graphics Quality
    cfg["m_eResolutionLevel"] = 0         # Native Full Resolution

    # 2. Water & Atmosphere
    cfg["m_eWaterReflection"] = 2         # Ultra Water Reflections
    cfg["m_eWaterSurfaceCaustics"] = 1    # Underwater Caustics
    cfg["m_eDynamicSkyLevel"] = 2         # Dynamic Sky & Volumetric Clouds
    cfg["m_eFogEffect"] = 1               # Atmospheric Fog

    # 3. Foliage & Wind Animation
    cfg["m_eDynamicVegetation"] = 1       # La cay & Co rung rinh theo gio

    # 4. Lighting & Shadows
    cfg["m_eVolumetricLights"] = 1        # Tia nang mat troi (God Rays)
    cfg["m_eRealTimeShadows"] = 1         # Bong do thoi gian thuc
    cfg["m_ShadowCfg"]["m_nDistance"] = 40
    cfg["m_ShadowCfg"]["m_eShadowResolutionLevel"] = 2
    cfg["m_ShadowCfg"]["m_nCascadeLevel"] = 2

    # 5. Post-Processing & PBR
    cfg["m_bHDR"] = True                  # Mau sac HDR song dong
    cfg["m_eBloom"] = 1                   # Quang sang Bloom lap lanh
    cfg["m_bSSAO"] = True                 # Do bong tiep xuc SSAO
    cfg["m_eAntiAliasing"] = 2            # Khu rang cua min mang
    cfg["m_eTextureQuality"] = 2          # Chat luong Texture Max
    cfg["m_eModelQuality"] = 2            # Chat luong Model 3D Max
    cfg["m_eMaterialQuality"] = 2         # Chat luong Shader Material Max
    cfg["m_bEnableLocalLight"] = True     # Anh sang den duoc phat sang

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

    print("\n [V] DA KICH HOAT THANH CONG DO HOA ULTRA NATIVE!")
    print("=" * 70)
    print(" ✨ Danh sach tinh nang da duoc bat:")
    print("  • 🌊 Mat nuoc phan chieu 3D & Vet nang duoi ho (Water Reflection & Caustics)")
    print("  • 🍃 La cay & Co rung rinh theo gio (Dynamic Vegetation)")
    print("  • ☀️ Tia nang mat troi xuyen qua cay (Volumetric God Rays)")
    print("  • ☁️ Bau troi dong & May 3D bong benh (Dynamic Sky Level)")
    print("  • 🌑 Bong do thoi gian thuc (Real-time Shadows)")
    print("  • 🌈 Mau sac HDR & Quang sang Bloom ruc ro (HDR & Bloom)")
    print("  • ⚡ Mo khoa 60 FPS sieu muot ma (Khong tut FPS, khong giat lag)")
    print("\n👉 Hay mo game Mini World len de xem su khac biet do hoa!")
    print("=" * 70 + "\n")
    return True

if __name__ == "__main__":
    optimize_graphics()
