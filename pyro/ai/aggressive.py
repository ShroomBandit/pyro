from pyro.components import AI, Fighter


class Aggressive(AI):
    """Pursue and attack the player once in sight."""

    def take_turn(self):
        monster = self.owner
        if monster.game.game_map.is_in_fov(monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(monster.game.player) >= 2:
                monster.move_astar(monster.game.player.x, monster.game.player.y)

            # Close enough, attack! (If the player is still alive)
            elif monster.game.player.component(Fighter).hp > 0:
                monster.component(Fighter).attack(monster.game.player)
