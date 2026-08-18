"""
Block mapping database: Minecraft (Java/Bedrock) -> Mini World: CREATA
"""

# Default fallback block ID in Mini World if not specifically mapped
DEFAULT_AIR = 0
DEFAULT_STONE = 103
DEFAULT_DIRT = 101

# Comprehensive dictionary of Minecraft block identifiers to Mini World block IDs
MC_TO_MW_BLOCKS = {
    # Air & Void
    "minecraft:air": 0,
    "minecraft:cave_air": 0,
    "minecraft:void_air": 0,

    # Basic Terrain & Stones
    "minecraft:stone": 103,
    "minecraft:granite": 103,
    "minecraft:polished_granite": 103,
    "minecraft:diorite": 103,
    "minecraft:polished_diorite": 103,
    "minecraft:andesite": 103,
    "minecraft:polished_andesite": 103,
    "minecraft:deepslate": 103,
    "minecraft:cobbled_deepslate": 104,
    "minecraft:cobblestone": 104,
    "minecraft:mossy_cobblestone": 104,
    "minecraft:bedrock": 1,

    # Dirt, Grass & Soil
    "minecraft:grass_block": 100,
    "minecraft:dirt": 101,
    "minecraft:coarse_dirt": 101,
    "minecraft:podzol": 101,
    "minecraft:mycelium": 100,
    "minecraft:dirt_path": 102,
    "minecraft:farmland": 102,
    "minecraft:mud": 101,
    "minecraft:clay": 105,

    # Sand & Gravel
    "minecraft:sand": 29,
    "minecraft:red_sand": 29,
    "minecraft:sandstone": 108,
    "minecraft:red_sandstone": 108,
    "minecraft:gravel": 107,

    # Wood Logs
    "minecraft:oak_log": 200,
    "minecraft:spruce_log": 201,
    "minecraft:birch_log": 202,
    "minecraft:jungle_log": 203,
    "minecraft:acacia_log": 204,
    "minecraft:dark_oak_log": 204,
    "minecraft:mangrove_log": 203,
    "minecraft:cherry_log": 200,
    "minecraft:stripped_oak_log": 200,
    "minecraft:stripped_spruce_log": 201,
    "minecraft:stripped_birch_log": 202,
    "minecraft:stripped_jungle_log": 203,
    "minecraft:wood": 200,

    # Wood Planks
    "minecraft:oak_planks": 207,
    "minecraft:spruce_planks": 208,
    "minecraft:birch_planks": 209,
    "minecraft:jungle_planks": 210,
    "minecraft:acacia_planks": 211,
    "minecraft:dark_oak_planks": 212,
    "minecraft:mangrove_planks": 210,
    "minecraft:cherry_planks": 207,
    "minecraft:bamboo_planks": 209,

    # Leaves
    "minecraft:oak_leaves": 218,
    "minecraft:spruce_leaves": 219,
    "minecraft:birch_leaves": 220,
    "minecraft:jungle_leaves": 221,
    "minecraft:acacia_leaves": 222,
    "minecraft:dark_oak_leaves": 218,
    "minecraft:mangrove_leaves": 221,
    "minecraft:cherry_leaves": 218,
    "minecraft:azalea_leaves": 218,

    # Water & Lava Liquids
    "minecraft:water": 4,
    "minecraft:flowing_water": 4,
    "minecraft:lava": 6,
    "minecraft:flowing_lava": 6,

    # Ores & Minerals
    "minecraft:coal_ore": 300,
    "minecraft:deepslate_coal_ore": 300,
    "minecraft:iron_ore": 301,
    "minecraft:deepslate_iron_ore": 301,
    "minecraft:gold_ore": 302,
    "minecraft:deepslate_gold_ore": 302,
    "minecraft:diamond_ore": 303,
    "minecraft:deepslate_diamond_ore": 303,
    "minecraft:lapis_ore": 304,
    "minecraft:deepslate_lapis_ore": 304,
    "minecraft:redstone_ore": 305,
    "minecraft:deepslate_redstone_ore": 305,
    "minecraft:emerald_ore": 306,
    "minecraft:deepslate_emerald_ore": 306,
    "minecraft:nether_quartz_ore": 307,
    "minecraft:nether_gold_ore": 302,
    "minecraft:ancient_debris": 303,

    # Mineral Blocks
    "minecraft:coal_block": 350,
    "minecraft:iron_block": 351,
    "minecraft:gold_block": 352,
    "minecraft:diamond_block": 353,
    "minecraft:lapis_block": 354,
    "minecraft:redstone_block": 355,
    "minecraft:emerald_block": 356,
    "minecraft:netherite_block": 353,

    # Building Blocks & Bricks
    "minecraft:bricks": 108,
    "minecraft:stone_bricks": 108,
    "minecraft:mossy_stone_bricks": 108,
    "minecraft:cracked_stone_bricks": 108,
    "minecraft:chiseled_stone_bricks": 108,
    "minecraft:mud_bricks": 108,
    "minecraft:bookshelf": 250,
    "minecraft:glass": 140,
    "minecraft:glass_pane": 140,
    "minecraft:white_stained_glass": 140,
    "minecraft:obsidian": 15,
    "minecraft:crying_obsidian": 16,

    # Ice & Snow
    "minecraft:ice": 430,
    "minecraft:packed_ice": 430,
    "minecraft:blue_ice": 430,
    "minecraft:snow": 120,
    "minecraft:snow_block": 120,

    # Nether & End
    "minecraft:netherrack": 15,
    "minecraft:soul_sand": 13,
    "minecraft:soul_soil": 101,
    "minecraft:basalt": 103,
    "minecraft:blackstone": 103,
    "minecraft:end_stone": 103,
    "minecraft:end_stone_bricks": 108,
    "minecraft:purpur_block": 108,

    # Flora & Plants
    "minecraft:poppy": 230,
    "minecraft:dandelion": 231,
    "minecraft:blue_orchid": 232,
    "minecraft:allium": 230,
    "minecraft:azure_bluet": 231,
    "minecraft:red_tulip": 230,
    "minecraft:orange_tulip": 230,
    "minecraft:white_tulip": 231,
    "minecraft:pink_tulip": 230,
    "minecraft:oxeye_daisy": 231,
    "minecraft:cornflower": 232,
    "minecraft:lily_of_the_valley": 231,
    "minecraft:sunflower": 231,
    "minecraft:rose_bush": 230,
    "minecraft:short_grass": 224,
    "minecraft:tall_grass": 224,
    "minecraft:fern": 224,
    "minecraft:large_fern": 224,
    "minecraft:dead_bush": 225,
    "minecraft:cactus": 238,
    "minecraft:sugar_cane": 234,
    "minecraft:bamboo": 234,
    "minecraft:vine": 224,
    "minecraft:lily_pad": 224,
    "minecraft:brown_mushroom": 240,
    "minecraft:red_mushroom": 241,

    # Wool & Colors
    "minecraft:white_wool": 260,
    "minecraft:orange_wool": 261,
    "minecraft:magenta_wool": 262,
    "minecraft:light_blue_wool": 263,
    "minecraft:yellow_wool": 264,
    "minecraft:lime_wool": 265,
    "minecraft:pink_wool": 266,
    "minecraft:gray_wool": 267,
    "minecraft:light_gray_wool": 268,
    "minecraft:cyan_wool": 269,
    "minecraft:purple_wool": 270,
    "minecraft:blue_wool": 271,
    "minecraft:brown_wool": 272,
    "minecraft:green_wool": 273,
    "minecraft:red_wool": 274,
    "minecraft:black_wool": 275,

    # Concrete & Terracotta
    "minecraft:white_concrete": 260,
    "minecraft:orange_concrete": 261,
    "minecraft:yellow_concrete": 264,
    "minecraft:lime_concrete": 265,
    "minecraft:green_concrete": 273,
    "minecraft:blue_concrete": 271,
    "minecraft:red_concrete": 274,
    "minecraft:black_concrete": 275,
    "minecraft:terracotta": 108,

    # Lights & Utilities
    "minecraft:torch": 280,
    "minecraft:wall_torch": 280,
    "minecraft:soul_torch": 280,
    "minecraft:soul_wall_torch": 280,
    "minecraft:lantern": 280,
    "minecraft:glowstone": 285,
    "minecraft:sea_lantern": 285,
    "minecraft:shroomlight": 285,
    "minecraft:crafting_table": 290,
    "minecraft:furnace": 291,
    "minecraft:chest": 292,
    "minecraft:trapped_chest": 292,
    "minecraft:barrel": 292,
    "minecraft:ladder": 295,
    "minecraft:scaffolding": 295,
}

# Legacy Minecraft 1.12 Block ID mapping (Numeric ID -> Mini World ID)
LEGACY_MC_ID_TO_MW = {
    0: 0,    # Air
    1: 103,  # Stone
    2: 100,  # Grass
    3: 101,  # Dirt
    4: 104,  # Cobblestone
    5: 207,  # Planks
    7: 1,    # Bedrock
    8: 4,    # Flowing Water
    9: 4,    # Still Water
    10: 6,   # Flowing Lava
    11: 6,   # Still Lava
    12: 29,  # Sand
    13: 107, # Gravel
    14: 302, # Gold Ore
    15: 301, # Iron Ore
    16: 300, # Coal Ore
    17: 200, # Wood
    18: 218, # Leaves
    19: 105, # Sponge
    20: 140, # Glass
    21: 304, # Lapis Ore
    22: 354, # Lapis Block
    24: 108, # Sandstone
    31: 224, # Tall Grass
    32: 225, # Dead Bush
    35: 260, # Wool
    37: 231, # Yellow Flower
    38: 230, # Red Flower
    39: 240, # Brown Mushroom
    40: 241, # Red Mushroom
    41: 352, # Gold Block
    42: 351, # Iron Block
    45: 108, # Brick Block
    46: 299, # TNT
    47: 250, # Bookshelf
    48: 104, # Moss Stone
    49: 15,  # Obsidian
    50: 280, # Torch
    54: 292, # Chest
    56: 303, # Diamond Ore
    57: 353, # Diamond Block
    58: 290, # Crafting Table
    61: 291, # Furnace
    65: 295, # Ladder
    73: 305, # Redstone Ore
    78: 120, # Snow Layer
    79: 430, # Ice
    80: 120, # Snow Block
    81: 238, # Cactus
    82: 105, # Clay
    83: 234, # Reeds
    87: 15,  # Netherrack
    88: 13,  # Soul Sand
    89: 285, # Glowstone
    98: 108, # Stone Brick
    129: 306,# Emerald Ore
    133: 356,# Emerald Block
}

def map_mc_block_to_mw(block_name_or_id):
    """
    Maps a Minecraft block state or numeric ID to Mini World block ID.
    """
    if isinstance(block_name_or_id, int):
        return LEGACY_MC_ID_TO_MW.get(block_name_or_id, DEFAULT_STONE if block_name_or_id > 0 else DEFAULT_AIR)
    
    name = str(block_name_or_id).lower()
    if "[" in name:
        name = name.split("[")[0]
    if not name.startswith("minecraft:"):
        name = "minecraft:" + name
        
    if name in MC_TO_MW_BLOCKS:
        return MC_TO_MW_BLOCKS[name]
        
    # Heuristic matching if not explicitly in table
    if "air" in name:
        return DEFAULT_AIR
    elif "leaves" in name:
        return 218
    elif "log" in name or "wood" in name or "stem" in name:
        return 200
    elif "plank" in name:
        return 207
    elif "ore" in name:
        return 300
    elif "brick" in name:
        return 108
    elif "stone" in name:
        return 103
    elif "glass" in name:
        return 140
    elif "wool" in name or "concrete" in name or "terracotta" in name:
        return 260
    elif "sand" in name:
        return 29
    elif "water" in name:
        return 4
    elif "lava" in name:
        return 6
    elif "flower" in name or "tulip" in name:
        return 230
        
    return DEFAULT_STONE
