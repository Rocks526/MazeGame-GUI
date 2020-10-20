import tkinter as tk
from PIL import Image, ImageTk


# ==============================  Support Start =========================================
TASK_ONE = 1
TASK_TWO = 2
TASK_THREE = 3

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


# ============================== Model Class End =========================================

# ============================== View Class Start =========================================
class MainWindow(object):
    """
    主窗口
    """
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        # 主窗口
        self.window = tk.Tk()
        # 标题
        self.window.title("Key Cave Adventure Game")
        # 窗口大小
        self.window.geometry("{}x{}".format(width, height))
        # 最顶上的Label
        self.label = tk.Label(self.window, text="Key Cave Adventure Game", bg="Medium spring green")
        # label定位 顶部 X填充
        self.label.pack(side=tk.TOP, fill=tk.X)
        # 进入主循环
        self.window.mainloop()


class AbstractGrid(tk.Canvas):
    """
    一个继承tk.Canvas类并实现大部分视图类功能的抽象类，
    包含行数（行数可能根据列数不同而不同），列数，长度，宽度，
    其中**kwargs表示所有被tk.Canvas类使用的变量也能被AbstractGrid类使用。
    """
    def __init__(self, master, rows, cols, width, height, **kwargs):
        super().__init__()
        self.master = master
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height


class DungeonMap(AbstractGrid):
    """
    一个继承AbstractGrid类的视图类，实体在地图中用在不同的位置上（row,column）的有颜色的格子来表示，
    可以假设行数与列数在地图中相同（因为地图是正方形的）。
    使用tk.Canvas类中的create rectangle和create text方法来实现给实体代表的格子上添加实体名字的功能，
    并使用kwargs方法设定地图的背景色为light grey（亮灰色）。
    Size指地图中的行数（与列数相等），width指格子的宽和高的像素（pixel）。
    """
    def __init__(self, master, size, width=600, **kwargs):
        super().__init__(master, size, size, width, width, **kwargs)


class KeyPad(AbstractGrid):
    """
    一个继承AbstractGrid类的代表界面中wsad软键盘的视图类
    使用tk.Canvas类中的create rectangle和create text方法来实现给每个方向键代表的格子上叠加方向字wsad的功能。
    """
    def __init__(self, master, width=200, height=100, **kwargs):
        super().__init__(master, 2, 3, width, height, **kwargs)


# ============================== View Class End =========================================

# ============================== Controller Class Start =========================================
class GameApp(object):
    """
    GameApp类是控制器类，能控制视图类和模型类间的交流
    task用来选择模式，其中TASK_ONE是一些自定义的可以使游戏像示例图那样展示的常量
    dungeon_name是用来加载等级的文件名。
    """
    def __init__(self, master, task=TASK_ONE, dungeon_name="game2.txt"):
        self.task = task
        # 游戏初始化
        self.gamelogic = GameLogic(dungeon_name)
        # 创建游戏界面
        main_window = MainWindow()

    # 开始游戏
    def start(self):
        pass


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
# ============================== Controller Class End =========================================


# ============================== Main Method ================================================
if __name__ == "__main__":
    game_app = GameApp(False)