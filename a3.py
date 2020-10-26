import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfile
import sys
from PIL import Image, ImageTk
import json
import os


# ==============================  Support Start =========================================

# 游戏程序实例 供视图绑定响应事件
app = None
# 倒计时图片
time_pic = None
# 剩余步数图片
move_pic = None
# 剩余心图片
heart_pic = None
# 墙图片
wall_pic = None
# 钥匙图片
key_pic = None
# 用户图片
player_pic = None
# 门图片
door_pic = None
# 道具图片
move_increase_pic = None
# 草地图片
empty_pic = None
# 消耗时间
custom_time = "0s"
custom_time_second = 0
custom_time_minute = 0
custom_time_hour = 0
# 文件保存路径
FILE_PATH = None
# 文件名称
FILE_NAME = "MazeGame.txt"
# 文件前缀标识
FILE_PREFIX = "=== MazeGame Saved File ==="
# 最高分数
HIGH_SCORES = {}
# 剩余心跳数
Heart_Num = 3
# 用户上一步操作方向
Player_Prev_Pos = None

# 窗口大小
WINDOWS_WIDTH = 800
WINDOWS_HEIGHT = 600
# 任务1,2,3
TASK_ONE = 1
TASK_TWO = 2
TASK_MASTER = 3
# wsad的高度
WSAD_HEIGHT = 60
# 游戏地图颜色
BASE_COLOR = "light grey"
# BASE_COLOR = "White"
# 建筑颜色
MAP_COLOR = {
    "WALL": "Dark grey",
    "PLAYER": "Medium spring green",
    "MOVEINCREASE": "Orange",
    "KEY": "Yellow",
    "DOOR": "Dark Red"
}

GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "

DIRECTIONS = {
    "W": (-1, 0),
    "S": (1, 0),
    "D": (0, 1),
    "A": (0, -1)
}

INVESTIGATE = "I"
QUIT = "Q"
HELP = "H"

VALID_ACTIONS = [INVESTIGATE, QUIT, HELP]
VALID_ACTIONS.extend(list(DIRECTIONS.keys()))

HELP_MESSAGE = f"Here is a list of valid actions: {VALID_ACTIONS}"

INVALID = """That's invalid."""

WIN_TEXT = "You have won the game with your strength and honour!"

LOSE_TEST = "You have lost all your strength and honour."


class Display:
    """Display of the dungeon."""

    def __init__(self, game_information, dungeon_size):
        """Construct a view of the dungeon.

        Parameters:
            game_information (dict<tuple<int, int>: Entity): Dictionary
                containing the position and the corresponding Entity
            dungeon_size (int): the width of the dungeon.
        """
        self._game_information = game_information
        self._dungeon_size = dungeon_size

    def display_game(self, player_pos):
        """Displays the dungeon.

        Parameters:
            player_pos (tuple<int, int>): The position of the Player
        """
        dungeon = ""

        for i in range(self._dungeon_size):
            rows = ""
            for j in range(self._dungeon_size):
                position = (i, j)
                entity = self._game_information.get(position)

                if entity is not None:
                    char = entity.get_id()
                elif position == player_pos:
                    char = PLAYER
                else:
                    char = SPACE
                rows += char
            if i < self._dungeon_size - 1:
                rows += "\n"
            dungeon += rows
        print(dungeon)

    def display_moves(self, moves):
        """Displays the number of moves the Player has left.

        Parameters:
            moves (int): THe number of moves the Player can preform.
        """
        print(f"Moves left: {moves}" + "\n")


def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.

    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        file_contents = file.readlines()

    for i in range(len(file_contents)):
        line = file_contents[i].strip()
        row = []
        for j in range(len(file_contents)):
            row.append(line[j])
        dungeon_layout.append(row)

    return dungeon_layout
# ==============================  Support End   =========================================


# ============================== Model Class Start =========================================
class Entity(object):
    """
    # 实体类
    """
    def __init__(self):
        """
        初始化
        """
        self.collidable = True

    def get_id(self):
        """
        获取ID
        :return:
        """
        return "Entity"

    def set_collide(self, collidable):
        """
        设置是否可碰撞
        :param collidable:
        :return:
        """
        self.collidable = collidable

    def can_collide(self):
        """
        是否可碰撞
        :return:
        """
        return self.collidable

    def __str__(self):
        """
        打印
        :return:
        """
        return "Entity('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Entity('{}')".format(self.get_id())


class Wall(Entity):
    """
    # 墙
    """
    def __init__(self):
        """
        初始化
        """
        super().__init__()
        self.collidable = False

    def get_id(self):
        """
        获取ID
        :return:
        """
        return "#"

    def __str__(self):
        """
        打印
        :return:
        """
        return "Wall('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Wall('{}')".format(self.get_id())


class Item(Entity):
    """
    # 抽象子类
    """
    def on_hit(self, game):
        """
        碰撞
        :param game:
        :return:
        """
        raise NotImplementedError

    def __str__(self):
        """
        打印
        :return:
        """
        return "Item('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Item('{}')".format(self.get_id())


class Key(Item):
    """
    # 解锁门
    """
    def get_id(self):
        """
        获取ID
        :return:
        """
        return "K"

    def on_hit(self, game):
        """
        # 玩家拿到钥匙 钥匙添加到玩家的存货中 并从地图中移除
        :param game:
        :return:
        """
        # 道具放入玩家背包
        game.get_player().add_item(self)
        # 从地图中删除 TODO 只允许存在一个K 否则会全部删除
        positions = game.get_positions('K')
        del game.get_game_information()[positions[0]]

    def __str__(self):
        """
        打印
        :return:
        """
        return "Key('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Key('{}')".format(self.get_id())


class MoveIncrease(Item):
    """
    # 增加用户步数的道具
    """
    def __init__(self, moves=5):
        """
        初始化
        :param moves:
        """
        super().__init__()
        self.moves = moves

    def get_id(self):
        """
        获取ID
        :return:
        """
        return "M"

    def on_hit(self, game):
        """
            # 玩家拿到此道具 物品添加到玩家的存货中 并从地图中移除 玩家步数增加指定的值
        :param game:
        :return:
        """
        # 玩家增加步数
        game.get_player().change_move_count(self.moves)
        # 道具放入玩家背包
        game.get_player().add_item(self)
        # 从地图中删除 TODO 只允许存在一个M 否则会全部删除
        positions = game.get_positions('M')
        del game.get_game_information()[positions[0]]

    def __str__(self):
        """
        打印
        :return:
        """
        return "MoveIncrease('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "MoveIncrease('{}')".format(self.get_id())


class Door(Entity):
    """
    # 允许玩家离开的门
    """
    def get_id(self):
        """
        获取ID
        :return:
        """
        return "D"

    def __str__(self):
        """
        打印
        :return:
        """
        return "Door('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Door('{}')".format(self.get_id())

    def on_hit(self, game):
        """
            # 当玩家有key时 游戏结束 没有key 提示You don’t have the key!
        :param game:
        :return:
        """
        products = game.get_player().get_inventory()
        is_has_key = False
        for product in products:
            if isinstance(product, Key):
                is_has_key = True
        if is_has_key:
            game.set_win(True)
        else:
            print("You don't have the key!")


class Player(Entity):
    """
    # 玩家
    """
    def __init__(self, max_movies):
        """
        初始化
        :param max_movies:
        """
        super().__init__()
        # 当前位置
        self.position = None
        # 最大可移动步数
        self.max_move_count = max_movies
        # 持有的物品
        self.product = []

    def get_id(self):
        """
        ID
        :return:
        """
        return "O"

    def __str__(self):
        """
        打印
        :return:
        """
        return "Player('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Player('{}')".format(self.get_id())

    def set_position(self, position):
        """
        # 设置Player的位置
        :param position:
        :return:
        """
        self.position = position

    def get_position(self):
        """
        # 设置Player的位置
        :return:
        """
        return self.position

    def change_move_count(self, number):
        """
            # 玩家捡到道具M 增加的步数
        :param number:
        :return:
        """
        self.max_move_count = self.max_move_count + number

    def moves_remaining(self):
        """
            # 返回代表玩家达到最大允许步数前的剩余步数
        :return:
        """
        return self.max_move_count

    def add_item(self, item):
        """
            # 给玩家的库存添加物品
        :param item:
        :return:
        """
        self.product.append(item)

    def get_inventory(self):
        """
            # 返回一个代表玩家库存的列表，如果玩家库存为空，返回一个空列表
        :return:
        """
        return self.product

    def is_get_key(self):
        for item in self.product:
            if isinstance(item, Key):
                return True

# ============================== Model Class End =========================================


# ============================== View Class Start =========================================
# class MainWindow(object):
#     """
#     主窗口
#     """
#     def __init__(self, game_logic, width=800, height=800, task=TASK_ONE):
#         # 屏幕宽度
#         self.width = width
#         # 屏幕高度
#         self.height = height
#         # 窗口模式
#         self.task = task
#         # 地图宽度
#         self.map_width = 600
#         # 地图的高度
#         self.map_height = 600
#         # 游戏信息封装实体
#         self.game_logic = game_logic
#         # 地牢建筑
#         self.map_info = game_logic.get_game_information()
#         # 地牢长度、宽度
#         self.map_count = game_logic.get_dungeon_size()
#         # 玩家起始位置
#         self.play_pos = game_logic.get_player().get_position()
#         # 主窗口
#         self.window = tk.Tk()
#         # 标题
#         self.window.title("Key Cave Adventure Game")
#         # 窗口大小
#         self.window.geometry("{}x{}".format(width, height))
#         # 添加组件
#         self.add_compent()
#         # 进入主循环
#         self.window.mainloop()
#
#     def add_compent(self):
#         # 最顶上的Label
#         self.label = tk.Label(self.window, text="Key Cave Adventure Game", bg="Medium spring green")
#         # label定位 顶部 X填充
#         self.label.pack(side=tk.TOP, fill=tk.X)
#
#         # TASK_ONE
#         if self.task == TASK_ONE:
#             # 游戏地图
#             self.canvas_map = tk.Canvas(self.window, bg=BASE_COLOR, width=self.map_width, height=self.height)
#             self.canvas_map.pack(side=tk.LEFT)
#             # 游戏键盘
#             self.canvas_wsad = tk.Canvas(self.window, bg="white", width=self.width - self.map_width, height=self.height)
#             self.canvas_wsad.pack(side=tk.RIGHT)
#             # w按键
#             self.canvas_wsad.create_rectangle(0 * (self.width - self.map_width)/3, self.height/3, 1 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT, fill=MAP_COLOR['WALL'])
#             self.canvas_wsad.create_text(0.5 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT/2, text="W", font="Calibri 20")
#             # s按键
#             self.canvas_wsad.create_rectangle(1 * (self.width - self.map_width)/3, self.height/3, 2 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT, fill=MAP_COLOR['WALL'])
#             self.canvas_wsad.create_text(1.5 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT/2, text="S", font="Calibri 20")
#             # n按键
#             self.canvas_wsad.create_rectangle(1 * (self.width - self.map_width)/3, self.height/3 - WSAD_HEIGHT, 2 * (self.width - self.map_width)/3, self.height/3, fill=MAP_COLOR['WALL'])
#             self.canvas_wsad.create_text(1.5 * (self.width - self.map_width)/3, self.height/3 - WSAD_HEIGHT/2, text="N", font="Calibri 20")
#             # e按键
#             self.canvas_wsad.create_rectangle(2 * (self.width - self.map_width)/3, self.height/3, 3 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT, fill=MAP_COLOR['WALL'])
#             self.canvas_wsad.create_text(2.5 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT/2, text="E", font="Calibri 20")
#
#             # 保存键盘坐标 确定用户点击是哪个键
#             self.canvas_wsad_pos = {
#                 "W": [0 * (self.width - self.map_width)/3, self.height/3, 1 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT],
#                 "S": [1 * (self.width - self.map_width)/3, self.height/3, 2 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT],
#                 "N": [1 * (self.width - self.map_width)/3, self.height/3 - WSAD_HEIGHT, 2 * (self.width - self.map_width)/3, self.height/3],
#                 "E": [2 * (self.width - self.map_width)/3, self.height/3, 3 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT]
#             }
#
#             # 游戏地图初始化
#             # 格子高度和宽度
#             self.item_height = self.map_height/self.map_count
#             self.item_width = self.map_width/self.map_count
#             for item_pos, item in self.map_info.items():
#                 x, y = item_pos
#                 if isinstance(item, Wall):
#                     print("WALL === {},{}".format(x, y))
#                     self.canvas_map.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width, (x + 1) * self.item_height, fill=MAP_COLOR["WALL"])
#                 elif isinstance(item, Key):
#                     print("Key === {},{}".format(x, y))
#                     self.canvas_map.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width, (x + 1) * self.item_height, fill=MAP_COLOR["KEY"], tag="key_pos")
#                     self.canvas_map.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Trash", font="Calibri 15", tag="key_font")
#                 elif isinstance(item, MoveIncrease):
#                     print("Move === {},{}".format(x, y))
#                     self.canvas_map.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width, (x + 1) * self.item_height, fill=MAP_COLOR["MOVEINCREASE"], tag="move_pos")
#                     self.canvas_map.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Banana", font="Calibri 15", tag="move_font")
#                 elif isinstance(item, Door):
#                     print("Door === {},{}".format(x, y))
#                     self.canvas_map.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width, (x + 1) * self.item_height, fill=MAP_COLOR["DOOR"], tag="door_pos")
#                     self.canvas_map.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Nest", font="Calibri 15", tag="door_font")
#                 else:
#                     print("No Right Entity...")
#             # 绘制人物坐标
#             player_x, player_y = self.play_pos
#             self.canvas_map.create_rectangle(player_y * self.item_width, player_x * self.item_height, (player_y + 1) * self.item_width,
#                                              (player_x + 1) * self.item_height, fill=MAP_COLOR["PLAYER"], tag="player_pos")
#             self.canvas_map.create_text((player_y + 0.5) * self.item_width, (player_x + 0.5) * self.item_height, text="Ibis",
#                                          font="Calibri 15", tag="player_font")
#
#             # 绑定用户鼠标/键盘事件
#             self.canvas_wsad.bind('<Button-1>', self.user_clicked_mouse)
#             # 让画布获得焦点,对于键盘
#             self.canvas_map.focus_set()
#             self.canvas_map.bind('<Key>', self.user_clicked_keyboard)
#
#         # TASK_TWO
#         elif self.task == TASK_TWO:
#             pass
#
#     # 根据用户点击屏幕坐标 计算用户点击的值
#     def user_clicked_mouse(self, event):
#         map = {
#             "W": "A",
#             "S": "S",
#             "N": "W",
#             "E": "D"
#         }
#         for direction, pos in self.canvas_wsad_pos.items():
#             if event.x > pos[0] and event.x < pos[2] and event.y > pos[1] and event.y < pos[3]:
#                 # W S N E 转换 W S A D
#                 direction = map[direction]
#                 # 用户逻辑处理
#                 self.user_input_handler(direction)
#
#     # 根据用户点击的键盘 计算用户点击的值
#     def user_clicked_keyboard(self, event):
#         if event.char in ['a', 'w', 's', 'd']:
#             self.user_input_handler(event.char.upper())
#
#     # 用户输入处理逻辑
#     def user_input_handler(self, direction):
#         global Player_Prev_Pos
#         print("用户往{}方向走了一步...".format(direction))
#         Player_Prev_Pos = direction
#         # 检查指定方向是否有实体
#         if not self.game_logic.collision_check(direction):
#             # 不会碰到实体 可能没有实体 或实体是道具
#             entity = self.game_logic.get_entity_in_direction(direction)
#             if not entity:
#                 # 没有实体 直接移动
#                 pass
#             else:
#                 # 道具 钥匙 或 门
#                 entity.on_hit(self.game_logic)
#                 # 判断是碰到什么实体 删除对应的图标 移动用户位置
#                 if isinstance(entity, Key):
#                     print("用户拿到钥匙...")
#                     self.canvas_map.delete("key_pos")
#                     self.canvas_map.delete("key_font")
#                 elif isinstance(entity, MoveIncrease):
#                     print("用户拿到道具，增加步数...")
#                     self.canvas_map.delete("move_pos")
#                     self.canvas_map.delete("move_font")
#                 elif isinstance(entity, Door):
#                     print("用户到达门...")
#                     # 检查用户是否有钥匙
#                     if self.game_logic.get_player().is_get_key():
#                         print("用户已拿到key，游戏胜利...")
#                         self.canvas_map.delete("door_pos")
#                         self.canvas_map.delete("door_font")
#                     else:
#                         print("用户未拿到key...")
#
#             # 移动用户位置 旧的位置删除 新的位置画出用户
#             self.canvas_map.delete("player_pos")
#             self.canvas_map.delete("player_font")
#             self.game_logic.move_player(direction)
#             player_x, player_y = self.game_logic.get_player().get_position()
#             self.canvas_map.create_rectangle(player_y * self.item_width, player_x * self.item_height,
#                                              (player_y + 1) * self.item_width,
#                                              (player_x + 1) * self.item_height, fill=MAP_COLOR["PLAYER"],
#                                              tag="player_pos")
#             self.canvas_map.create_text((player_y + 0.5) * self.item_width, (player_x + 0.5) * self.item_height,
#                                         text="Ibis",
#                                         font="Calibri 15", tag="player_font")
#         else:
#             # 墙
#             print(INVALID)
#         # 玩家步数+1
#         self.game_logic.get_player().max_move_count = self.game_logic.get_player().max_move_count - 1
#
#         # 检查游戏是否赢了
#         if self.game_logic.won():
#             print(WIN_TEXT)
#             messagebox.showinfo('You won!', 'You have finished the level!')
#             sys.exit()
#
#         # 检查用户步数是否耗尽
#         if self.game_logic.get_player().moves_remaining() < 1:
#             print(LOSE_TEST)
#             messagebox.showinfo('You lost!', LOSE_TEST)
#             sys.exit()


class AbstractGrid(tk.Canvas):
    """
    一个继承tk.Canvas类并实现大部分视图类功能的抽象类，
    包含行数（行数可能根据列数不同而不同），列数，长度，宽度，
    其中**kwargs表示所有被tk.Canvas类使用的变量也能被AbstractGrid类使用。
    """
    def __init__(self, master, rows, cols, width, height, **kwargs):
        print("==================AbstractGrid===========")
        print(kwargs)
        print(kwargs['bg'])
        super().__init__(master=master, width=width, height=height, bg=kwargs['bg'])
        # 父窗口
        self.master = master
        # 行
        self.rows = rows
        # 列
        self.cols = cols
        # 宽度
        self.width = width
        # 高度
        self.height = height
        # 参数
        self.args = kwargs
        # 背景色
        self.bg = kwargs['bg']
        print(self.args)
        # 画布
        # self.canvas = tk.Canvas(master=self.master, width=self.width, height=self.height)


class DungeonMap(AbstractGrid):
    """
    一个继承AbstractGrid类的视图类，实体在地图中用在不同的位置上（row,column）的有颜色的格子来表示，
    可以假设行数与列数在地图中相同（因为地图是正方形的）。
    使用tk.Canvas类中的create rectangle和create text方法来实现给实体代表的格子上添加实体名字的功能，
    并使用kwargs方法设定地图的背景色为light grey（亮灰色）。
    Size指地图中的行数（与列数相等），width指格子的宽和高的像素（pixel）。
    """
    def __init__(self, master, size, width=600, **kwargs):
        print("=============DungeonMap================")
        print(kwargs)
        print(kwargs['bg'])
        super().__init__(master, size, size, width*size, width*size, **kwargs)
        # 游戏地图初始化
        # 格子高度和宽度
        self.item_height = width
        self.item_width = width
        self.map_info = kwargs['map_info']
        self.play_pos = kwargs['player_pos']
        for item_pos, item in self.map_info.items():
            x, y = item_pos
            if isinstance(item, Wall):
                print("WALL === {},{}".format(x, y))
                self.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width,
                                                 (x + 1) * self.item_height, fill=MAP_COLOR["WALL"], tag="wall_pos_{}_{}".format(x, y))
            elif isinstance(item, Key):
                print("Key === {},{}".format(x, y))
                self.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width,
                                                 (x + 1) * self.item_height, fill=MAP_COLOR["KEY"], tag="key_pos")
                self.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Trash",
                                            font="Calibri 15", tag="key_font")
            elif isinstance(item, MoveIncrease):
                print("Move === {},{}".format(x, y))
                self.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width,
                                                 (x + 1) * self.item_height, fill=MAP_COLOR["MOVEINCREASE"],
                                                 tag="move_pos")
                self.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Banana",
                                            font="Calibri 15", tag="move_font")
            elif isinstance(item, Door):
                print("Door === {},{}".format(x, y))
                self.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width,
                                                 (x + 1) * self.item_height, fill=MAP_COLOR["DOOR"], tag="door_pos")
                self.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Nest",
                                            font="Calibri 15", tag="door_font")
            else:
                print("No Right Entity...")
        # 绘制人物坐标
        player_x, player_y = self.play_pos
        self.create_rectangle(player_y * self.item_width, player_x * self.item_height,
                                         (player_y + 1) * self.item_width,
                                         (player_x + 1) * self.item_height, fill=MAP_COLOR["PLAYER"], tag="player_pos")
        self.create_text((player_y + 0.5) * self.item_width, (player_x + 0.5) * self.item_height,
                                    text="Ibis",
                                    font="Calibri 15", tag="player_font")
        # 让画布获得焦点,对于键盘
        self.focus_set()
        self.bind('<Key>', self.user_clicked_keyboard)

    # 根据用户点击的键盘 计算用户点击的值
    def user_clicked_keyboard(self, event):
        if event.char in ['a', 'w', 's', 'd']:
            app.user_input_handler(event.char.upper())


class AdvancedDungeonMap(DungeonMap):
    """
    游戏地图增强类 将格子转换成图片
    """
    def __init__(self, master, size, width=600, **kwargs):
        print("================AdvancedDungeonMap==============")
        print(width*size)
        print(kwargs)
        print(kwargs['bg'])
        super().__init__(master=master, size=size, width=width, **kwargs)

        # 背景改为草地
        img_empty = Image.open("./images/empty.png")
        img_empty = img_empty.resize((self.item_width, self.item_height))
        global empty_pic
        empty_pic = ImageTk.PhotoImage(img_empty)
        # self.create_image(0, 0, anchor=tk.NW, image=empty_pic)
        for x in range(size):
            for y in range(size):
                if not self.map_info.get((x, y), None):
                    # 草地
                    self.create_image(y * self.item_width, x * self.item_width, anchor=tk.NW, image=empty_pic)
        # 所有墙坐标
        wall_pos = []
        for item_pos, item in self.map_info.items():
            x, y = item_pos
            if isinstance(item, Wall):
                print("WALL === {},{}".format(x, y))
                # self.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width,
                #                                  (x + 1) * self.item_height, fill=MAP_COLOR["WALL"])
                img1 = Image.open("./images/wall.gif")
                img1 = img1.resize((self.item_width, self.item_height))
                global wall_pic
                wall_pic = ImageTk.PhotoImage(img1)
                wall_pos.append((y * self.item_width, x * self.item_height))
                self.create_image(y * self.item_width, x * self.item_height, anchor=tk.NW, image=wall_pic)
            elif isinstance(item, Key):
                print("Key === {},{}".format(x, y))
                # self.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width,
                #                                  (x + 1) * self.item_height, fill=MAP_COLOR["KEY"], tag="key_pos")
                # self.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Trash",
                #                             font="Calibri 15", tag="key_font")
                img2 = Image.open("./images/key.gif")
                img2 = img2.resize((self.item_width, self.item_height))
                global key_pic
                key_pic = ImageTk.PhotoImage(img2)

                self.create_image(y * self.item_width, x * self.item_height, anchor=tk.NW, image=key_pic, tag="key_pos")
            elif isinstance(item, MoveIncrease):
                print("Move === {},{}".format(x, y))
                # self.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width,
                #                                  (x + 1) * self.item_height, fill=MAP_COLOR["MOVEINCREASE"],
                #                                  tag="move_pos")
                # self.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Banana",
                #                             font="Calibri 15", tag="move_font")
                img3 = Image.open("./images/moveIncrease.gif")
                img3 = img3.resize((self.item_width, self.item_height))
                global move_increase_pic
                move_increase_pic = ImageTk.PhotoImage(img3)
                self.create_image(y * self.item_width, x * self.item_height, anchor=tk.NW, image=move_increase_pic, tag="move_pos")
            elif isinstance(item, Door):
                # print("Door === {},{}".format(x, y))
                # self.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width,
                #                                  (x + 1) * self.item_height, fill=MAP_COLOR["DOOR"], tag="door_pos")
                # self.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Nest",
                #                             font="Calibri 15", tag="door_font")
                img4 = Image.open("./images/door.gif")
                img4 = img4.resize((self.item_width, self.item_height))
                global door_pic
                door_pic = ImageTk.PhotoImage(img4)
                self.create_image(y * self.item_width, x * self.item_height, anchor=tk.NW, image=door_pic, tag="door_pos")
            else:
                print("No Right Entity...")
        # 字删掉
        self.delete("player_font")
        self.delete("key_font")
        self.delete("move_font")
        self.delete("door_font")
        # 绘制墙
        print(wall_pos)
        for x, y in wall_pos:
            self.create_image(x, y, anchor=tk.NW, image=wall_pic)
        # 绘制人物坐标
        player_x, player_y = self.play_pos
        # self.create_rectangle(player_y * self.item_width, player_x * self.item_height,
        #                                  (player_y + 1) * self.item_width,
        #                                  (player_x + 1) * self.item_height, fill=MAP_COLOR["PLAYER"], tag="player_pos")
        img5 = Image.open("./images/player.gif")
        img5 = img5.resize((self.item_width, self.item_height))
        global player_pic
        player_pic = ImageTk.PhotoImage(img5)
        self.create_image(player_y * self.item_width, player_x * self.item_height, anchor=tk.NW, image=player_pic, tag="player_pos")


class KeyPad(AbstractGrid):
    """
    一个继承AbstractGrid类的代表界面中wsad软键盘的视图类
    使用tk.Canvas类中的create rectangle和create text方法来实现给每个方向键代表的格子上叠加方向字wsad的功能。
    """
    def __init__(self, master, rows, colums, width=200, height=100, **kwargs):
        super().__init__(master, rows, colums, width*colums, height*rows, **kwargs)

        # 游戏键盘
        # w按键
        self.create_rectangle(0 * width, height*rows*2/5, 1 * width, height*rows*2/5 + height, fill=MAP_COLOR['WALL'])
        self.create_text(0.5 * width, height*rows*2/5 + height / 2, text="W", font="Calibri 20")
        # s按键
        self.create_rectangle(1 * width, height*rows*2/5, 2 * width, height*rows*2/5 + height, fill=MAP_COLOR['WALL'])
        self.create_text(1.5 * width, height*rows*2/5 + height / 2, text="S", font="Calibri 20")
        # n按键
        self.create_rectangle(1 * width, height*rows*2/5 - height, 2 * width, height*rows*2/5, fill=MAP_COLOR['WALL'])
        self.create_text(1.5 * width, height*rows*2/5 - height / 2, text="N", font="Calibri 20")
        # e按键
        self.create_rectangle(2 * width, height*rows*2/5, 3 * width, height*rows*2/5 + height, fill=MAP_COLOR['WALL'])
        self.create_text(2.5 * width, height*rows*2/5 + height / 2, text="E", font="Calibri 20")

        # 保存键盘坐标 确定用户点击是哪个键
        self.canvas_wsad_pos = {
            "W": [0 * width, height*rows*2/5, 1 * width, height*rows*2/5 + height],
            "S": [1 * width, height*rows*2/5, 2 * width, height*rows*2/5 + height],
            "N": [1 * width, height*rows*2/5 - height, 2 * width, height*rows*2/5],
            "E": [2 * width, height*rows*2/5, 3 * width, height*rows*2/5 + height]
        }

        print(self.canvas_wsad_pos)

        # 绑定用户鼠标/键盘事件
        self.bind('<Button-1>', self.user_clicked_mouse)

    # 根据用户点击屏幕坐标 计算用户点击的值
    def user_clicked_mouse(self, event):
        map = {
            "W": "A",
            "S": "S",
            "N": "W",
            "E": "D"
        }
        for direction, pos in self.canvas_wsad_pos.items():
            if event.x > pos[0] and event.x < pos[2] and event.y > pos[1] and event.y < pos[3]:
                # W S N E 转换 W S A D
                direction = map[direction]
                # 用户逻辑处理
                app.user_input_handler(direction=direction)


class StatusBar(tk.Frame):
    """
        窗口底部状态条
    """
    def __init__(self, master, width, height, **kwargs):
        super().__init__(master=master, width=width, height=height, bg='White')
        # TASK2 底部状态栏分三块 宽度均分
        self.frame_1 = tk.Frame(master=self, width=width/3, height=height, bg="White")
        self.frame_2 = tk.Frame(master=self, width=width/3, height=height, bg="Red")
        self.frame_3 = tk.Frame(master=self, width=width/3, height=height, bg="Black")
        self.frame_1.pack(side=tk.LEFT, fill=tk.BOTH)
        self.frame_2.pack(side=tk.LEFT, fill=tk.BOTH)
        self.frame_3.pack(side=tk.LEFT, fill=tk.BOTH)
        # frame1 两个Button
        # self.button_new_game = tk.Button(master=self.frame_1, text="New game", bd='1', command=app.new_game)
        # self.button_game_over = tk.Button(master=self.frame_1, text="Quit", bd='1', command=app.quit)
        self.button_new_game = tk.Button(master=self.frame_1, text="New game", bd='1', width=10, height=1, command=app.new_game)
        self.button_game_over = tk.Button(master=self.frame_1, text="Quit", bd='1', width=10, height=1, command=app.quit)
        self.button_new_game.pack(side=tk.TOP, expand=True, padx=100)
        self.button_game_over.pack(side=tk.BOTTOM, expand=True, padx=100)
        # # frame2
        img = Image.open("./images/clock.gif")
        img = img.resize((60, 60))
        # TODO 定时器
        global time_pic, custom_time
        time_pic = ImageTk.PhotoImage(img)
        self.time = tk.Label(master=self.frame_2, text="Time elapsed \n {}".format(custom_time),
                             image=time_pic, compound="left", width=300, height=60, bg="White")
        self.time.pack(fill=tk.Y)
        self.time.after(1000, self.update_time)
        # frame3
        img2 = Image.open("./images/lightning.gif")
        img2 = img2.resize((40, 60))
        global move_pic
        move_pic = ImageTk.PhotoImage(img2)
        self.move = tk.Label(master=self.frame_3, text="Moves left \n {} moves remaining".format(app.get_player_move()),
                             image=move_pic, compound="left", width=300, height=60, bg="White")
        self.move.pack(fill=tk.Y)

    def update_time(self):
        global custom_time_hour, custom_time_minute, custom_time_second, custom_time
        custom_time_second = custom_time_second + 1
        if custom_time_second == 60:
            custom_time_minute = custom_time_minute + 1
            custom_time_second = 0
        if custom_time_minute == 60:
            custom_time_hour = custom_time_hour + 1
            custom_time_minute = 0
        # 更新时间
        custom_time = ""
        if custom_time_hour != 0:
            custom_time = custom_time + "{}h".format(custom_time_hour)
        if custom_time_minute != 0:
            custom_time = custom_time + " {}m".format(custom_time_minute)
        custom_time = custom_time + " {}s".format(custom_time_second)
        self.time['text'] = "Time elapsed \n {}".format(custom_time)

        self.time.after(1000, self.update_time)


class StatusBar2(tk.Frame):
    """
        窗口底部状态条
    """
    def __init__(self, master, width, height, **kwargs):
        super().__init__(master=master, width=width, height=height, bg='White')
        # TASK2 底部状态栏分三块 宽度均分
        self.frame_1 = tk.Frame(master=self, width=width/4, height=height, bg="White")
        self.frame_2 = tk.Frame(master=self, width=width/4, height=height, bg="Red")
        self.frame_3 = tk.Frame(master=self, width=width/4, height=height, bg="Black")
        self.frame_4 = tk.Frame(master=self, width=width/4, height=height, bg="White")
        self.frame_1.pack(side=tk.LEFT, fill=tk.BOTH)
        self.frame_2.pack(side=tk.LEFT, fill=tk.BOTH)
        self.frame_3.pack(side=tk.LEFT, fill=tk.BOTH)
        self.frame_4.pack(side=tk.LEFT, fill=tk.BOTH)
        # frame1 两个Button
        # self.button_new_game = tk.Button(master=self.frame_1, text="New game", bd='1', command=app.new_game)
        # self.button_game_over = tk.Button(master=self.frame_1, text="Quit", bd='1', command=app.quit)
        self.button_new_game = tk.Button(master=self.frame_1, text="New game", bd='1', width=10, height=1, command=app.new_game)
        self.button_game_over = tk.Button(master=self.frame_1, text="Quit", bd='1', width=10, height=1, command=app.quit)
        self.button_new_game.pack(side=tk.TOP, expand=True, padx=50)
        self.button_game_over.pack(side=tk.BOTTOM, expand=True)
        # # frame2
        img = Image.open("./images/clock.gif")
        img = img.resize((60, 60))
        # TODO 定时器
        global time_pic, custom_time
        time_pic = ImageTk.PhotoImage(img)
        self.time = tk.Label(master=self.frame_2, text="Time elapsed \n {}".format(custom_time),
                             image=time_pic, compound="left", width=200, height=60, bg="White")
        self.time.pack(fill=tk.Y)
        self.time.after(1000, self.update_time)
        # frame3
        img2 = Image.open("./images/lightning.gif")
        img2 = img2.resize((40, 60))
        global move_pic
        move_pic = ImageTk.PhotoImage(img2)
        self.move = tk.Label(master=self.frame_3, text="Moves left \n {} moves remaining".format(app.get_player_move()),
                             image=move_pic, compound="left", width=200, height=60, bg="White")
        self.move.pack(fill=tk.Y)
        # frame4
        img3 = Image.open("./images/lives.gif")
        img3 = img3.resize((60, 60))
        global heart_pic, Heart_Num
        heart_pic = ImageTk.PhotoImage(img3)
        self.canvas_heart = tk.Canvas(master=self.frame_4, width=60, height=60, bg="White")
        self.canvas_heart.create_image(0, 0, image=heart_pic, anchor=tk.NW)
        self.canvas_heart.pack(side=tk.LEFT, fill=tk.Y)
        self.heart_label = tk.Label(master=self.frame_4, width=100, text="Lives remaing:{}".format(Heart_Num), bg="White")
        self.heart_label.pack(side=tk.TOP, fill=tk.Y)
        self.user_heart_button = tk.Button(master=self.frame_4, width=100, text="Use life", command=app.use_life, bg="White")
        self.user_heart_button.pack(side=tk.BOTTOM, fill=tk.Y)

    def update_time(self):
        global custom_time_hour, custom_time_minute, custom_time_second, custom_time
        custom_time_second = custom_time_second + 1
        if custom_time_second == 60:
            custom_time_minute = custom_time_minute + 1
            custom_time_second = 0
        if custom_time_minute == 60:
            custom_time_hour = custom_time_hour + 1
            custom_time_minute = 0
        # 更新时间
        custom_time = ""
        if custom_time_hour != 0:
            custom_time = custom_time + "{}h".format(custom_time_hour)
        if custom_time_minute != 0:
            custom_time = custom_time + " {}m".format(custom_time_minute)
        custom_time = custom_time + " {}s".format(custom_time_second)
        self.time['text'] = "Time elapsed \n {}".format(custom_time)

        self.time.after(1000, self.update_time)
# ============================== View Class End =========================================


# ============================== Controller Class Start =========================================
class GameLogic(object):
    """
    # GameLogic类包含所有的游戏信息和游戏该怎么玩
    """
    def __init__(self, dungeon_name="game1.txt"):
        """Constructor of the GameLogic class.

        Parameters:
            dungeon_name (str): The name of the level.
        """
        # 地牢二维数组
        self._dungeon = load_game(dungeon_name)
        # 地牢宽度
        self._dungeon_size = len(self._dungeon)
        # 玩家
        self._player = Player(GAME_LEVELS[dungeon_name])
        # 地牢所有实体位置
        self._game_information = self.init_game_information()
        # 玩家输赢
        self._win = False

    def get_positions(self, entity):
        """ Returns a list of tuples containing all positions of a given Entity
             type.
        # 返回给定实体在地牢中的位置
        Parameters:
            entity (str): the id of an entity.

        Returns:
            )list<tuple<int, int>>): Returns a list of tuples representing the
            positions of a given entity id.
        """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def get_dungeon_size(self):
        """
        # 获取地牢的宽
        :return:
        """
        return self._dungeon_size

    def init_game_information(self):
        """
        # 返回一个包含位置和对应实体作为键值对的字典
        :return:
        """
        res = {}
        for i in range(len(self._dungeon)):
            for j in range(len(self._dungeon[i])):
                if self._dungeon[i][j] == "#":
                    entity = Wall()
                    res.update({
                        (i, j): entity
                    })
                elif self._dungeon[i][j] == "K":
                    entity = Key()
                    res.update({
                        (i, j): entity
                    })
                elif self._dungeon[i][j] == "M":
                    entity = MoveIncrease()
                    res.update({
                        (i, j): entity
                    })
                elif self._dungeon[i][j] == "D":
                    entity = Door()
                    res.update({
                        (i, j): entity
                    })
                elif self._dungeon[i][j] == "O":
                    self._player.set_position((i, j))
        return res

    def get_game_information(self):
        """
        # 返回一个包含位置和对应实体作为键值对的字典
        :return:
        """
        return self._game_information

    def get_player(self):
        """
         # 返回游戏的Player对象
        :return:
        """
        return self._player

    def get_entity(self, position):
        """
        # 返回实体在当前地牢的给定位置，实体在给定方向或者位置在地牢外这个方法应该返回None
        :param position:
        :return:
        """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """
         返回一个包含用户给定位置的实体，如果给定方向没有实体或在地牢外这个方法应返回None
        :param direction:
        :return:
        """
        row, colum = self._player.get_position()
        if direction == 'W':
            row = row - 1
        elif direction == 'S':
            row = row + 1
        elif direction == 'A':
            colum = colum - 1
        elif direction == 'D':
            colum = colum + 1
        return self._game_information.get((row, colum))

    def collision_check(self, direction):
        """
        # 当用户沿给定方向前进并不会碰到实体时返回False，否则返回True
        :param direction:
        :return:
        """
        row, colum = self._player.get_position()
        if direction == 'W':
            row = row - 1
        elif direction == 'S':
            row = row + 1
        elif direction == 'A':
            colum = colum - 1
        elif direction == 'D':
            colum = colum + 1
        if not self._game_information.get((row, colum)):
            # 没有实体
            return False
        if self._game_information.get((row, colum)).can_collide():
            # 可被碰撞的实体 钥匙 门 道具等
            return False
        return True

    def new_position(self, direction):
        """
        # 返回一个包含沿给定方向的新位置的元组
        :param direction:
        :return:
        """
        row, colum = self._player.get_position()
        if direction == 'W':
            row = row - 1
        elif direction == 'S':
            row = row + 1
        elif direction == 'A':
            colum = colum - 1
        elif direction == 'D':
            colum = colum + 1
        return row, colum

    def move_player(self, direction):
        """
        # 根据给定的方向更新玩家的位置
        :param direction:
        :return:
        """
        row, colum = self._player.get_position()
        if direction == 'W':
            row = row - 1
        elif direction == 'S':
            row = row + 1
        elif direction == 'A':
            colum = colum - 1
        elif direction == 'D':
            colum = colum + 1
        self._player.set_position((row, colum))

    def check_game_over(self):
        """
        # 检查游戏是否结束 如果结束了返回True 否则返回False
        :return:
        """
        if self._win or self.get_player().moves_remaining() < 1:
            return True
        else:
            return False

    def set_win(self, win):
        """
        # 设置游戏胜利状态为True或者False
        :param win:
        :return:
        """
        self._win = win

    def won(self):
        """
        # 返回游戏是否胜利
        :return:
        """
        return self._win


class GameApp(object):
    """
    GameApp类是控制器类，能控制视图类和模型类间的交流
    task用来选择模式，其中TASK_ONE是一些自定义的可以使游戏像示例图那样展示的常量
    dungeon_name是用来加载等级的文件名。
    """

    def __init__(self, task=TASK_ONE, dungeon_name="game2.txt"):
        # 任务
        self.task = task
        # 游戏地图
        self.dungeon_name = dungeon_name
        # 游戏初始化
        # self.game_logic = GameLogic(dungeon_name)
        # 创建游戏界面
        # main_window = MainWindow(task=task, game_logic=self.game_logic)

        # 主窗口
        self.window = tk.Tk()
        # 标题
        self.window.title("Key Cave Adventure Game")
        # 窗口大小
        self.window.geometry("{}x{}".format(WINDOWS_WIDTH, WINDOWS_HEIGHT))
        # 初始化游戏逻辑
        self.game_logic = GameLogic(dungeon_name=dungeon_name)

        # 更新app实例
        global app
        app = self

        # 添加组件
        self.add_component()

        # 添加菜单
        self.add_menu()

        # 进入主循环
        self.window.mainloop()

    def add_menu(self):
        # 添加菜单
        if self.task == TASK_ONE:
            pass
        elif self.task == TASK_TWO:
            menu_bar = tk.Menu(master=self.window)
            child_menu = tk.Menu(master=menu_bar)
            menu_bar.add_cascade(label="File", menu=child_menu)
            child_menu.add_command(label="New game", command=self.new_game)
            child_menu.add_command(label="Load game", command=self.load_game)
            child_menu.add_command(label="Save game", command=self.save_game)
            child_menu.add_command(label="Quit", command=self.window.destroy)
            self.window.config(menu=menu_bar)
        elif self.task == TASK_MASTER:
            # 添加最高分数
            menu_bar = tk.Menu(master=self.window)
            child_menu = tk.Menu(master=menu_bar)
            menu_bar.add_cascade(label="File", menu=child_menu)
            child_menu.add_command(label="New game", command=self.new_game)
            child_menu.add_command(label="Load game", command=self.load_game)
            child_menu.add_command(label="Save game", command=self.save_game)
            child_menu.add_command(label="High scores", command=self.show_high_score)
            child_menu.add_command(label="Quit", command=self.window.destroy)
            self.window.config(menu=menu_bar)
        else:
            print("错误的任务选型...")

    def show_high_score(self):
        # 展示最高分数的三人
        self.high_window = tk.Tk()
        label = tk.Label(master=self.high_window, text="High Scores", bg="Medium spring green")
        label.pack(fill=tk.X)
        show_user_info = ""
        global HIGH_SCORES
        for user, time in HIGH_SCORES.items():
            show_user_info = show_user_info + user + ":" + time + "\n"
        label2 = tk.Label(master=self.high_window, text=show_user_info, bg="White")
        label2.pack(fill=tk.X)
        button = tk.Button(master=self.high_window, text="Done", command=self.done_handler)
        button.pack()

    def done_handler(self):
        # Done处理
        self.high_window.destroy()

    def save_game(self):
        print("-----save_game---------")
        self.root = tk.Tk()

        tk.Label(self.root, text="目标路径:").grid(row=0, column=0)
        tk.Entry(self.root, textvariable=self.root).grid(row=0, column=1)
        tk.Button(self.root, text="路径选择", command=self.selectPath).grid(row=0, column=2)
        self.root.mainloop()

    def selectPath(self):
        global FILE_PATH
        # print(FILE_PATH)
        FILE_PATH = askdirectory()
        # print(FILE_PATH)
        self.root.destroy()
        file_saved = FILE_PATH + '/' + FILE_NAME
        with open(file_saved, 'w+') as f:
            # 文件加个统一前缀标识
            f.write(FILE_PREFIX + "\n")
            # 保存任务TASK
            f.write(str(self.task) + "\n")
            # 保存地图
            f.write(self.dungeon_name + "\n")
            # 保存用户位置
            f.write(json.dumps(self.game_logic.get_player().get_position()) + "\n")
            # 保存用户剩余步数
            f.write(str(self.get_player_move()) + "\n")
            # TODO 保存当前使用的时间
            global custom_time, custom_time_second, custom_time_minute, custom_time_hour
            f.write(str(custom_time) + ":" + str(custom_time_hour) + ":" + str(custom_time_minute) + ":" + str(custom_time_second) + "\n")
            # 用户已经拥有的道具
            for item in self.game_logic.get_player().product:
                f.write(str(item) + ":")

    def load_game(self):
        print("-----load_game---------")
        self.root = tk.Tk()

        tk.Label(self.root, text="目标路径:").grid(row=0, column=0)
        tk.Entry(self.root, textvariable=self.root).grid(row=0, column=1)
        tk.Button(self.root, text="路径选择", command=self.selectPath2).grid(row=0, column=2)
        self.root.mainloop()

    def selectPath2(self):
        global FILE_PATH
        FILE_PATH = askopenfile()
        self.root.destroy()
        print(FILE_PATH.name)
        file_is_exist = os.path.exists(str(FILE_PATH.name))
        if file_is_exist:
            try:
                with open(FILE_PATH.name, 'r') as f:
                    flag = f.readline().replace("\n", "")
                    if flag != FILE_PREFIX:
                        messagebox.showerror('文件加载!', '文件加载错误...请选择正确的游戏文件...')
                    self.task = int(f.readline().replace("\n", ""))
                    self.dungeon_name = f.readline().replace("\n", "")
                    player_pos = f.readline().replace("\n", "")
                    player_pos = json.loads(player_pos)
                    plyaer_move = int(f.readline().replace("\n", ""))
                    custom_time = f.readline().replace("\n", "").split(":")
                    products = f.readline().split(":")
                    self.recovery_game(player_pos, plyaer_move, custom_time, products)
            except Exception as e:
                # print(e.with_traceback())
                messagebox.showerror('文件加载!', '文件加载错误...请选择正确的游戏文件...')
        else:
            messagebox.showerror('文件加载!', '文件加载错误...该文件不存在...')

    # 恢复游戏
    def recovery_game(self, player_pos, plyaer_move, custom_timed, products):
        print("Load Game Start...")
        # 初始化游戏逻辑
        self.game_logic = GameLogic(dungeon_name=self.dungeon_name)
        self.game_logic.get_player().set_position(player_pos)
        self.game_logic.get_player().max_move_count = plyaer_move
        # 恢复计时器
        global custom_time, custom_time_second, custom_time_hour, custom_time_minute
        custom_time = custom_timed[0]
        custom_time_hour = int(custom_timed[1])
        custom_time_minute = int(custom_timed[2])
        custom_time_second = int(custom_timed[3])
        # TODO 使用时间
        # 重新加载窗口
        self.status_bar.destroy()
        self.canvas_key.destroy()
        self.canvas_map.destroy()
        self.label.destroy()
        self.add_component()
        # 地图删除用户已经使用的道具 加入用户背包
        for item in products:
            print(item)
            if item == str(Key()):
                self.canvas_map.delete("key_pos")
                self.game_logic.get_player().add_item(Key())
            elif item == str(MoveIncrease()):
                self.canvas_map.delete("move_pos")
                self.game_logic.get_player().add_item(MoveIncrease())

    def add_component(self):
        if self.task == TASK_ONE:
            # TASK 1
            # 最顶上的Label
            self.label = tk.Label(self.window, text="Key Cave Adventure Game", bg="Medium spring green")
            # label定位 顶部 X填充
            self.label.pack(side=tk.TOP, fill=tk.X)
            # 窗口宽800*600 分给游戏地图600*600 键盘200*600
            # 游戏每个格子的宽和高 = 600 / 地图size
            self.item_width = int(600 / self.game_logic.get_dungeon_size())
            self.item_height = int(600 / self.game_logic.get_dungeon_size())
            self.canvas_map = DungeonMap(self.window, self.game_logic.get_dungeon_size(), width=self.item_width,
                                         map_info=self.game_logic.get_game_information(),
                                         player_pos=self.game_logic.get_player().get_position(),
                                         bg=BASE_COLOR)
            self.canvas_map.pack(side=tk.LEFT)
            # 键盘 200*600  键盘宽为200/3 = 60  键盘高*rows=600
            self.canvas_key = KeyPad(self.window, 20, 3, width=60, height=30, bg='White')
            self.canvas_key.pack(side=tk.RIGHT)
        elif self.task == TASK_TWO:
            # TASK 2
            # 最顶上的Label
            self.label = tk.Label(self.window, text="Key Cave Adventure Game", bg="Medium spring green")
            # label定位 顶部 X填充
            self.label.pack(side=tk.TOP, fill=tk.X)
            # 底部状态栏
            self.status_bar = StatusBar(master=self.window, width=800, height=60)
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            # 窗口宽800*600 分给游戏地图500*500 键盘300*500
            # 游戏每个格子的宽和高 = 600 / 地图size
            self.item_width = int(500 / self.game_logic.get_dungeon_size())
            self.item_height = int(500 / self.game_logic.get_dungeon_size())
            self.canvas_map = AdvancedDungeonMap(self.window, self.game_logic.get_dungeon_size(), width=self.item_width,
                                         map_info=self.game_logic.get_game_information(),
                                         player_pos=self.game_logic.get_player().get_position(),
                                         bg=BASE_COLOR, tag="map")
            self.canvas_map.pack(side=tk.LEFT)
            # 键盘 300*500  键盘宽为300/3 = 100  键盘高*rows=500
            self.canvas_key = KeyPad(self.window, 20, 3, width=100, height=25, bg='White', tag="keypad")
            self.canvas_key.pack(side=tk.RIGHT)
        elif self.task == TASK_MASTER:
            # 最顶上的Label
            self.label = tk.Label(self.window, text="Key Cave Adventure Game", bg="Medium spring green")
            # label定位 顶部 X填充
            self.label.pack(side=tk.TOP, fill=tk.X)
            # 底部状态栏
            self.status_bar = StatusBar2(master=self.window, width=800, height=60)
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            # 窗口宽800*600 分给游戏地图500*500 键盘300*500
            # 游戏每个格子的宽和高 = 600 / 地图size
            self.item_width = int(500 / self.game_logic.get_dungeon_size())
            self.item_height = int(500 / self.game_logic.get_dungeon_size())
            self.canvas_map = AdvancedDungeonMap(self.window, self.game_logic.get_dungeon_size(), width=self.item_width,
                                         map_info=self.game_logic.get_game_information(),
                                         player_pos=self.game_logic.get_player().get_position(),
                                         bg=BASE_COLOR, tag="map")
            self.canvas_map.pack(side=tk.LEFT)
            # 键盘 300*500  键盘宽为300/3 = 100  键盘高*rows=500
            self.canvas_key = KeyPad(self.window, 20, 3, width=100, height=25, bg='White', tag="keypad")
            self.canvas_key.pack(side=tk.RIGHT)
        else:
            print("错误的任务选项...")

    # 用户输入处理逻辑
    def user_input_handler(self, direction):
        global Player_Prev_Pos
        print("用户往{}方向走了一步...".format(direction))
        Player_Prev_Pos = direction
        # 检查指定方向是否有实体
        if not self.game_logic.collision_check(direction):
            # 不会碰到实体 可能没有实体 或实体是道具
            entity = self.game_logic.get_entity_in_direction(direction)
            if not entity:
                # 没有实体 直接移动
                pass
            else:
                # 道具 钥匙 或 门
                entity.on_hit(self.game_logic)
                # 判断是碰到什么实体 删除对应的图标 移动用户位置
                if isinstance(entity, Key):
                    print("用户拿到钥匙...")
                    self.canvas_map.delete("key_pos")
                    self.canvas_map.delete("key_font")
                elif isinstance(entity, MoveIncrease):
                    print("用户拿到道具，增加步数...")
                    self.canvas_map.delete("move_pos")
                    self.canvas_map.delete("move_font")
                elif isinstance(entity, Door):
                    print("用户到达门...")
                    # 检查用户是否有钥匙
                    if self.game_logic.get_player().is_get_key():
                        print("用户已拿到key，游戏胜利...")
                        self.canvas_map.delete("door_pos")
                        self.canvas_map.delete("door_font")
                    else:
                        print("用户未拿到key...")
                else:
                    print("用户检测到未知实体...")

            # 移动用户位置 旧的位置删除 新的位置画出用户
            self.canvas_map.delete("player_pos")
            self.canvas_map.delete("player_font")
            self.game_logic.move_player(direction)
            # 背景增加草坪
            player_x, player_y = self.game_logic.get_player().get_position()
            if self.task == TASK_ONE:
                self.canvas_map.create_rectangle(player_y * self.item_width, player_x * self.item_height,
                                                 (player_y + 1) * self.item_width,
                                                 (player_x + 1) * self.item_height, fill=MAP_COLOR["PLAYER"],
                                                 tag="player_pos")
                self.canvas_map.create_text((player_y + 0.5) * self.item_width, (player_x + 0.5) * self.item_height,
                                            text="Ibis",
                                            font="Calibri 15", tag="player_font")
            elif self.task == TASK_TWO:
                self.canvas_map.create_image(player_y * self.item_width, player_x * self.item_height,anchor=tk.NW,
                                             image=empty_pic)
                self.canvas_map.create_image(player_y * self.item_width, player_x * self.item_height,anchor=tk.NW,
                                             image=player_pic, tag="player_pos")
            elif self.task == TASK_MASTER:
                self.canvas_map.create_image(player_y * self.item_width, player_x * self.item_height,anchor=tk.NW,
                                             image=empty_pic)
                self.canvas_map.create_image(player_y * self.item_width, player_x * self.item_height,anchor=tk.NW,
                                             image=player_pic, tag="player_pos")
        else:
            # 墙
            print(INVALID)
        # 玩家步数+1
        self.game_logic.get_player().max_move_count = self.game_logic.get_player().max_move_count - 1

        # 更新TASK2 MASTER剩余步数
        if self.task != TASK_ONE:
            self.status_bar.move['text'] = "Moves left \n {} moves remaining".format(app.get_player_move())

        # 检查游戏是否赢了
        if self.game_logic.won():
            print(WIN_TEXT)
            self.game_win_handler()

        # 检查用户步数是否耗尽
        if self.game_logic.get_player().moves_remaining() < 1:
            print(LOSE_TEST)
            self.game_over_handler()

    def use_life(self):
        # 用户使用心回退
        global Heart_Num, Player_Prev_Pos
        if Heart_Num > 0:
            # 用户恢复上一步位置 走反方向
            if Player_Prev_Pos == 'W':
                Player_Prev_Pos = 'S'
            elif Player_Prev_Pos == 'S':
                Player_Prev_Pos = 'W'
            elif Player_Prev_Pos == 'A':
                Player_Prev_Pos = 'D'
            elif Player_Prev_Pos == 'D':
                Player_Prev_Pos = 'A'
            else:
                print("Error direction...")
            self.user_input_handler(Player_Prev_Pos)
            # 用户步数 + 2
            self.game_logic.get_player().max_move_count = self.game_logic.get_player().max_move_count + 2
            self.status_bar.move['text'] = "Moves left \n {} moves remaining".format(app.get_player_move())
            # 心数减少1
            Heart_Num = Heart_Num - 1
            self.status_bar.heart_label['text'] = "Lives remaing:{}".format(Heart_Num)
        else:
            messagebox.showerror('使用生命失败！', '剩余生命数不足，无法使用生命!')

    def user_name_add(self):
        # 登记用户信息
        global HIGH_SCORES, SCORE_TMP
        user_name = self.name_entry.get()
        max_score = SCORE_TMP
        max_user = user_name
        if len(HIGH_SCORES) < 3:
            HIGH_SCORES[user_name] = SCORE_TMP
        else:
            for user, score in HIGH_SCORES.items():
                if self.compare_time(max_score, score):
                    max_score = score
                    max_user = user
            del HIGH_SCORES[max_user]
            HIGH_SCORES[user_name] = SCORE_TMP
        self.user_scores_window.destroy()
        res = messagebox.askyesno('You won!',
                                  'You have finished the level with a score of {}. \n Would you like to play again?'.format(
                                      SCORE_TMP))
        if res:
            self.new_game()
        else:
            sys.exit()

    # 游戏胜利处理
    def game_win_handler(self):
        global custom_time, HIGH_SCORES, SCORE_TMP
        if self.task == TASK_ONE:
            messagebox.showinfo('You won!', 'You have finished the level!')
            sys.exit()
        elif self.task == TASK_TWO:
            res = messagebox.askyesno('You won!', 'You have finished the level with a score of {}. \n Would you like to play again?'.format(custom_time))
            if res:
                self.new_game()
            else:
                sys.exit()
        elif self.task == TASK_MASTER:
            # 是否打破记录
            flag = False
            SCORE_TMP = custom_time
            for score in HIGH_SCORES.values():
                if self.compare_time(SCORE_TMP, score):
                    flag = True
            if flag or len(HIGH_SCORES) < 3:
                # 输入你的名字
                self.user_scores_window = tk.Tk()
                self.user_scores_window.title('You Win!')
                # 最顶上的Label
                label = tk.Label(self.user_scores_window, text="You won in {}! Enter your name:".format(custom_time), bg="Medium spring green")
                # label定位 顶部 X填充
                label.pack(side=tk.TOP, fill=tk.X)
                self.name_entry = tk.Entry(master=self.user_scores_window)
                self.name_entry.pack()
                button = tk.Button(master=self.user_scores_window, text="Enter", command=self.user_name_add)
                button.pack()
            else:
                res = messagebox.askyesno('You won!',
                                          'You have finished the level with a score of {}. \n Would you like to play again?'.format(
                                              custom_time))
                if res:
                    self.new_game()
                else:
                    sys.exit()
        else:
            print("错误的任务选型..")

    # 比较两个时间大小
    def compare_time(self, time1, time2):
        if time1 == time2:
            return False
        time1 = time1.replace("h", ":").replace("m", ":").replace("s", ":").split(":")
        time2 = time2.replace("h", ":").replace("m", ":").replace("s", ":").split(":")
        if len(time1) < len(time2):
            return True
        elif len(time1) > len(time2):
            return False
        else:
            for i in range(len(time1)):
                if int(time1[i]) < int(time2[i]):
                    return True
                elif int(time1[i]) > int(time2[i]):
                    return False
                else:
                    continue

    # 游戏结束处理逻辑
    def game_over_handler(self):
        global custom_time
        if self.task == TASK_ONE:
            messagebox.showinfo('You lost!', LOSE_TEST)
            sys.exit()
        elif self.task == TASK_TWO:
            res = messagebox.askyesno('You lost!',
                                      'You have finished the level with a score of {}. \n Would you like to play again?'.format(
                                          custom_time))
            if res:
                self.new_game()
            else:
                sys.exit()
        elif self.task == TASK_MASTER:
            res = messagebox.askyesno('You lost!',
                                      'You have finished the level with a score of {}. \n Would you like to play again?'.format(
                                          custom_time))
            if res:
                self.new_game()
            else:
                sys.exit()
        else:
            print("错误的任务选型..")

    # 开始新得游戏
    def new_game(self):
        print("New Game Start...")
        # 初始化游戏逻辑
        self.game_logic = GameLogic(dungeon_name=self.dungeon_name)
        # 初始化计时器
        global custom_time, custom_time_second, custom_time_hour, custom_time_minute
        custom_time = ""
        custom_time_hour = custom_time_second = custom_time_minute = 0
        # 重新加载窗口
        self.status_bar.destroy()
        self.canvas_key.destroy()
        self.canvas_map.destroy()
        self.label.destroy()
        self.add_component()

    # 游戏结束
    def quit(self):
        print("Game is over...")
        sys.exit()

    # 获取用户当前剩余步数
    def get_player_move(self):
        return self.game_logic.get_player().moves_remaining()

# ============================== Controller Class End =========================================


# ============================== Main Method ================================================
if __name__ == "__main__":
    # GameApp(dungeon_name="game1.txt", task=TASK_ONE)
    GameApp(dungeon_name="game2.txt", task=TASK_TWO)
    # 主窗口
    # window = tk.Tk()
    # 标题
    # window.title("Key Cave Adventure Game")
    # 窗口大小
    # window.geometry("{}x{}".format(WINDOWS_WIDTH, WINDOWS_HEIGHT))
    # 添加组件
    # game_logic = GameLogic()
    # 窗口宽800*600 分给游戏地图600*600 键盘200*600
    # 游戏每个格子的宽和高 = 600 / 地图size
    # item_width = int(600 / game_logic.get_dungeon_size())
    # item_height = int(600 / game_logic.get_dungeon_size())
    # canvas_map = AdvancedDungeonMap(window, game_logic.get_dungeon_size(), width=item_width,
    #                              map_info=game_logic.get_game_information(),
    #                              player_pos=game_logic.get_player().get_position(),
    #                              bg=BASE_COLOR)
    # canvas_map.pack()

    # m1 = Image.open("./images/wall.gif")
    # m1 = m1.resize((120, 120))
    # m2 = ImageTk.PhotoImage(m1)
    # map = tk.Canvas(master=window, width=600, height=600, bg="Red")
    # map.create_rectangle(0, 0, 180, 180, fill=MAP_COLOR["WALL"])
    # map.create_image(0, 0, anchor=tk.NW, image=m2)
    # map.pack()


    # status_bar = StatusBar(master=window, width=800, height=100)
    # status_bar.pack()
    # frame = tk.Frame(window, width=80, height=80)
    # img = Image.open("./images/clock.png")
    # img2 = img.resize((100, 100))
    # resource = ImageTk.PhotoImage(img2)
    # time = tk.Label(frame, text="Time elapsed \n 0m 31s",
    #                      image=resource, compound="left")
    # print(resource.width())
    # print(resource.height())
    # time.pack()
    # frame.pack()
    # 事件循环
    # window.mainloop()



