class PhysicsEngine:
    def __init__(self):
        self.gravity_factor = 1.0  # 重力因子，可调整下落速度
        self.collision_buffer = 0  # 碰撞缓冲区大小
    
    def can_move(self, block, board, dx, dy):
        """检查方块是否可以移动到指定位置"""
        # 临时移动方块获取新位置
        block.x += dx
        block.y += dy
        
        # 检查新位置是否有效
        result = self.is_valid_position(block, board)
        
        # 恢复原位置
        block.x -= dx
        block.y -= dy
        
        return result
    
    def is_valid_position(self, block, board):
        """检查方块当前位置是否有效"""
        for x, y in block.get_occupied_cells():
            # 检查是否超出边界
            if not (0 <= x < board.width) or not (0 <= y < board.height):
                return False
            # 检查是否与已有方块重叠
            if y >= 0 and not board.is_cell_empty(x, y):
                return False
        return True
    
    def apply_gravity(self, block, delta_time):
        """应用重力效果，加速下落"""
        # 计算重力引起的下落距离
        gravity_movement = self.gravity_factor * delta_time / 1000
        
        # 将连续的重力转换为离散的网格移动
        # 当积累的重力效果足够移动一个格子时才移动
        block.gravity_accumulator = getattr(block, 'gravity_accumulator', 0) + gravity_movement
        
        # 如果累积的重力效果超过1，则下移方块
        grid_movement = int(block.gravity_accumulator)
        if grid_movement > 0:
            block.gravity_accumulator -= grid_movement
            return grid_movement
        return 0
    
    def handle_collisions(self, block, board):
        """处理碰撞效果"""
        # 检查方块与游戏板底部或其他方块的碰撞
        for x, y in block.get_occupied_cells():
            if y + 1 >= board.height or (y + 1 >= 0 and not board.is_cell_empty(x, y + 1)):
                # 碰撞动画效果可以在这里添加
                return True  # 发生碰撞
        return False  # 没有碰撞
