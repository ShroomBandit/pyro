import os
import tcod as libtcod

# Tile colors
COLOR_DARK_WALL = libtcod.Color(0, 0, 100)
COLOR_LIGHT_WALL = libtcod.Color(130, 110, 50)
COLOR_DARK_GROUND = libtcod.Color(50, 50, 150)
COLOR_LIGHT_GROUND = libtcod.Color(200, 180, 50)
COLOR_LIGHT_GRASS = libtcod.Color(40, 87, 24)

# GUI
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
MAP_WIDTH = 80
MAP_HEIGHT = 43
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30

# Dungeon generation
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

# Render Orders
RENDER_ORDER_DEFAULT = 10
RENDER_ORDER_ITEM = 8
RENDER_ORDER_CORPSE = 1

# Experience and levelling
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
LEVEL_UP_STAT_HP = 20
LEVEL_UP_STAT_POWER = 1
LEVEL_UP_STAT_DEFENSE = 1

# Player, monster, spell statistics
if 'HEALTH' in os.environ:
    PLAYER_DEFAULT_HP = int(os.environ['HEALTH'])
else:
    PLAYER_DEFAULT_HP = 100
PLAYER_DEFAULT_DEFENSE = 1
PLAYER_DEFAULT_POWER = 2
SPELL_CONFUSE_RANGE = 5
SPELL_CONFUSE_TURNS = 10
SPELL_FIREBALL_RANGE = 4
SPELL_FIREBALL_STRENGTH = 15
SPELL_FIREBALL_RADIUS = 3
SPELL_HEAL_STRENGTH = 40
SPELL_LIGHTNING_BOLT_RANGE = 5
SPELL_LIGHTNING_BOLT_STRENGTH = 10
