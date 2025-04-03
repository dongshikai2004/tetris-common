class Block:
    def __init__(self, x, y, shape, color, block_type="normal"):
        self.x = x
        self.y = y
        self.shape = shape  # 二维数组表示方块形状
        self.color = color  # 颜色代码
        self.type = block_type  # 方块类型
        self.rotation = 0  # 当前旋转状态
        
    def __deepcopy__(self, memo):
        """支持深拷贝操作"""
        import copy
        # 创建一个新实例
        result = Block(
            self.x, 
            self.y, 
            copy.deepcopy(self.shape, memo),
            self.color,
            self.type
        )
        # 复制旋转状态
        result.rotation = self.rotation
        return result

    def get_occupied_cells(self):
        """获取当前方块占据的所有单元格坐标"""
        cells = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    # 根据旋转状态转换坐标
                    real_x, real_y = self._transform_coordinates(x, y)
                    cells.append((self.x + real_x, self.y + real_y))
        return cells
    
    def _transform_coordinates(self, x, y):
        """根据旋转状态转换相对坐标"""
        size = len(self.shape)
        if self.rotation == 0:
            return x, y
        elif self.rotation == 1:  # 90度
            return size - 1 - y, x
        elif self.rotation == 2:  # 180度
            return size - 1 - x, size - 1 - y
        elif self.rotation == 3:  # 270度
            return y, size - 1 - x
            
    def move(self, dx, dy):
        """移动方块"""
        self.x += dx
        self.y += dy
    
    def rotate(self, clockwise=True):
        """旋转方块"""
        if clockwise:
            self.rotation = (self.rotation + 1) % 4
        else:
            self.rotation = (self.rotation - 1) % 4
    
    def get_cell_value(self):
        """获取方块单元格的值（用于游戏板）"""
        if self.type == "normal":
            return self.color  # 正常方块返回颜色代码（正整数）
        else:
            # 特殊方块返回负值
            special_codes = {
                "exploding": -1,
                "rainbow": -2,
                "freezing": -3
            }
            return special_codes.get(self.type, -99)
    
    def is_special(self):
        """判断是否为特殊方块"""
        return self.type != "normal"
