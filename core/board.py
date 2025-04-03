class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        # 0表示空格，正整数表示不同颜色的方块，负整数表示特殊方块
    
    def clear(self):
        """清空游戏板"""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
    
    def is_valid_position(self, x, y):
        """检查坐标是否有效"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_cell_empty(self, x, y):
        """检查指定位置是否为空"""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] == 0
    
    def place_block(self, block):
        """将方块放置到游戏板上"""
        for cell_x, cell_y in block.get_occupied_cells():
            if self.is_valid_position(cell_x, cell_y):
                self.grid[cell_y][cell_x] = block.get_cell_value()
                
        # 如果是特殊方块，触发特殊效果
        if block.is_special():
            self._trigger_special_effect(block)
    
    def _trigger_special_effect(self, block):
        """触发特殊方块效果"""
        if block.type == "exploding":
            self._explode_area(block.x, block.y)
        elif block.type == "freezing":
            # 冰冻效果在Game类中处理
            pass
        elif block.type == "rainbow":
            self._rainbow_adapt(block)
    
    def _explode_area(self, center_x, center_y):
        """爆炸方块效果：清除周围的方块"""
        radius = 2
        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                if self.is_valid_position(x, y):
                    self.grid[y][x] = 0
    
    def _rainbow_adapt(self, block):
        """彩虹方块效果：适应周围颜色形成消除组合"""
        # 检测周围最常见的颜色并应用
        pass
    
    def clear_lines(self):
        """检查并消除已填满的行，返回消除的行数"""
        lines_to_clear = []
        for y in range(self.height):
            if all(cell != 0 for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        if not lines_to_clear:
            return 0  # 没有需要消除的行
        
        # 创建新的游戏板，只保留非满行
        new_grid = []
        for y in range(self.height):
            if y not in lines_to_clear:
                new_grid.append(self.grid[y])
        
        # 在顶部添加足够数量的空行
        empty_rows_needed = len(lines_to_clear)
        for _ in range(empty_rows_needed):
            new_grid.insert(0, [0 for _ in range(self.width)])
        
        # 更新游戏板
        self.grid = new_grid
        
        return len(lines_to_clear)
