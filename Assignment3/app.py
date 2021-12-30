"""
Simple 2d world where the player can interact with the items in the world.
"""
import random

__author__ = "ZILIANG WANG"
__date__ = "18/10/2019"
__version__ = "1.1.0"
__copyright__ = "The University of Queensland, 2019"

import math
import tkinter as tk

from typing import Tuple, List

import pymunk

from game.block import Block, MysteryBlock
from game.entity import Entity, BoundaryWall
from game.mob import Mob, CloudMob, Fireball
from game.item import DroppedItem, Coin
from game.view import GameView, ViewRenderer
from game.world import World
from game.util import get_collision_direction

from level import load_world, WorldBuilder
from player import Player

import json

BLOCK_SIZE = 2 ** 4
MAX_WINDOW_SIZE = (1080, math.inf)

GOAL_SIZES = {
    "flag": (0.2, 9),
    "tunnel": (2, 2)
}

BLOCKS = {
    '#': 'brick',
    '%': 'brick_base',
    '?': 'mystery_empty',
    '$': 'mystery_coin',
    '^': 'cube',
    'b': 'bounce',
    'I': 'tunnel',
    '=': 'flag_block',
    "S": 'switch'
}

ITEMS = {
    'C': 'coin',
    "*": "star"
}

MOBS = {
    '&': "cloud",
    '@': 'mushroom'
}


class myFireball(Mob):
    """The fireball mob is a moving entity that moves straight in a direction.

    When colliding with the player it will damage the player and explode.
    """
    _id = "myfireball"

    def __init__(self):
        super().__init__(self._id, size=(16, 16), weight=0, tempo=80)

    def on_hit(self, event: pymunk.Arbiter, data):
        world, player = data
        world.remove_mob(self)


class Mushroom(Mob):
    """
    """
    _id = "mushroom"
    _active = True

    def __init__(self, fire_range=10):
        super().__init__(self._id, size=(16, 16), weight=300, tempo=40)

    def is_active(self):
        return self._active

    def on_hit(self, event, block):
        direct = get_collision_direction(block, self)
        if direct == "L":
            self.set_tempo(40)
        elif direct == "R":
            self.set_tempo(-40)

    def on_hit_player(self, event, player):
        direct = get_collision_direction(player, self)
        if direct == "L":
            self.set_tempo(40)
            player.damage()
        elif direct == "R":
            self.set_tempo(-40)
            player.damage()
        elif direct == "A":
            self._active = False
            self.set_tempo(0)

    def step(self, time_delta, game_data):
        vx, vy = self.get_velocity()
        self.set_velocity((self.get_tempo(), vy))


class Star(DroppedItem):
    _id = "star"

    def __init__(self, duration=10):
        super().__init__()
        self._duration = duration

    def collect(self, player):
        player.invincible(self._duration * 1000)


class Bounce(Block):
    _id = "bounce"

    def __init__(self, drop: str = None, drop_range=(1, 1)):
        super().__init__()
        self._drop = drop
        self._drop_range = drop_range
        self._active = False

    def get_drops(self) -> Tuple[str, ...]:
        """Get the drops of the mystery block

        Returns:
            tuple<str, ...>: The item identifiers of the dropped items.
        """
        return (self._drop,) * random.randint(*self._drop_range)

    def _drop_items(self, world, drops: Tuple[str]):
        """Drop each of the dropped items into the world.

        Parameters:
            world (World): The world to place dropped items within.
            drops (tuple<str>): A tuple of item identifiers to place.
        """
        x, y = self.get_position()
        for drop in drops:
            if drop is not None:
                # world.add_item(create_item(drop), TODO: Make this non-hardcoded
                world.add_item(Coin(), x + random.randint(-10, 10), y - 25)

    def on_hit(self, event, data):
        """Callback collision with player event handler."""
        world, player = data
        # Ensure the bottom of the block is being hit
        if get_collision_direction(player, self) == "A":
            pos_x = player.get_velocity()[0]
            player.set_velocity((pos_x, -280))

    def is_active(self) -> bool:
        """(bool): Returns true if the block has not yet dropped items."""
        return self._active


class Tunnel(Block):
    _id = "tunnel"

    def __init__(self, drop: str = None, drop_range=(1, 1)):
        super().__init__()
        self._drop = drop
        self._drop_range = drop_range
        self._active = False


class Flagblock(Block):
    _id = "flag_block"

    def __init__(self, drop: str = None, drop_range=(1, 1)):
        super().__init__()
        self._drop = drop
        self._drop_range = drop_range
        self._active = False


class Switch(Block):
    _id = "switch"

    _press_stamp = 0

    def __init__(self):
        super().__init__()

    def press(self, n):
        self._press_stamp = 1000 * n

    def step(self, time_delta, game_data):
        self._press_stamp -= 1

    def isPressed(self):
        return self._press_stamp > 0


def create_block(world: World, block_id: str, x: int, y: int, *args):
    """Create a new block instance and add it to the world based on the block_id.

    Parameters:
        world (World): The world where the block should be added to.
        block_id (str): The block identifier of the block to create.
        x (int): The x coordinate of the block.
        y (int): The y coordinate of the block.
    """
    block_id = BLOCKS[block_id]
    if block_id == "mystery_empty":
        block = MysteryBlock()
    elif block_id == "mystery_coin":
        block = MysteryBlock(drop="coin", drop_range=(3, 6))
    elif block_id == "bounce":
        block = Bounce()
    elif block_id == "tunnel":
        block = Tunnel()
    elif block_id == "flag_block":
        block = Flagblock()
    elif block_id == "switch":
        block = Switch()
    else:
        block = Block(block_id)

    world.add_block(block, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_item(world: World, item_id: str, x: int, y: int, *args):
    """Create a new item instance and add it to the world based on the item_id.

    Parameters:
        world (World): The world where the item should be added to.
        item_id (str): The item identifier of the item to create.
        x (int): The x coordinate of the item.
        y (int): The y coordinate of the item.
    """
    item_id = ITEMS[item_id]
    if item_id == "coin":
        item = Coin()
    elif item_id == "star":
        item = Star(10)
    else:
        item = DroppedItem(item_id)

    world.add_item(item, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_mob(world: World, mob_id: str, x: int, y: int, *args):
    """Create a new mob instance and add it to the world based on the mob_id.

    Parameters:
        world (World): The world where the mob should be added to.
        mob_id (str): The mob identifier of the mob to create.
        x (int): The x coordinate of the mob.
        y (int): The y coordinate of the mob.
    """
    mob_id = MOBS[mob_id]
    if mob_id == "cloud":
        mob = CloudMob()
    elif mob_id == "fireball":
        mob = Fireball()
    elif mob_id == "mushroom":
        mob = Mushroom()
    elif mob_id == "myfireball":
        mob = myFireball()
    else:
        mob = Mob(mob_id, size=(1, 1))

    world.add_mob(mob, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_unknown(world: World, entity_id: str, x: int, y: int, *args):
    """Create an unknown entity."""
    world.add_thing(Entity(), x * BLOCK_SIZE, y * BLOCK_SIZE,
                    size=(BLOCK_SIZE, BLOCK_SIZE))


BLOCK_IMAGES = {
    "brick": "brick",
    "brick_base": "brick_base",
    "cube": "cube",
    "bounce": "bounce_block",
    "tunnel": "tunnel",
    "flag_block": "flag_block",
    "flag": "flag",
    "switch": "switch"
}

ITEM_IMAGES = {
    "coin": "coin_item",
    "star": "star"
}

MOB_IMAGES = {
    "cloud": "floaty",
    "fireball": "fireball_down",
    "mushroom": "mushroom",
    "myfireball": "fireball_down"
}


class MarioViewRenderer(ViewRenderer):
    """A customised view renderer for a game of mario."""

    @ViewRenderer.draw.register(Player)
    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:

        if shape.body.velocity.x >= 0:
            image = self.load_image("mario_right")
        else:
            image = self.load_image("mario_left")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="player")]

    @ViewRenderer.draw.register(MysteryBlock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_active():
            image = self.load_image("coin")
        else:
            image = self.load_image("coin_used")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(Tunnel)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        image = self.load_image("tunnel")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(Flagblock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        image = self.load_image("flag_block")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(Mushroom)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_active():
            image = self.load_image("mushroom")
        else:
            image = self.load_image("mushroom_squished")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="mob")]

    @ViewRenderer.draw.register(Switch)
    def _draw_mystery_block(self, instance: Switch, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.isPressed():
            image = self.load_image("switch_pressed")
        else:
            image = self.load_image("switch")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="mob")]


class WorldState:
    """
    """
    running: bool
    pendding: bool
    stop: bool

    def __init__(self):
        self._clear()
        self.stop = True

    def _clear(self):
        self.running = False
        self.pendding = False
        self.stop = False

    def isRunning(self):
        return self.running

    def setRunning(self, s: bool):
        self._clear()
        self.running = s

    def isPendding(self):
        return self.pendding

    def setPendding(self, s: bool):
        if self.running:
            self._clear()
            self.pendding = s

    def isStop(self):
        return self.stop

    def setStop(self, s: bool):
        self.stop = s


class Dialog(tk.Toplevel):
    """

    """

    def __init__(self, parent, title=None):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self, master):
        pass

    def buttonbox(self):
        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

    def validate(self):
        return 1  # override

    def apply(self):
        pass  # override


class ScoreDialog(Dialog):
    def body(self, master):
        f = open("score", "rt")
        content = f.readline()
        if content == "":
            tk.Label(master, text="empty").grid(row=0)
        else:
            tk.Label(master, text=content).grid(row=0)

        self.e1 = tk.Entry(master)
        return self.e1

    def apply(self):
        self.result = self.e1.get()


class MyDialog(Dialog):

    def body(self, master):
        tk.Label(master, text="world name:").grid(row=0)
        self.e1 = tk.Entry(master)
        self.e1.grid(row=0, column=1)
        return self.e1  # initial focus

    def apply(self):
        self.result = self.e1.get()


class pathDialog(Dialog):
    def body(self, master):
        tk.Label(master, text="path:").grid(row=0)
        self.e1 = tk.Entry(master)
        self.e1.grid(row=0, column=1)
        return self.e1  # initial focus

    def apply(self):
        self.result = self.e1.get()


class StatusBar(tk.Frame):
    _score: int = 0
    _percent = 1
    _realScore: int = 0

    def __init__(self, frame):
        f = tk.Frame(frame, height=60)
        self._f = f
        f.pack(side=tk.BOTTOM, fill=tk.BOTH)
        bar = tk.Label(f, bg="green")
        self._bar = bar
        self._empty = tk.Label(f, text="", bg="gray")
        self._realScoreBar = tk.Label(f, text="score")
        self._bar.place(x=0, y=0, relwidth=1, relheight=0.5)
        self._empty.place(x=0, y=0, relwidth=0, relheight=0.5)
        self._realScoreBar.place(x=0.9, rely=0.5, relwidth=0.5, relheight=0.5)
        # bar.pack(side=tk.BOTTOM, fill=tk.BOTH)

    def destroy(self):
        self._f.destroy()

    def setScore(self, score):
        self._score = score
        self.render()

    def setPercent(self, remain):
        self._percent = remain
        self.render()

    def setRealScore(self, realScore):
        self._realScore = realScore
        self.render()

    def render(self):
        self._realScoreBar["text"] = "score: " + str(self._realScore)
        color = "green"
        if self._percent < 0.25:
            color = "red"
        elif self._percent < 0.5:
            color = "orange"
        self._bar["bg"] = color
        self._bar.place(x=0, y=0, relwidth=self._percent, relheight=0.5)
        self._empty.place(relx=self._percent, y=0, relwidth=1 - self._percent, relheight=0.5)
        self._realScoreBar.place(x=0, rely=0.5, relwidth=1, relheight=0.5)


class UI:
    _frame: tk.Tk
    _t: tk.Text
    _statusBar: StatusBar

    _file_menu: tk.Menu

    def __init__(self, frame: tk.Tk):
        self._frame = frame
        self._t = tk.Text(frame, height=1)
        self._initMenu()

    def _initMenu(self):
        menubar = tk.Menu(frame)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.bind("<Button-1>", lambda e: frame.quit)

        file_menu.add_command(label='LOAD LEVEL', command=self._loadLevenCallback)
        file_menu.add_command(label='RESET LEVEL', command=self._resetLevelCallback)
        file_menu.add_command(label='High Scores', command=self.showHighScores)
        file_menu.add_separator()
        file_menu.add_command(label='EXIT', command=frame.quit)

        frame.config(menu=menubar)
        frame.title("Mario")

        frame.bind("<Leave>", self._leaveCallback)
        frame.bind("<Enter>", self._enterCallback)

    def showHighScores(self):
        ScoreDialog(self._frame)

    def initStatusBar(self):
        if hasattr(self, "_statusBar"):
            self._statusBar.destroy()
        self._statusBar = StatusBar(self._frame)

    def setScore(self, n):
        self._statusBar.setScore(n)

    def setPercent(self, p):
        self._statusBar.setPercent(p)

    def setRealScore(self, rs):
        self._statusBar.setRealScore(rs)

    def _loadLevenCallback(self):
        self.__loadLevelCallback()

    def _resetLevelCallback(self):
        self.__resetLevelCallback()

    def _leaveCallback(self, e):
        self.__leaveCallback(e)

    def _enterCallback(self, e):
        self.__enterCallback(e)

    def bindLoadLeven(self, f):
        self.__loadLevelCallback = f

    def bindResetLevel(self, f):
        self.__resetLevelCallback = f

    def bindLeave(self, f):
        self.__leaveCallback = f

    def bindEnter(self, f):
        self.__enterCallback = f


class MarioApp:
    """High-level app class for Mario, a 2d platformer"""

    _world: World
    _state: WorldState
    _view: GameView
    _ui: UI

    def __init__(self, master: tk.Tk, ui: UI, config):
        """Construct a new game of a MarioApp game.

        Parameters:
            master (tk.Tk): tkinter root widget
        """

        self._master = master
        self._state = WorldState()
        self._ui = ui

        world_config, player_config = config

        world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, int(world_config[0])), fallback=create_unknown)
        world_builder.register_builders(BLOCKS.keys(), create_block)
        world_builder.register_builders(ITEMS.keys(), create_item)
        world_builder.register_builders(MOBS.keys(), create_mob)
        self._builder = world_builder

        self._renderer = MarioViewRenderer(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)

        self.bind()
        self.start(world_config[1])

        master.update_idletasks()

    def reset_world(self, new_level):
        self._builder.clear()
        self._world = load_world(self._builder, new_level)
        self._world.add_player(self._player, BLOCK_SIZE, BLOCK_SIZE)
        self._setup_collision_handlers()
        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        if hasattr(self, '_view'):
            self._view.destroy()
        self._view = GameView(self._master, size, self._renderer)
        self._view.pack()
        self._ui.initStatusBar()
        self._player.connectUI(self._ui)

    def next_level(self):
        f = open("score", "w+")
        content = f.read()
        if content == "":
            content = []
            content.append(self._player.get_realscore())
            f.write(json.dumps(content))
        else:
            content = json.load(f)
            content.append(self._player.get_realscore())
            content.sort()
            if content.len() > 10:
                content.remove(content.len() - 1)
        f.write(json.dumps(content))

        if self._preMapName == "level2.txt":
            ScoreDialog()
            return
        self._builder.clear()
        self._world = load_world(self._builder, "level2.txt")
        self._world.add_player(self._player, BLOCK_SIZE, BLOCK_SIZE)
        self._setup_collision_handlers()
        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        if hasattr(self, '_view'):
            self._view.destroy()
        self._view = GameView(self._master, size, self._renderer)
        self._view.pack()

    def bind(self):
        """Bind all the keyboard events to their event handlers."""

        self._master.bind("<a>", self._move)
        self._master.bind("<d>", self._move)
        self._master.bind("<A>", self._move)
        self._master.bind("<D>", self._move)
        self._master.bind("<Left>", self._move)
        self._master.bind("<Right>", self._move)

        self._master.bind("<w>", self._jump)
        self._master.bind("<W>", self._jump)
        self._master.bind("<Up>", self._jump)

        self._master.bind("<S>", self._duck)
        self._master.bind("<s>", self._duck)
        self._master.bind("<Down>", self._duck)
        self._master.bind("<x>", self._attack)

        self._ui.bindLoadLeven(lambda: self.start(MyDialog(self._master).result))
        self._ui.bindResetLevel(lambda: self.start())
        self._ui.bindLeave(lambda e: self.pendding())
        self._ui.bindEnter(lambda e: self.conti())

    def redraw(self):
        """Redraw all the entities in the game canvas."""
        self._view.delete(tk.ALL)
        self._view.draw_entities(self._world.get_all_things())

    def scroll(self):
        """Scroll the view along with the player in the center unless
        they are near the left or right boundaries
        """
        x_position = self._player.get_position()[0]
        half_screen = self._master.winfo_width() / 2
        world_size = self._world.get_pixel_size()[0] - half_screen

        # Left side
        if x_position <= half_screen:
            self._view.set_offset((0, 0))

        # Between left and right sides
        elif half_screen <= x_position <= world_size:
            self._view.set_offset((half_screen - x_position, 0))

        # Right side
        elif x_position >= world_size:
            self._view.set_offset((half_screen - world_size, 0))

    def step(self):
        """Step the world physics and redraw the canvas."""
        if self._state.isRunning():
            data = (self._world, self._player)
            self._world.step(data)

            self.scroll()
            self.redraw()

            self._master.after(10, self.step)

    def start(self, mapName=None):
        if mapName == None and self._preMapName:
            self._player = Player(max_health=5)
            self.reset_world(self._preMapName)
            self._state.setRunning(True)
            self.step()
        else:
            self._preMapName = mapName
            self._player = Player(max_health=5)
            self.reset_world(mapName)
            self._state.setRunning(True)
            self.step()

    def pendding(self):
        self._state.setPendding(True)

    def conti(self):
        if self._state.isPendding():
            self._state.setRunning(True)
            self.step()

    def _move(self, event):
        move_pos = repr(event.char)
        move_pos = move_pos.replace("'", "")

        pos_y = self._player.get_velocity()[1]
        if move_pos == 'd' or (event.keysym == "Right") or move_pos == 'D':
            self._player.set_velocity((80, pos_y))
        elif move_pos == 'a' or (event.keysym == "Left") or move_pos == "A":
            self._player.set_velocity((-80, pos_y))

    def _jump(self, event):
        pos_x = self._player.get_velocity()[0]
        if not self._player.is_jumping():
            self._player.set_velocity((pos_x, -200))
            self._player.set_jumping(True)

    def _duck(self, event):
        if not self._player.is_jumping():
            pos_x = self._player.get_velocity()[0]
            self._player.set_velocity((pos_x, 100))

    def _attack(self, e):
        self._player.attack(self._world, myFireball())

    def _setup_collision_handlers(self):
        self._world.add_collision_handler("player", "item", on_begin=self._handle_player_collide_item)
        self._world.add_collision_handler("player", "block", on_begin=self._handle_player_collide_block,
                                          on_separate=self._handle_player_separate_block)
        self._world.add_collision_handler("player", "mob", on_begin=self._handle_player_collide_mob)
        self._world.add_collision_handler("mob", "block", on_begin=self._handle_mob_collide_block)
        self._world.add_collision_handler("mob", "mob", on_begin=self._handle_mob_collide_mob)
        self._world.add_collision_handler("mob", "item", on_begin=self._handle_mob_collide_item)

    def _handle_mob_collide_block(self, mob: Mob, block: Block, data,
                                  arbiter: pymunk.Arbiter) -> bool:
        mob_id = mob.get_id()
        block_id = block.get_id()
        if mob_id == "fireball" or mob_id == "myfireball":
            if block_id == "brick":
                self._world.remove_block(block)
            self._world.remove_mob(mob)
        if mob_id == "mushroom":
            mob.on_hit(arbiter, block)
        return True

    def _handle_mob_collide_item(self, mob: Mob, block: Block, data,
                                 arbiter: pymunk.Arbiter) -> bool:
        return False

    def _handle_mob_collide_mob(self, mob1: Mob, mob2: Mob, data,
                                arbiter: pymunk.Arbiter) -> bool:
        id1 = mob1.get_id()
        id2 = mob2.get_id()
        if id1 == "fireball" or id2 == "fireball" or id1 == "myfireball" or id2 == "myfireball":
            self._world.remove_mob(mob1)
            self._world.remove_mob(mob2)

        return False

    def _handle_player_collide_item(self, player: Player, dropped_item: DroppedItem,
                                    data, arbiter: pymunk.Arbiter) -> bool:
        """Callback to handle collision between the player and a (dropped) item. If the player has sufficient space in
        their to pick up the item, the item will be removed from the game world.

        Parameters:
            player (Player): The player that was involved in the collision
            dropped_item (DroppedItem): The (dropped) item that the player collided with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      (see http://www.pymunk.org/en/latest/pymunk.html#pymunk.Arbiter)
                                      NOTE: you probably won't need this
        Return:
             bool: False (always ignore this type of collision)
                   (more generally, collision callbacks return True iff the collision should be considered valid; i.e.
                   returning False makes the world ignore the collision)
        """

        item_id = dropped_item.get_id()
        if item_id == "coin":
            self._player.change_realscore(1)
        elif item_id == "star":
            dropped_item.collect(player)
        self._world.remove_item(dropped_item)
        return True

    def _handle_player_collide_block(self, player: Player, block: Block, data,
                                     arbiter: pymunk.Arbiter) -> bool:
        block_id = block.get_id()
        if block_id == "flag_block" or block_id == "tunnel":
            self.next_level()
        elif block_id == "switch":
            block.press(0.3)
        elif block_id == "bounce":
            block.on_hit(arbiter, (self._world, player))
        else:
            block.on_hit(arbiter, (self._world, player))

        player.set_jumping(False)
        return True

    def _handle_player_collide_mob(self, player: Player, mob: Mob, data,
                                   arbiter: pymunk.Arbiter) -> bool:
        if mob.get_id() == "fireball":
            mob.on_hit(arbiter, (self._world, player))
            player.damage()
        if mob.get_id() == "mushroom":
            mob.on_hit_player(arbiter, player)
        return True

    def _handle_player_separate_block(self, player: Player, block: Block, data,
                                      arbiter: pymunk.Arbiter) -> bool:
        return True


def parse(path):
    f = open(path, 'rt')
    sreadlines = f.readlines()
    ret = ([], [])
    world = False
    player = False
    for i in range(len(sreadlines)):
        l = sreadlines[i]
        if l.find("World") > 0:
            world = True
            player = False
            continue
        elif l.find("Player") > 0:
            world = False
            player = True
            continue
        if world:
            ret[0].append(l.split(":")[1].strip())
        else:
            ret[1].append(l.split(":")[1].strip())
    return ret


if __name__ == '__main__':
    frame = tk.Tk()
    ui = UI(frame)
    path = pathDialog(frame).result
    config = parse(path)
    app = MarioApp(frame, ui, config)
    frame.mainloop()
