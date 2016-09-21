import component as libcomp
import libtcodpy as libtcod
from settings import *


class AI(libcomp.Component):
    def take_turn(self, game):
        # Children must implement
        return


class BasicMonster(AI):
    def take_turn(self, game):
        monster = self.owner
        if libtcod.map_is_in_fov(game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(game.player) >= 2:
                monster.move_towards(game.map, game.objects,
                                     game.player.x, game.player.y)

            # Close enough, attack! (If the player is still alive)
            elif game.player.components.get(Fighter).hp > 0:
                monster.components.get(Fighter).attack(game.player, game)


def basic_monster():
    return BasicMonster()


class ConfusedMonster(AI):
    def __init__(self, restore_ai, num_turns=CONFUSE_NUM_TURNS):
        self.restore_ai = restore_ai
        self.num_turns = num_turns

    def take_turn(self, game):
        if self.num_turns > 0:
            # Move in a random direction
            self.owner.move(game.map, game.objects,
                            libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            # Restore normal AI
            self.owner.components[AI] = restore_ai
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            game.message(msg, libtcod.red)


def confused_monster():
    return ConfusedMonster(BasicMonster())