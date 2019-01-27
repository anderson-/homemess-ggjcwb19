import arcade
import random

SPRITE_P1W='res/p1.png'
SPRITE_P2W='res/p2.png'
SPRITE_P3W='res/p3.png'
SPRITE_P4W='res/p4.png'
SPRITE_P1='res/pp1.png'
SPRITE_P2='res/pp2.png'
SPRITE_P3='res/pp3.png'
SPRITE_P4='res/pp4.png'
SPRITE_CASTLE_WALK='res/cw.png'
SPRITE_CASTLE_STAND='res/cs.png'
BG='res/bg.png'
F0='res/f0.png'
F1='res/f1.png'
F2='res/f2.png'
F3='res/f3.png'
F4='res/f4.png'


RF=3 # resize factor
SCREEN_WIDTH = 400*RF
SCREEN_HEIGHT = 300*RF
SPRITE_SCALING = 1*RF

PLAYER_SPEED = 2*RF
CASTLE_SPEED = 1*RF
JUMP_SPEED = 5*RF
GRAVITY = -9.8*RF

rand_color = lambda: getattr(arcade.color, random.choice(dir(arcade.color)[:-10]))

class Player(object):
    def __init__(self, x, level, w, h, stand_tiles, stand_file, walk_tiles, walk_file):
        self.player_sprite_stand_right = None
        self.player_sprite_stand_left = None
        self.player_sprite_walk = None
        self.player_sprite_list = None
        self.start_x = x
        self.start_y = level*RF*60+100
        self.w = w
        self.h = h
        self.stand_tiles = stand_tiles
        self.stand_file = stand_file
        self.walk_tiles = walk_tiles
        self.walk_file = walk_file

        self.jumping = False
        self.level = level
        self.jumping_dir = 0
        self.hiden = False
        self.player_inside = None
        self.teleport_time = 0
        self.score = 0

    def _load_tiles(self, size):
        list_imgs = []
        for j in range(size[1]):
            for i in range(size[0]):
                list_imgs.append([i*self.w, j*self.h, self.w, self.h])
        return list_imgs

    def setup(self):
        self.player_sprite_list = arcade.SpriteList()

        list_imgs = self._load_tiles(self.stand_tiles)
        self.player_sprite_stand_right = arcade.AnimatedTimeSprite()
        self.player_sprite_stand_right.textures = []
        for t in arcade.draw_commands.load_textures(self.stand_file, list_imgs):
            self.player_sprite_stand_right.textures.append(t)
        self.player_sprite_stand_right.texture_change_frames = 10
        # self.player_sprite_stand_right.frame = random.choice(range(self.stand_tiles[0]))
        self.player_sprite_stand_right.scale = SPRITE_SCALING
        self.player_sprite_stand_right.center_x = self.start_x
        self.player_sprite_stand_right.bottom = self.start_y
        self.player_sprite_list.append(self.player_sprite_stand_right)

        self.player_sprite_stand_left = arcade.AnimatedTimeSprite()
        self.player_sprite_stand_left.textures = []
        for t in arcade.draw_commands.load_textures(self.stand_file, list_imgs, mirrored=True):
            self.player_sprite_stand_left.textures.append(t)
        self.player_sprite_stand_left.texture_change_frames = 10
        # self.player_sprite_stand_left.frame = random.choice(range(self.stand_tiles[0]))
        self.player_sprite_stand_left.scale = SPRITE_SCALING
        self.player_sprite_stand_left.center_x = self.start_x
        self.player_sprite_stand_left.bottom = self.start_y
        self.player_sprite_list.append(self.player_sprite_stand_left)

        list_imgs = self._load_tiles(self.walk_tiles)
        self.player_sprite_walk = arcade.AnimatedWalkingSprite()
        self.player_sprite_walk.stand_right_textures = []
        self.player_sprite_walk.stand_left_textures = []
        self.player_sprite_walk.walk_right_textures = []
        self.player_sprite_walk.walk_left_textures = []
        self.player_sprite_walk.texture_change_distance = 2.5*RF
        self.player_sprite_walk.scale = SPRITE_SCALING
        self.player_sprite_walk.center_x = self.start_x
        self.player_sprite_walk.bottom = self.start_y

        for t in arcade.draw_commands.load_textures(self.walk_file, list_imgs):
            self.player_sprite_walk.walk_left_textures.append(t)

        for t in arcade.draw_commands.load_textures(self.walk_file, list_imgs, mirrored=True):
            self.player_sprite_walk.walk_right_textures.append(t)

        loads = arcade.draw_commands.load_textures(self.walk_file, list_imgs)
        self.player_sprite_walk.stand_right_textures.append(loads[0])
        self.player_sprite_walk.stand_left_textures.append(loads[0])

        self.player_sprite_list.append(self.player_sprite_walk)

    def over(self, player):
        self_sprite = self.player_sprite_walk
        player_sprite = player.player_sprite_walk
        if self_sprite.left < player_sprite.center_x:
            if self_sprite.right > player_sprite.center_x:
                if self_sprite.bottom < player_sprite.center_y:
                    if self_sprite.top > player_sprite.center_y:
                        if not player.jumping:
                            return self.level == player.level
        return False

    def draw(self):
        if self.hiden:
            return
        if self.player_inside:
            if self.player_sprite_walk.state == arcade.sprite.FACE_LEFT:
                t = self.player_inside.player_sprite_stand_right
            else:
                t = self.player_inside.player_sprite_stand_left
            c = self.player_sprite_stand_right
            arcade.draw_texture_rectangle(c.center_x, c.center_y + 80, t.width, t.height, t._texture)
        if self.player_sprite_walk.change_x:
            self.player_sprite_walk.draw()

        else:
            if self.player_sprite_walk.state == arcade.sprite.FACE_LEFT:
                self.player_sprite_stand_right.draw()
            else:
                self.player_sprite_stand_left.draw()



    def update(self, delta_time):

        self.player_sprite_list.update()
        self.player_sprite_list.update_animation()

        if self.player_inside:
            self.player_inside.score += delta_time

        if self.teleport_time > 0:
            self.teleport_time -= delta_time
        else:
            self.teleport_time = 0

        level_y = self.level*RF*60
        pos_y = self.player_sprite_walk.bottom

        if self.jumping:
            change_y = self.player_sprite_walk.change_y + GRAVITY*delta_time
            self.move(y=change_y)
            if pos_y <= level_y and change_y < 0:
                self.jumping = False
        else:
            self.move(y=0)
            for sprite in self.player_sprite_list.sprite_list:
                sprite.bottom = level_y


    def move(self, x=None, y=None):
        for sprite in self.player_sprite_list.sprite_list:
            if not x is None:
                sprite.change_x = x
            if not y is None:
                sprite.change_y = y

    def reverse_move(self):
        for sprite in self.player_sprite_list.sprite_list:
            sprite.change_x = -sprite.change_x

    def set_pos(self, x, y, mid=False):
        for sprite in self.player_sprite_list.sprite_list:
            sprite.bottom = y
            if mid:
                sprite.center_x = x
            else:
                sprite.left = x

    def jump(self, up=True):
        if not self.jumping and (self.level + (1 if up else -1)) in range(5):
            self.jumping = True
            self.jumping_dir = 1 if up else .4
            for sprite in self.player_sprite_list.sprite_list:
                sprite.change_y = JUMP_SPEED * self.jumping_dir
            self.level += 1 if up else -1


class MyGame(arcade.Window):

    def __init__(self, width, height):
        super().__init__(width, height)

        self.background = None
        self.foreground_list = []
        self.sprites_list = None
        self.castle = Player(450, 1, 70, 64, [3, 1], SPRITE_CASTLE_STAND, [9, 1], SPRITE_CASTLE_WALK)

        self.players = []

        p1 = Player(420, 3, 40, 32, [9, 1], SPRITE_P1, [6, 1], SPRITE_P1W)
        p1.keys = [
            arcade.key.I,
            arcade.key.K,
            arcade.key.J,
            arcade.key.L,
        ]
        self.players.append(p1)

        p2 = Player(500, 3, 40, 32, [9, 1], SPRITE_P2, [6, 1], SPRITE_P2W)
        p2.keys = [
            arcade.key.W,
            arcade.key.S,
            arcade.key.A,
            arcade.key.D,
        ]
        self.players.append(p2)

        p3 = Player(580, 3, 40, 32, [9, 1], SPRITE_P3, [6, 1], SPRITE_P3W)
        p3.keys = [
            arcade.key.UP,
            arcade.key.DOWN,
            arcade.key.LEFT,
            arcade.key.RIGHT,
        ]
        self.players.append(p3)

        p4 = Player(660, 3, 40, 32, [9, 1], SPRITE_P4, [6, 1], SPRITE_P4W)
        p4.keys = [
            arcade.key.T,
            arcade.key.G,
            arcade.key.F,
            arcade.key.H,
        ]
        self.players.append(p4)

        self.holes = [
            [[390, 0, -1], [20, 1, 1]],
            [[360,1, -1], [50, 2, 1]],
            [[330,2, -1], [60, 3, 1]],
            [[330,3, -1], [60, 4, 1]],
            [[0, 0, 1], [398, 0, -1]],
            [[295, 4, -1], [295, 4, -1]],
        ]

        self.hc = []
        for _ in self.holes:
            self.hc.append(rand_color())

        for hole_a, hole_b in self.holes:
            hole_a[0] *= RF
            hole_b[0] *= RF
            hole_a[1] *= RF*60
            hole_b[1] *= RF*60

    def setup(self):
        self.background = arcade.load_texture(BG)
        self.foreground_list = [
            arcade.load_texture(F4),
            arcade.load_texture(F3),
            arcade.load_texture(F2),
            arcade.load_texture(F1),
            arcade.load_texture(F0),
        ]

        self.castle.setup()
        for player in self.players:
            player.setup()

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                                      SCREEN_WIDTH, SCREEN_HEIGHT, self.background)


        for level in reversed(range(5)):
            for p in self.players + [self.castle]:
                if p.level == level:
                    if not p.jumping:
                        p.draw()
            arcade.draw_texture_rectangle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                                          SCREEN_WIDTH, SCREEN_HEIGHT, self.foreground_list[level])

        for p in self.players + [self.castle]:
            if p.jumping:
                p.draw()

        arcade.draw_texture_rectangle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                                      SCREEN_WIDTH, SCREEN_HEIGHT, self.foreground_list[0])



        # for i, hole in enumerate(self.holes):
        #     hole_a, hole_b = hole
        #     arcade.draw_commands.draw_xywh_rectangle_filled(*hole_a[:2], 10, 10, self.hc[i])
        #     arcade.draw_commands.draw_xywh_rectangle_filled(*hole_b[:2], 10, 10, self.hc[i])

        ms = max([p.score for p in self.players])

        output_score = ''
        for i, player in enumerate(self.players):
            output_score += 'P%d%s:%03d     ' % (i+1, '$' if ms == player.score else ' ', player.score)
        arcade.draw_text(output_score, 20, SCREEN_HEIGHT - 20, arcade.color.BLACK, 16)

    def on_key_press(self, key, key_modifiers):
        for player in self.players:
            for i, k in enumerate(player.keys):
                if key == k:
                    if i == 0:
                        if self.castle.player_inside == player:
                            player.jump()
                            self.castle.jump()
                    if i == 1:
                        if self.castle.player_inside == player:
                            player.jump(False)
                            self.castle.jump(False)
                    if i == 2:
                        if self.castle.player_inside == player:
                            self.castle.move(x=-CASTLE_SPEED)
                            player.move(x=-CASTLE_SPEED)
                        else:
                            player.move(x=-PLAYER_SPEED)
                    if i == 3:
                        if self.castle.player_inside == player:
                            self.castle.move(x=CASTLE_SPEED)
                            player.move(x=CASTLE_SPEED)
                        else:
                            player.move(x=PLAYER_SPEED)

        if key == arcade.key.Q:
            exit()

    def on_key_release(self, key, key_modifiers):
        for player in self.players:
            for i, k in enumerate(player.keys):
                if key == k:
                    player.move(x=0)
                    if self.castle.player_inside == player:
                        self.castle.move(x=0)

    def update(self, delta_time):
        self.castle.update(delta_time)

        for player in self.players:
            player.update(delta_time)
            if self.castle.over(player) and self.castle.player_inside != player:
                self._set_player(player)
            self._check_teleport(player)
        self._check_teleport(self.castle)

    def _check_teleport(self, player):
        if player.teleport_time:
            return
        # player.move(x=0)
        for pair_hole in self.holes:
            for hole_in, hole_out in [pair_hole, [pair_hole[1], pair_hole[0]]]:
                p_sprite = player.player_sprite_walk
                if p_sprite.left < hole_in[0]:
                    if p_sprite.right > hole_in[0]:
                        if p_sprite.bottom <= hole_in[1]:
                            if p_sprite.top >= hole_in[1]:
                                if player.level == hole_in[1]/(RF*60):
                                    if player == self.castle:
                                        self.castle.move(x=0)
                                        self.castle.set_pos(hole_in[0] + hole_in[2]*42*RF, hole_in[1], True)
                                    elif not player.jumping:
                                        player.level = hole_out[1]/(RF*60)
                                        player.set_pos(hole_out[0] + hole_out[2]*22*RF, hole_out[1], True)
                                        player.teleport_time = .2
                                        if hole_out in self.holes[-1]:
                                            player.reverse_move()
                                        break

    def _set_player(self, player):
        if self.castle.player_inside:
            self.castle.player_inside.hiden = False
            self.castle.player_inside.jump()
            if not self.castle.level == 0:
                self.castle.player_inside.level = 0
            self.castle.move(x=0)
            # player.move(x=MOVEMENT_SPEED)
        self.castle.player_inside = player
        player.hiden = True

def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
