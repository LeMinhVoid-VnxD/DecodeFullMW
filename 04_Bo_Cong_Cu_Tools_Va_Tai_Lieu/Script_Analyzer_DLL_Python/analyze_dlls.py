"""
Mini World Native DLL Analyzer & Header / Function Extractor
Analyzes all game DLLs, demangles C++ functions, dumps RTTI classes, imports/exports and strings.
"""

import os
import re
import ctypes
import struct
import pefile

# Windows MSVC Demangler
try:
    dbghelp = ctypes.windll.dbghelp
    undecorate = dbghelp.UnDecorateSymbolName
    undecorate.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint]
    undecorate.restype = ctypes.c_uint

    def demangle(mangled):
        buf = ctypes.create_string_buffer(2048)
        res = undecorate(mangled.encode('latin1'), buf, 2048, 0)
        if res and buf.value:
            return buf.value.decode('latin1', 'ignore')
        return mangled
except Exception:
    def demangle(mangled):
        return mangled

def extract_strings(data, min_len=4):
    strings = []
    # ASCII strings
    for m in re.finditer(rb'[\x20-\x7e]{' + str(min_len).encode() + rb',}', data):
        s = m.group().decode('latin1', 'ignore')
        if s.strip():
            strings.append(s.strip())
    # UTF-16 LE strings
    for m in re.finditer(rb'(?:[\x20-\x7e]\x00){' + str(min_len).encode() + rb',}', data):
        try:
            s = m.group().decode('utf-16le', 'ignore')
            if s.strip():
                strings.append(s.strip())
        except Exception:
            pass
    return sorted(list(set(strings)))

def analyze_single_dll(dll_path, output_dir):
    dll_name = os.path.basename(dll_path)
    stem = os.path.splitext(dll_name)[0]
    out_txt = os.path.join(output_dir, f"{stem}_analysis.txt")
    out_md = os.path.join(output_dir, f"{stem}_functions.md")

    print(f"[*] Dang phan tich: {dll_name} ({os.path.getsize(dll_path)/(1024*1024):.2f} MB)...")

    try:
        pe = pefile.PE(dll_path)
    except Exception as e:
        print(f"    [!] Khong the doc PE header: {e}")
        return

    with open(dll_path, 'rb') as f:
        raw_data = f.read()

    # 1. Exports
    exports = []
    if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if exp.name:
                mangled = exp.name.decode('latin1', 'ignore')
                demangled_name = demangle(mangled)
                exports.append({
                    'ordinal': exp.ordinal,
                    'rva': hex(exp.address),
                    'mangled': mangled,
                    'demangled': demangled_name
                })

    # 2. Imports
    imports = {}
    if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            imp_dll = entry.dll.decode('latin1', 'ignore')
            imports[imp_dll] = []
            for imp in entry.imports:
                if imp.name:
                    imports[imp_dll].append(imp.name.decode('latin1', 'ignore'))
                elif imp.ordinal:
                    imports[imp_dll].append(f"Ordinal_{imp.ordinal}")

    # 3. RTTI Classes
    rtti_classes = []
    for m in re.finditer(rb'\.\?AV([A-Za-z0-9_<>$,]+)@@', raw_data):
        cname = m.group(1).decode('latin1', 'ignore')
        rtti_classes.append(cname)
    rtti_classes = sorted(list(set(rtti_classes)))

    # 4. Extract Strings
    game_strings = extract_strings(raw_data, min_len=5)

    # Write Text Report
    with open(out_txt, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"BAO CAO PHAN TICH NHI PHAN THU VIEN: {dll_name}\n")
        f.write(f"Dung luong: {len(raw_data):,} bytes ({len(raw_data)/(1024*1024):.2f} MB)\n")
        f.write(f"Kien truc: {'32-bit (x86)' if pe.FILE_HEADER.Machine == 0x14c else '64-bit (x64)'}\n")
        f.write(f"So luong ham Export: {len(exports)}\n")
        f.write(f"So luong C++ RTTI Classes: {len(rtti_classes)}\n")
        f.write("=" * 80 + "\n\n")

        # Exports
        f.write(f"--- 1. DANH SACH HAM EXPORT ({len(exports)} HAMS) ---\n")
        for exp in exports:
            f.write(f"[{exp['rva']}] Ordinal {exp['ordinal']:<4}: {exp['demangled']}\n")
            if exp['demangled'] != exp['mangled']:
                f.write(f"      (Symbol: {exp['mangled']})\n")
        f.write("\n")

        # RTTI Classes
        f.write(f"--- 2. DANH SACH C++ CLASSES & STRUCTS RTTI ({len(rtti_classes)} CLASSES) ---\n")
        for cls in rtti_classes:
            f.write(f"  class {cls}\n")
        f.write("\n")

        # Imports
        f.write(f"--- 3. THU VIEN & HAM DEPENDENCIES IMPORT ({len(imports)} DLLS) ---\n")
        for idll, ifuncs in imports.items():
            f.write(f"  [{idll}] ({len(ifuncs)} functions)\n")
            for fn in ifuncs[:15]:
                f.write(f"    - {fn}\n")
            if len(ifuncs) > 15:
                f.write(f"    - ... ({len(ifuncs) - 15} ham khac)\n")
        f.write("\n")

        # Interesting Game Strings
        f.write(f"--- 4. CHUOI KY TU NOI BAT TRONG GAME ({len(game_strings)} STRINGS) ---\n")
        filtered_strings = [s for s in game_strings if any(k in s.lower() for k in ['http', 'lua', 'pkg', 'map', 'save', 'load', 'block', 'chunk', 'error', 'config', 'mini'])]
        for s in filtered_strings[:500]:
            f.write(f"  \"{s}\"\n")

    # Write Markdown Function Reference
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write(f"# Danh mục Hàm & Cấu trúc C++: `{dll_name}`\n\n")
        f.write(f"- **Dung lượng**: {len(raw_data)/(1024*1024):.2f} MB\n")
        f.write(f"- **Tổng số hàm Export**: {len(exports):,}\n")
        f.write(f"- **Tổng số lớp RTTI**: {len(rtti_classes):,}\n\n")

        f.write("## Danh sách C++ Classes (RTTI)\n\n")
        f.write("| STT | Tên Lớp (Class / Struct) |\n")
        f.write("| :---: | :--- |\n")
        for idx, cls in enumerate(rtti_classes[:200], 1):
            f.write(f"| {idx} | `{cls}` |\n")
        if len(rtti_classes) > 200:
            f.write(f"| ... | *Và {len(rtti_classes) - 200} lớp khác...* |\n")

        f.write("\n## Danh sách Hàm C++ (Demangled Functions)\n\n")
        f.write("| Địa chỉ RVA | Tên Hàm C++ |\n")
        f.write("| :---: | :--- |\n")
        for exp in exports:
            f.write(f"| `{exp['rva']}` | `{exp['demangled']}` |\n")

    print(f"    [+] Da tao bao cao: {out_txt}")

def main():
    print("=" * 70)
    print("       MINI WORLD NATIVE DLL DECOMPILER & ANALYZER TOOL")
    print("=" * 70)

    dll_dir = r"C:\Users\Le Minh\AppData\Roaming\miniworldOverseasgame"
    output_dir = r"C:\Users\Le Minh\OneDrive\Desktop\decodepkg\dll_analysis"
    os.makedirs(output_dir, exist_ok=True)

    target_dlls = [
        "libEngine.dll",
        "libframework.dll",
        "libMiniBlock.dll",
        "libiworld.dll",
        "libMiniBaseEngine.dll",
        "libMiniBaseGame.dll",
        "liblua.dll",
        "libSandBoxEngine.dll",
        "libSandboxEngineDriver.dll"
    ]

    for d in target_dlls:
        p = os.path.join(dll_dir, d)
        if os.path.exists(p):
            analyze_single_dll(p, output_dir)

    print("\n" + "=" * 70)
    print(f"[V] HOAN TAT PHAN TICH TOAN BO FILE .DLL CHINH CUA MINI WORLD!")
    print(f"Thu muc ket qua: {output_dir}")
    print("=" * 70)

if __name__ == "__main__":
    main()
