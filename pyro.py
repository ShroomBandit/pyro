import libtcodpy as libtcod
import object as libobj
import map as libmap
import game as libgame
import ui as libui
import ai as libai
import fighter as libfighter
import experience as libxp
import item as libitem
import abilities as libabilities
import shelve
from settings import *


def move_player_or_attack(dx, dy, game):
    x = game.player.x + dx
    y = game.player.y + dy
    target = None
    for object in game.objects:
        if object.component(libfighter.Fighter):
            if object.x == x and object.y == y:
                target = object
                break

    if target:
        game.player.component(libfighter.Fighter).attack(target)
        return (False, None)
    else:
        game.player.move(dx, dy)
        return (True, 'move')


def show_character_info(console, game):
    msg = """Character Information

Level: {0}
Experience: {1}
Next Level: {2}

Current HP: {3}
Maximum HP: {4}
Attack: {5}
Defense: {6}
"""
    exp = game.player.component(libxp.Experience)
    fighter = game.player.component(libfighter.Fighter)
    msg = msg.format(exp.level,
                     exp.xp,
                     exp.required_for_level_up(),
                     fighter.hp,
                     fighter.max_hp(),
                     fighter.power(),
                     fighter.defense())
    libui.messagebox(console, msg, CHARACTER_SCREEN_WIDTH)

def handle_keys(ui, game):
    if ui.keyboard.vk == libtcod.KEY_ENTER and ui.keyboard.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif ui.keyboard.vk == libtcod.KEY_ESCAPE:
        # Exit game
        return (False, 'exit')

    if game.state != 'playing':
        return (False, None)

    key_char = chr(ui.keyboard.c)

    if libtcod.KEY_UP == ui.keyboard.vk:
        return move_player_or_attack(0, -1, game)
    elif libtcod.KEY_DOWN == ui.keyboard.vk:
        return move_player_or_attack(0, 1, game)
    elif libtcod.KEY_LEFT == ui.keyboard.vk:
        return move_player_or_attack(-1, 0, game)
    elif libtcod.KEY_RIGHT == ui.keyboard.vk:
        return move_player_or_attack(1, 0, game)
    elif key_char == 'q': # up-left
        return move_player_or_attack(-1, -1, game)
    elif key_char == 'e': # up-right
        return move_player_or_attack(1, -1, game)
    elif key_char == 'z': # down-left
        return move_player_or_attack(-1, 1, game)
    elif key_char == 'x': # down-right
        return move_player_or_attack(1, 1, game)
    elif key_char == 'f':
        # Don't move, let the monsters come to you
        return (False, None)
    elif key_char == 'g':
        # Pick up an item; look for one in the player's tile
        for object in game.objects:
            item = object.component(libitem.Item)
            if item:
                if object.x == game.player.x and object.y == game.player.y:
                    item.pick_up(game.player)
                    break
        return (False, None)
    elif key_char == 'i':
        # Show the inventory
        msg = 'Select an item to use it, or any other key to cancel.\n'
        inventory = game.player.component(libitem.Inventory).items
        selected_item = libui.inventory_menu(ui.console, inventory, msg)
        if selected_item:
            selected_item.use(ui)
        return (False, None)
    elif key_char == 'd':
        # Show the inventory; if an item is selected, drop it
        msg = 'Select an item to drop it, or any other key to cancel.\n'
        inventory = game.player.component(libitem.Inventory).items
        selected_item = libui.inventory_menu(ui.console, inventory, msg)
        if selected_item:
            selected_item.drop()
        return (False, None)
    elif key_char == '>':
        # Go down the stairs to the next level
        if game.stairs.x == game.player.x and game.stairs.y == game.player.y:
            next_dungeon_level(game)
            libtcod.console_clear(ui.console)
        return (True, None)
    elif key_char == 'c':
        show_character_info(ui.console, game)
        return (False, None)
    else:
        return (False, 'idle')


def player_death(player, game):
    game.message('You died!')
    game.state = 'dead'

    player.char = '%'
    player.color = libtcod.dark_red


def make_fov_map(map):
    # Create the FOV map according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y,
                                       not map[x][y].block_sight,
                                       not map[x][y].blocked)
    return fov_map


def check_player_level_up(game, console):
    player = game.player
    exp = player.component(libxp.Experience)

    # See if the player's XP is enough to level up
    if exp.can_level_up():
        return

    # Ding! Level up!
    exp.level_up()
    msg = 'Your battle skills grow stronger! You reached level {}!'
    game.message(msg.format(exp.level), libtcod.yellow)

    choice = None
    while choice is None:
        fighter = player.component(libfighter.Fighter)
        options = ['Constitution (+20 HP, from {})'.format(fighter.base_max_hp),
                   'Strength (+1 attack, from {})'.format(fighter.base_power),
                   'Agility (+1 defense, from {})'.format(fighter.base_defense)]
        choice = libui.menu(console, 'Level up! Choose a stat to raise:\n',
                            options, LEVEL_SCREEN_WIDTH)
        if choice == 0:
            fighter.base_max_hp += 20
            fighter.hp += 20
        elif choice == 1:
            fighter.base_power += 1
        elif choice == 2:
            fighter.base_defense += 1


def new_game():
    # Create the player
    exp_comp = libxp.Experience(xp=0, level=1)
    fighter_comp = libfighter.Fighter(hp=100, defense=1, power=2,
                                  death_fn=player_death)
    inventory_component = libitem.Inventory()
    player = libobj.Object(0, 0, '@', 'player', libtcod.white, blocks=True,
                           components={libfighter.Fighter: fighter_comp,
                                       libxp.Experience: exp_comp,
                                       libitem.Inventory: inventory_component})

    # Generate map (not drawn to the screen yet)
    dungeon_level = 1
    (map, objects, stairs) = libmap.make_map(player, dungeon_level)
    fov_map = make_fov_map(map)

    messages = []

    game = libgame.Game('playing', map, fov_map, objects, stairs,
                        player, messages, dungeon_level)

    # Initial equipment: a dagger and scroll of lightning
    equipment_comp = libitem.Equipment(slot='right hand', power_bonus=2)
    dagger = libobj.Object(0, 0, '-', 'dagger', libtcod.sky, render_order=0,
                           components={libitem.Equipment: equipment_comp},
                           game=game)
    inventory_component.items.append(dagger)
    equipment_comp.item_owner = player
    equipment_comp.is_equipped = True


    item_comp = libitem.Item(use_fn=libabilities.cast_lightning)
    spell = libobj.Object(0, 0, '-', 'scroll of lightning', libtcod.blue,
                          render_order=0, components={libitem.Item: item_comp},
                          game=game)
    inventory_component.items.append(spell)
    item_comp.item_owner = player

    m = 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!'
    game.message(m, libtcod.red)

    return game


def next_dungeon_level(game):
    # Advance to the next level
    # Heal the player by 50%
    game.message('You take a moment to rest, and recover your strength.',
                 libtcod.light_violet)
    fighter = game.player.component(libfighter.Fighter)
    fighter.heal(fighter.max_hp() / 2)

    msg = 'After a rare moment of peace, you descend deeper into the heart '
    msg += 'of the dungeon...'
    game.message(msg, libtcod.red)
    game.dungeon_level += 1

    (map, objects, stairs) = libmap.make_map(game.player, game.dungeon_level)
    fov_map = make_fov_map(map)

    game.map = map
    game.fov_map = fov_map
    game.objects = objects
    game.stairs = stairs

    for object in game.objects:
        object.game = game

def play_game(game, ui):
    for object in game.objects:
        object.game = game

    fov_recompute = True
    libtcod.console_clear(ui.console)
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                    libtcod.EVENT_MOUSE, ui.keyboard, ui.mouse)

        libui.render_all(ui, game, fov_recompute)

        libtcod.console_flush()

        check_player_level_up(game, ui.console)

        for object in game.objects:
            object.clear(ui.console)

        (fov_recompute, player_action) = handle_keys(ui, game)

        if player_action == 'exit':
            save_game(game)
            break

        if game.state == 'playing' and player_action != 'idle':
            for object in game.objects:
                ai = object.component(libai.AI)
                if ai:
                    ai.take_turn()


def save_game(game):
    # Open an empty shelve (possibly overwriting an old one) to write the data
    file = shelve.open('savegame', 'n')
    file['map'] = game.map
    file['objects'] = game.objects
    file['player_index'] = game.objects.index(game.player)
    file['messages'] = game.messages
    file['state'] = game.state
    file['stairs_index'] = game.objects.index(game.stairs)
    file['dungeon_level'] = game.dungeon_level
    file.close()


def load_game():
    # Open the previously saved shelve and load the game data
    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]
    messages = file['messages']
    state = file['state']
    stairs = objects[file['stairs_index']]
    dungeon_level = file['dungeon_level']
    file.close()

    fov_map = make_fov_map(map)

    return libgame.Game(state, map, fov_map, objects, stairs, player, messages,
                        dungeon_level)


def main_menu(ui):
    background = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        # Show the image at twice the regular console resolution
        libtcod.image_blit_2x(background, 0, 0, 0)

        # Show the game's title and credits
        libtcod.console_set_default_foreground(ui.console, libtcod.light_yellow)
        libtcod.console_print_ex(ui.console, SCREEN_WIDTH/2, (SCREEN_HEIGHT/2)-4,
                                 libtcod.BKGND_NONE, libtcod.CENTER,
                                 'TOMBS OF THE ANCIENT KINGS')
        libtcod.console_print_ex(ui.console, SCREEN_WIDTH/2, SCREEN_HEIGHT-2,
                                 libtcod.BKGND_NONE, libtcod.CENTER,
                                 'By N. Wolfe')

        # Show options and wait for the player's choice
        options = ['Play a new game', 'Continue last game', 'Quit']
        choice = libui.menu(ui.console, '', options, 24)

        if choice == 0:
            # New game
            game = new_game()
            play_game(game, ui)
        elif choice == 1:
            # Load last game
            try:
                game = load_game()
                play_game(game, ui)
            except:
                libui.messagebox(ui.console, '\n No saved game to load.\n', 24)
                continue
        elif choice == 2:
            # Quit
            break


###############################################################################
# Initialization & Main Loop                                                  #
###############################################################################

libtcod.console_set_custom_font('terminal8x12_gs_tc.png',
                                libtcod.FONT_TYPE_GREYSCALE |
                                libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                          'Tombs Of The Ancient Kings', False)
libtcod.sys_set_fps(LIMIT_FPS)

keyboard = libtcod.Key()
mouse = libtcod.Mouse()
console = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
ui = libui.UserInterface(keyboard, mouse, console, panel)

main_menu(ui)
