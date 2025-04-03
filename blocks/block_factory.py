import random
from blocks.base_block import Block

class BlockFactory:
    def __init__(self):
        # 经典俄罗斯方块形状定义
        self.shapes = {
            'I': [[1, 1, 1, 1]],
            'J': [[1, 0, 0], [1, 1, 1]],
            'L': [[0, 0, 1], [1, 1, 1]],
            'O': [[1, 1], [1, 1]],
            'S': [[0, 1, 1], [1, 1, 0]],
            'T': [[0, 1, 0], [1, 1, 1]],
            'Z': [[1, 1, 0], [0, 1, 1]]
        }
        
        # 特殊形状
        self.special_shapes = {
            'plus': [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
            'u': [[1, 0, 1], [1, 1, 1]],
            'cross': [[0, 1, 0, 0], [1, 1, 1, 1], [0, 1, 0, 0]]
        }
        
        # 方块颜色
        self.colors = {
            'I': 1,  # 青色
            'J': 2,  # 蓝色
            'L': 3,  # 橙色
            'O': 4,  # 黄色
            'S': 5,  # 绿色
            'T': 6,  # 紫色
            'Z': 7   # 红色
        }
        
        # 特殊方块类型
        self.special_types = ["exploding", "rainbow", "freezing"]
    
    def create_block(self, game_mode):
        """根据游戏模式创建方块"""
        # 起始位置
        start_x = 4
        start_y = 0
        
        # 根据游戏模式决定方块生成策略
        if game_mode == "classic":
            return self._create_classic_block(start_x, start_y)
        elif game_mode == "challenge":
            # 挑战模式有10%概率生成特殊方块
            if random.random() < 0.1:
                return self._create_special_block(start_x, start_y)
            else:
                return self._create_classic_block(start_x, start_y)
        elif game_mode == "timed":
            # 限时模式方块更加多样
            if random.random() < 0.2:
                return self._create_special_block(start_x, start_y)
            else:
                return self._create_classic_block(start_x, start_y)
        
        # 默认返回经典方块
        return self._create_classic_block(start_x, start_y)
    
    def _create_classic_block(self, x, y):
        """创建经典俄罗斯方块"""
        shape_key = random.choice(list(self.shapes.keys()))
        shape = self.shapes[shape_key]
        color = self.colors[shape_key]
        return Block(x, y, shape, color)
    
    def _create_special_block(self, x, y):
        """创建特殊方块"""
        # 随机选择特殊形状
        if random.random() < 0.5:
            shape_key = random.choice(list(self.shapes.keys()))
            shape = self.shapes[shape_key]
        else:
            shape_key = random.choice(list(self.special_shapes.keys()))
            shape = self.special_shapes[shape_key]
        
        # 特殊方块有特殊颜色 (8-10)
        color = random.randint(8, 10)
        
        # 随机选择特殊类型
        special_type = random.choice(self.special_types)
        
        return Block(x, y, shape, color, special_type)
