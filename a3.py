import tkinter as tk
from tkinter import messagebox
import sys
from PIL import Image, ImageTk


# ==============================  Support Start =========================================

# 游戏程序实例 供视图绑定响应事件
app = None

# 窗口大小
WINDOWS_WIDTH = 800
WINDOWS_HEIGHT = 600
# 任务1,2,3
TASK_ONE = 1
TASK_TWO = 2
TASK_THREE = 3
# wsad的高度
WSAD_HEIGHT = 60
# 游戏地图颜色
BASE_COLOR = "light grey"
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
class MainWindow(object):
    """
    主窗口
    """
    def __init__(self, game_logic, width=800, height=800, task=TASK_ONE):
        # 屏幕宽度
        self.width = width
        # 屏幕高度
        self.height = height
        # 窗口模式
        self.task = task
        # 地图宽度
        self.map_width = 600
        # 地图的高度
        self.map_height = 600
        # 游戏信息封装实体
        self.game_logic = game_logic
        # 地牢建筑
        self.map_info = game_logic.get_game_information()
        # 地牢长度、宽度
        self.map_count = game_logic.get_dungeon_size()
        # 玩家起始位置
        self.play_pos = game_logic.get_player().get_position()
        # 主窗口
        self.window = tk.Tk()
        # 标题
        self.window.title("Key Cave Adventure Game")
        # 窗口大小
        self.window.geometry("{}x{}".format(width, height))
        # 添加组件
        self.add_compent()
        # 进入主循环
        self.window.mainloop()

    def add_compent(self):
        # 最顶上的Label
        self.label = tk.Label(self.window, text="Key Cave Adventure Game", bg="Medium spring green")
        # label定位 顶部 X填充
        self.label.pack(side=tk.TOP, fill=tk.X)

        # TASK_ONE
        if self.task == TASK_ONE:
            # 游戏地图
            self.canvas_map = tk.Canvas(self.window, bg=BASE_COLOR, width=self.map_width, height=self.height)
            self.canvas_map.pack(side=tk.LEFT)
            # 游戏键盘
            self.canvas_wsad = tk.Canvas(self.window, bg="white", width=self.width - self.map_width, height=self.height)
            self.canvas_wsad.pack(side=tk.RIGHT)
            # w按键
            self.canvas_wsad.create_rectangle(0 * (self.width - self.map_width)/3, self.height/3, 1 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT, fill=MAP_COLOR['WALL'])
            self.canvas_wsad.create_text(0.5 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT/2, text="W", font="Calibri 20")
            # s按键
            self.canvas_wsad.create_rectangle(1 * (self.width - self.map_width)/3, self.height/3, 2 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT, fill=MAP_COLOR['WALL'])
            self.canvas_wsad.create_text(1.5 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT/2, text="S", font="Calibri 20")
            # n按键
            self.canvas_wsad.create_rectangle(1 * (self.width - self.map_width)/3, self.height/3 - WSAD_HEIGHT, 2 * (self.width - self.map_width)/3, self.height/3, fill=MAP_COLOR['WALL'])
            self.canvas_wsad.create_text(1.5 * (self.width - self.map_width)/3, self.height/3 - WSAD_HEIGHT/2, text="N", font="Calibri 20")
            # e按键
            self.canvas_wsad.create_rectangle(2 * (self.width - self.map_width)/3, self.height/3, 3 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT, fill=MAP_COLOR['WALL'])
            self.canvas_wsad.create_text(2.5 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT/2, text="E", font="Calibri 20")

            # 保存键盘坐标 确定用户点击是哪个键
            self.canvas_wsad_pos = {
                "W": [0 * (self.width - self.map_width)/3, self.height/3, 1 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT],
                "S": [1 * (self.width - self.map_width)/3, self.height/3, 2 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT],
                "N": [1 * (self.width - self.map_width)/3, self.height/3 - WSAD_HEIGHT, 2 * (self.width - self.map_width)/3, self.height/3],
                "E": [2 * (self.width - self.map_width)/3, self.height/3, 3 * (self.width - self.map_width)/3, self.height/3 + WSAD_HEIGHT]
            }

            # 游戏地图初始化
            # 格子高度和宽度
            self.item_height = self.map_height/self.map_count
            self.item_width = self.map_width/self.map_count
            for item_pos, item in self.map_info.items():
                x, y = item_pos
                if isinstance(item, Wall):
                    print("WALL === {},{}".format(x, y))
                    self.canvas_map.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width, (x + 1) * self.item_height, fill=MAP_COLOR["WALL"])
                elif isinstance(item, Key):
                    print("Key === {},{}".format(x, y))
                    self.canvas_map.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width, (x + 1) * self.item_height, fill=MAP_COLOR["KEY"], tag="key_pos")
                    self.canvas_map.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Trash", font="Calibri 15", tag="key_font")
                elif isinstance(item, MoveIncrease):
                    print("Move === {},{}".format(x, y))
                    self.canvas_map.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width, (x + 1) * self.item_height, fill=MAP_COLOR["MOVEINCREASE"], tag="move_pos")
                    self.canvas_map.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Banana", font="Calibri 15", tag="move_font")
                elif isinstance(item, Door):
                    print("Door === {},{}".format(x, y))
                    self.canvas_map.create_rectangle(y * self.item_width, x * self.item_height, (y + 1) * self.item_width, (x + 1) * self.item_height, fill=MAP_COLOR["DOOR"], tag="door_pos")
                    self.canvas_map.create_text((y + 0.5) * self.item_width, (x + 0.5) * self.item_height, text="Nest", font="Calibri 15", tag="door_font")
                else:
                    print("No Right Entity...")
            # 绘制人物坐标
            player_x, player_y = self.play_pos
            self.canvas_map.create_rectangle(player_y * self.item_width, player_x * self.item_height, (player_y + 1) * self.item_width,
                                             (player_x + 1) * self.item_height, fill=MAP_COLOR["PLAYER"], tag="player_pos")
            self.canvas_map.create_text((player_y + 0.5) * self.item_width, (player_x + 0.5) * self.item_height, text="Ibis",
                                         font="Calibri 15", tag="player_font")

            # 绑定用户鼠标/键盘事件
            self.canvas_wsad.bind('<Button-1>', self.user_clicked_mouse)
            # 让画布获得焦点,对于键盘
            self.canvas_map.focus_set()
            self.canvas_map.bind('<Key>', self.user_clicked_keyboard)

        # TASK_TWO
        elif self.task == TASK_TWO:
            pass

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
                self.user_input_handler(direction)

    # 根据用户点击的键盘 计算用户点击的值
    def user_clicked_keyboard(self, event):
        if event.char in ['a', 'w', 's', 'd']:
            self.user_input_handler(event.char.upper())

    # 用户输入处理逻辑
    def user_input_handler(self, direction):
        print("用户往{}方向走了一步...".format(direction))
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

            # 移动用户位置 旧的位置删除 新的位置画出用户
            self.canvas_map.delete("player_pos")
            self.canvas_map.delete("player_font")
            self.game_logic.move_player(direction)
            player_x, player_y = self.game_logic.get_player().get_position()
            self.canvas_map.create_rectangle(player_y * self.item_width, player_x * self.item_height,
                                             (player_y + 1) * self.item_width,
                                             (player_x + 1) * self.item_height, fill=MAP_COLOR["PLAYER"],
                                             tag="player_pos")
            self.canvas_map.create_text((player_y + 0.5) * self.item_width, (player_x + 0.5) * self.item_height,
                                        text="Ibis",
                                        font="Calibri 15", tag="player_font")
        else:
            # 墙
            print(INVALID)
        # 玩家步数+1
        self.game_logic.get_player().max_move_count = self.game_logic.get_player().max_move_count - 1

        # 检查游戏是否赢了
        if self.game_logic.won():
            print(WIN_TEXT)
            messagebox.showinfo('You won!', 'You have finished the level!')
            sys.exit()

        # 检查用户步数是否耗尽
        if self.game_logic.get_player().moves_remaining() < 1:
            print(LOSE_TEST)
            messagebox.showinfo('You lost!', LOSE_TEST)
            sys.exit()


class AbstractGrid(tk.Canvas):
    """
    一个继承tk.Canvas类并实现大部分视图类功能的抽象类，
    包含行数（行数可能根据列数不同而不同），列数，长度，宽度，
    其中**kwargs表示所有被tk.Canvas类使用的变量也能被AbstractGrid类使用。
    """
    def __init__(self, master, rows, cols, width, height, **kwargs):
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
                                                 (x + 1) * self.item_height, fill=MAP_COLOR["WALL"])
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
        self.frame_1 = tk.Frame(master=self, width=width/3, height=height)
        self.frame_2 = tk.Frame(master=self, width=width/3, height=height)
        self.frame_3 = tk.Frame(master=self, width=width/3, height=height)
        self.frame_1.pack(side=tk.LEFT)
        self.frame_2.pack(side=tk.LEFT)
        self.frame_3.pack(side=tk.LEFT)
        # frame1 两个Button
        self.button_new_game = tk.Button(master=self.frame_1, text="New game", bd='1', command=app.new_game)
        self.button_game_over = tk.Button(master=self.frame_1, text="Quit", bd='1', command=app.quit)
        self.button_new_game.pack(side=tk.TOP)
        self.button_game_over.pack(side=tk.BOTTOM)
        # frame2

        # frame3



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
        # 添加组件
        self.add_component()
        # TASK 1
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

        # TASK 2

        # 更新app实例
        global app
        app = self

        # 进入主循环
        # self.window.mainloop()

    def add_component(self):
        if self.task == TASK_ONE:
            pass
        elif self.task == TASK_TWO:
            pass
        elif self.task == TASK_THREE:
            pass
        else:
            print("错误的任务选项...")

    # 用户输入处理逻辑
    def user_input_handler(self, direction):
        print("用户往{}方向走了一步...".format(direction))
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
            player_x, player_y = self.game_logic.get_player().get_position()
            self.canvas_map.create_rectangle(player_y * self.item_width, player_x * self.item_height,
                                             (player_y + 1) * self.item_width,
                                             (player_x + 1) * self.item_height, fill=MAP_COLOR["PLAYER"],
                                             tag="player_pos")
            self.canvas_map.create_text((player_y + 0.5) * self.item_width, (player_x + 0.5) * self.item_height,
                                        text="Ibis",
                                        font="Calibri 15", tag="player_font")
        else:
            # 墙
            print(INVALID)
        # 玩家步数+1
        self.game_logic.get_player().max_move_count = self.game_logic.get_player().max_move_count - 1

        # 检查游戏是否赢了
        if self.game_logic.won():
            print(WIN_TEXT)
            messagebox.showinfo('You won!', 'You have finished the level!')
            sys.exit()

        # 检查用户步数是否耗尽
        if self.game_logic.get_player().moves_remaining() < 1:
            print(LOSE_TEST)
            messagebox.showinfo('You lost!', LOSE_TEST)
            sys.exit()

    # 开始新得游戏
    def new_game(self):
        print("New Game Start...")

    # 游戏结束
    def quit(self):
        print("Game is over...")

# ============================== Controller Class End =========================================


# ============================== Main Method ================================================
if __name__ == "__main__":
    GameApp(dungeon_name="game1.txt")
    # 主窗口
    window = tk.Tk()
    # 标题
    window.title("Key Cave Adventure Game")
    # 窗口大小
    window.geometry("{}x{}".format(WINDOWS_WIDTH, WINDOWS_HEIGHT))
    # 添加组件
    status_bar = StatusBar(master=window, width=800, height=200)
    status_bar.pack()
    # 事件循环
    window.mainloop()