"""
Core Converter Engine: Minecraft World / .mca -> Mini World Map / .r
"""

import os
import time
import glob
from mc_mca_reader import MCAReader
from mw_region_writer import MWRegionWriter, MWWorldGenerator

def convert_single_mca(mca_path, output_r_path=None, progress_cb=None):
    """
    Converts a single Minecraft .mca file to Mini World .r file.
    """
    if not os.path.exists(mca_path):
        if progress_cb:
            progress_cb(f"Error: File {mca_path} not found!")
        return False

    reader = MCAReader(mca_path)
    rx, rz = reader.rx, reader.rz
    
    if output_r_path is None:
        output_r_path = os.path.join(os.path.dirname(mca_path), f"x{rx}z{rz}.r")

    if progress_cb:
        progress_cb(f"Converting Region ({rx}, {rz}): {os.path.basename(mca_path)} -> {os.path.basename(output_r_path)}...")

    writer = MWRegionWriter(rx, rz)
    chunk_count = 0
    total_blocks = 0

    for chunk in reader.read_all_chunks():
        writer.add_chunk(chunk)
        chunk_count += 1
        total_blocks += len(chunk.blocks)

    written_chunks = writer.write_to_file(output_r_path)
    
    if progress_cb:
        progress_cb(f"Finished: {written_chunks} chunks ({total_blocks:,} blocks) -> {output_r_path}")

    return True

def convert_minecraft_world(mc_world_dir, output_base_dir, world_name=None, progress_cb=None):
    """
    Converts an entire Minecraft save folder to a complete Mini World map folder.
    """
    if not os.path.exists(mc_world_dir):
        if progress_cb:
            progress_cb(f"Error: Minecraft world folder {mc_world_dir} does not exist!")
        return None

    # Locate region directory inside world folder
    region_dir = os.path.join(mc_world_dir, "region")
    if not os.path.exists(region_dir):
        # Maybe user selected the region folder itself
        if any(f.endswith(".mca") for f in os.listdir(mc_world_dir)):
            region_dir = mc_world_dir
        else:
            if progress_cb:
                progress_cb("Error: No 'region' folder or .mca files found in the specified path!")
            return None

    mca_files = glob.glob(os.path.join(region_dir, "*.mca"))
    if not mca_files:
        if progress_cb:
            progress_cb(f"No .mca files found in {region_dir}!")
        return None

    if world_name is None:
        world_name = os.path.basename(os.path.abspath(mc_world_dir))
        if world_name.lower() in ["region", "saves", "minecraft"]:
            world_name = "Converted_MC_World"

    world_id = int(time.time())
    world_dir, m0_dir = MWWorldGenerator.create_world(world_id, world_name, output_base_dir)

    if progress_cb:
        progress_cb(f"Creating Mini World Map: {world_name} (ID: w{world_id})")
        progress_cb(f"Found {len(mca_files)} region files (.mca) to convert.")

    t0 = time.time()
    converted_count = 0
    total_chunks = 0
    total_blocks = 0

    for idx, mca in enumerate(mca_files, 1):
        reader = MCAReader(mca)
        rx, rz = reader.rx, reader.rz
        out_r = os.path.join(m0_dir, f"x{rx}z{rz}.r")

        if progress_cb:
            progress_cb(f"[{idx}/{len(mca_files)}] Converting {os.path.basename(mca)} -> x{rx}z{rz}.r...")

        writer = MWRegionWriter(rx, rz)
        reg_chunks = 0
        reg_blocks = 0
        for chunk in reader.read_all_chunks():
            writer.add_chunk(chunk)
            reg_chunks += 1
            reg_blocks += len(chunk.blocks)

        if reg_chunks > 0:
            writer.write_to_file(out_r)
            converted_count += 1
            total_chunks += reg_chunks
            total_blocks += reg_blocks

    elapsed = time.time() - t0
    if progress_cb:
        progress_cb("\n" + "=" * 55)
        progress_cb(f"[V] CHUYEN DOI THANH CONG BAN DO MINECRAFT!")
        progress_cb(f"- So file Region (.r): {converted_count}")
        progress_cb(f"- Tong so Chunk: {total_chunks:,}")
        progress_cb(f"- Tong so Block da chuyen: {total_blocks:,}")
        progress_cb(f"- Thoi gian: {elapsed:.2f}s")
        progress_cb(f"- Thu muc ban do Mini World: {world_dir}")
        progress_cb("=" * 55)

    return world_dir
