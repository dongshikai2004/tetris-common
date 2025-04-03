import pygame
from utils.font_manager import FontManager

class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.block_size = 30  # 方块大小，单位：像素
        
        # 游戏区域位置和大小 - 将左侧边距从200减小到150
        self.board_left = 150  # 从200减小到150，使游戏区域向左移动
        self.board_top = 50
        
        # 边框宽度
        self.border_width = 2
        
        # 颜色定义
        self.colors = [
            (0, 0, 0),       # 0: 空白
            (0, 240, 240),   # 1: I方块 - 青色
            (0, 0, 240),     # 2: J方块 - 蓝色
            (240, 160, 0),   # 3: L方块 - 橙色
            (240, 240, 0),   # 4: O方块 - 黄色
            (0, 240, 0),     # 5: S方块 - 绿色
            (160, 0, 240),   # 6: T方块 - 紫色
            (240, 0, 0),     # 7: Z方块 - 红色
            (255, 64, 64),   # 8: 爆炸方块 - 亮红色
            (64, 64, 255),   # 9: 冰冻方块 - 亮蓝色
            (255, 255, 64)   # 10: 彩虹方块 - 亮黄色
        ]
        
        # 使用字体管理器
        self.font_manager = FontManager()
    
    def render_game(self, board, current_block, next_block, score, level, mode, 
                   ghost_block=None, time_remaining=None, paused=False, 
                   return_confirm=False, game_over=False, combo_info=None, highest_score=0):
        """渲染整个游戏界面"""
        # 清空屏幕
        self.screen.fill((40, 44, 52))
        
        # 绘制游戏区域边框
        border_rect = pygame.Rect(
            self.board_left - self.border_width, 
            self.board_top - self.border_width,
            board.width * self.block_size + self.border_width * 2,
            board.height * self.block_size + self.border_width * 2
        )
        pygame.draw.rect(self.screen, (200, 200, 200), border_rect, self.border_width)
        
        # 绘制游戏板
        self._render_board(board)
        
        # 绘制幽灵方块（如果存在）- 先绘制幽灵方块，再绘制当前方块，这样当前方块会在上层
        if ghost_block and not paused:
            self._render_ghost_block(ghost_block)
        
        # 绘制当前方块
        self._render_block(current_block)
        
        # 绘制信息面板
        self._render_info_panel(next_block, score, level, mode, time_remaining, highest_score)
        
        # 渲染连消信息 - 放在最后确保它在最上层
        if combo_info and combo_info[1]:  # combo_info=(连消计数, 是否显示, 行数)
            combo_count = combo_info[0]
            lines_cleared = combo_info[2] if len(combo_info) > 2 else 0
            if combo_count > 0:  # 只要有连消就显示
                self._render_combo_effect(combo_count, lines_cleared)
        
        # 如果游戏暂停，显示暂停消息，不显示Q键提示
        if paused:
            self._render_overlay_message("游戏暂停", "按 P 键继续游戏", (255, 255, 255), show_q_tip=False)
        
        # 如果需要确认返回，显示确认消息，不显示Q键提示
        if return_confirm:
            self._render_overlay_message("确认返回主菜单?", "再次按 R 键确认返回", (255, 255, 0), show_q_tip=False)
        
        # 如果游戏结束，显示游戏结束消息
        if game_over:
            # 显示分数和最高分对比
            if score >= highest_score and highest_score > 0:
                self._render_overlay_message(f"游戏结束！得分: {score}", f"恭喜！创造新纪录！(原纪录: {highest_score})", (255, 100, 100), show_q_tip=True)
            else:
                self._render_overlay_message(f"游戏结束！得分: {score}", f"历史最高分: {highest_score}", (255, 100, 100), show_q_tip=True)
    
    def _render_board(self, board):
        """渲染游戏板"""
        for y in range(board.height):
            for x in range(board.width):
                cell_value = board.grid[y][x]
                if cell_value != 0:  # 不是空白格子
                    # 确定颜色索引
                    color_index = abs(cell_value)
                    if color_index >= len(self.colors):
                        color_index = 0
                    
                    # 绘制方块
                    rect = pygame.Rect(
                        self.board_left + x * self.block_size,
                        self.board_top + y * self.block_size,
                        self.block_size, self.block_size
                    )
                    pygame.draw.rect(self.screen, self.colors[color_index], rect)
                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)
                    
                    # 如果是特殊方块，绘制特殊标记
                    if cell_value < 0:
                        self._draw_special_marker(rect, cell_value)
    
    def _render_block(self, block):
        """渲染当前活动方块"""
        if not block:
            return
            
        color_index = abs(block.get_cell_value())
        if color_index >= len(self.colors):
            color_index = 0
            
        for x, y in block.get_occupied_cells():
            # 只渲染在游戏板范围内的部分
            if y >= 0:
                rect = pygame.Rect(
                    self.board_left + x * self.block_size,
                    self.board_top + y * self.block_size,
                    self.block_size, self.block_size
                )
                pygame.draw.rect(self.screen, self.colors[color_index], rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
                
                # 特殊方块标记
                if block.is_special():
                    self._draw_special_marker(rect, block.get_cell_value())
    
    def _render_ghost_block(self, ghost_block):
        """渲染幽灵方块 - 半透明提示块"""
        if not ghost_block:
            return
            
        # 获取颜色，但使用半透明效果
        color_index = abs(ghost_block.get_cell_value())
        if color_index >= len(self.colors):
            color_index = 0
        
        # 生成半透明颜色 - 保留原色调但降低饱和度和透明度
        base_color = self.colors[color_index]
        ghost_color = (base_color[0], base_color[1], base_color[2], 75)  # 添加透明度
        ghost_border = (200, 200, 200, 120)  # 边框颜色，半透明
        
        # 创建一个临时surface用于半透明渲染
        for x, y in ghost_block.get_occupied_cells():
            # 只渲染在游戏板范围内的部分
            if y >= 0:
                rect = pygame.Rect(
                    self.board_left + x * self.block_size,
                    self.board_top + y * self.block_size,
                    self.block_size, self.block_size
                )
                
                # 使用轮廓方式渲染幽灵方块，看起来更像"预览"
                pygame.draw.rect(self.screen, ghost_color, rect, 1)  # 1像素宽的边框
                smaller_rect = pygame.Rect(
                    rect.left + 2, rect.top + 2,
                    rect.width - 4, rect.height - 4
                )
                pygame.draw.rect(self.screen, ghost_color, smaller_rect, 1)
                
                # 还可以绘制十字线来增强可见性
                pygame.draw.line(self.screen, ghost_color,
                               (rect.left, rect.top), 
                               (rect.right, rect.bottom), 1)
                pygame.draw.line(self.screen, ghost_color,
                               (rect.left, rect.bottom), 
                               (rect.right, rect.top), 1)
    
    def _draw_special_marker(self, rect, value):
        """在特殊方块上绘制标记"""
        center_x = rect.x + rect.width // 2
        center_y = rect.y + rect.height // 2
        radius = min(rect.width, rect.height) // 4
        
        if value == -1:  # 爆炸方块
            pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius)
        elif value == -2:  # 彩虹方块
            # 绘制彩虹图案
            for i in range(3):
                pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius - i * 2, 1)
        elif value == -3:  # 冰冻方块
            # 绘制雪花图案
            pygame.draw.line(self.screen, (255, 255, 255), 
                            (center_x - radius, center_y), (center_x + radius, center_y), 1)
            pygame.draw.line(self.screen, (255, 255, 255), 
                            (center_x, center_y - radius), (center_x, center_y + radius), 1)
    
    def _render_info_panel(self, next_block, score, level, mode, time_remaining=None, highest_score=0):
        """渲染游戏信息面板"""
        # 下一个方块区域 - 调整水平位置以保持与游戏板的间距
        next_area_left = self.board_left + (self.block_size * 10) + 50
        next_area_top = self.board_top
        next_area_width = 150
        next_area_height = 100
        
        # 绘制下一个方块区域边框
        next_rect = pygame.Rect(next_area_left, next_area_top, next_area_width, next_area_height)
        pygame.draw.rect(self.screen, (200, 200, 200), next_rect, self.border_width)
        
        # 标题文本
        next_text = self.font_manager.render_text("下一个:", 24, (255, 255, 255))
        self.screen.blit(next_text, (next_area_left + 10, next_area_top + 10))
        
        # 绘制下一个方块
        if next_block:
            offset_x = next_area_left + next_area_width // 2 - len(next_block.shape[0]) * self.block_size // 2
            offset_y = next_area_top + 40
            
            color_index = abs(next_block.get_cell_value())
            if color_index >= len(self.colors):
                color_index = 0
                
            for y, row in enumerate(next_block.shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            offset_x + x * self.block_size,
                            offset_y + y * self.block_size,
                            self.block_size, self.block_size
                        )
                        pygame.draw.rect(self.screen, self.colors[color_index], rect)
                        pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
        
        # 分数和等级信息
        score_y = next_area_top + next_area_height + 30
        score_text = self.font_manager.render_text(f"分数: {score}", 36, (255, 255, 255))
        self.screen.blit(score_text, (next_area_left, score_y))
        
        # 添加最高分显示
        high_score_y = score_y + 40
        high_score_text = self.font_manager.render_text(f"最高分: {highest_score}", 36, (255, 215, 0))  # 用金色显示最高分
        self.screen.blit(high_score_text, (next_area_left, high_score_y))
        
        level_y = high_score_y + 40  # 调整等级显示位置
        level_text = self.font_manager.render_text(f"等级: {level}", 36, (255, 255, 255))
        self.screen.blit(level_text, (next_area_left, level_y))
        
        # 游戏模式
        mode_y = level_y + 40
        mode_names = {
            "classic": "经典模式",
            "timed": "限时模式",
            "challenge": "挑战模式"
        }
        mode_text = self.font_manager.render_text(f"模式: {mode_names.get(mode, mode)}", 36, (255, 255, 255))
        self.screen.blit(mode_text, (next_area_left, mode_y))
        
        # 如果是限时模式，显示剩余时间
        if time_remaining is not None:
            time_y = mode_y + 40
            minutes = int(time_remaining // 60)
            seconds = int(time_remaining % 60)
            
            # 根据剩余时间变化颜色
            time_color = (255, 255, 255)  # 默认白色
            if time_remaining < 30:  # 少于30秒显示红色
                time_color = (255, 50, 50)
            elif time_remaining < 60:  # 少于1分钟显示黄色
                time_color = (255, 255, 50)
            
            time_text = self.font_manager.render_text(f"剩余时间: {minutes:02d}:{seconds:02d}", 36, time_color)
            self.screen.blit(time_text, (next_area_left, time_y))
            
            # 调整控制说明的起始位置
            controls_y = time_y + 50
        else:
            # 没有时间显示时的控制说明位置
            controls_y = mode_y + 50
        
        # 控制说明
        controls = [
            "↑: 旋转", "←→: 移动", 
            "↓: 加速下落", "空格: 硬降",
            "R: 返回菜单(需确认)",
            "P: 暂停"
        ]
        
        # 计算所需总高度，确保不会超出屏幕底部
        screen_height = self.screen.get_height()
        line_height = 20
        total_controls_height = len(controls) * line_height
        
        # 如果预计位置会超出屏幕，则调整起始位置
        if controls_y + total_controls_height > screen_height - 10:
            controls_y = screen_height - total_controls_height - 10
        
        for i, control in enumerate(controls):
            control_text = self.font_manager.render_text(control, 18, (200, 200, 200))
            self.screen.blit(control_text, (next_area_left, controls_y + i * line_height))
    
    def _render_overlay_message(self, main_text, sub_text, color, show_q_tip=True):
        """渲染覆盖在游戏上的消息"""
        # 创建半透明背景
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # 半透明黑色
        self.screen.blit(overlay, (0, 0))
        
        # 渲染主要文本
        main_surface = self.font_manager.render_text(main_text, 48, color)
        main_rect = main_surface.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 30))
        self.screen.blit(main_surface, main_rect)
        
        # 渲染辅助文本
        sub_surface = self.font_manager.render_text(sub_text, 28, (200, 200, 200))
        sub_rect = sub_surface.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 30))
        self.screen.blit(sub_surface, sub_rect)
        
        # 添加Q键提示 - 只在需要时显示
        if show_q_tip:
            q_text = self.font_manager.render_text("按 Q 键返回菜单", 24, (255, 255, 0))
            q_rect = q_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 70))
            self.screen.blit(q_text, q_rect)
    
    def _render_combo_effect(self, combo_count, lines_cleared):
        """渲染连消特效 - 显示"perfect X 连消的行数" """
        # 增大连消显示的尺寸
        overlay_width = 250
        overlay_height = 100
        
        # 创建半透明效果层
        overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        
        # 根据连消数变化背景颜色
        if combo_count >= 5:
            bg_color = (160, 32, 240, 200)  # 紫色背景 - 高级连消
        elif combo_count >= 3:
            bg_color = (0, 0, 200, 200)  # 深蓝背景 - 中级连消
        else:
            bg_color = (50, 50, 150, 200)  # 蓝色背景 - 基础连消
        
        overlay.fill(bg_color)
        
        # 计算显示位置 - 在游戏区域中央偏上
        pos_x = self.board_left + (self.block_size * 10) // 2 - overlay_width // 2
        pos_y = self.board_top + 150  # 固定在游戏区域中上部
        
        # 设置边框颜色和宽度
        border_color = (255, 215, 0)  # 金色边框
        border_width = 3  # 边框宽度为3像素
        
        # 渲染"Perfect"文本
        perfect_text = self.font_manager.render_text("Perfect", 48, (255, 215, 0))  # 金色
        
        # 渲染连消行数文本
        combo_text = self.font_manager.render_text(f"x{combo_count} 连消{lines_cleared}行", 32, (255, 255, 255))
        
        # 计算文本位置，使其居中显示
        perfect_x = (overlay_width - perfect_text.get_width()) // 2
        combo_x = (overlay_width - combo_text.get_width()) // 2
        
        # 绘制文本到覆盖层
        overlay.blit(perfect_text, (perfect_x, 10))
        overlay.blit(combo_text, (combo_x, 60))
        
        # 绘制边框到覆盖层
        pygame.draw.rect(overlay, border_color, overlay.get_rect(), border_width)
        
        # 添加装饰性元素 - 四角星标记
        star_size = 10
        star_positions = [
            (border_width, border_width),  # 左上
            (overlay_width - border_width - star_size, border_width),  # 右上
            (border_width, overlay_height - border_width - star_size),  # 左下
            (overlay_width - border_width - star_size, overlay_height - border_width - star_size)  # 右下
        ]
        
        for x, y in star_positions:
            pygame.draw.polygon(overlay, (255, 255, 255), [
                (x + star_size//2, y),  # 上
                (x + star_size, y + star_size//2),  # 右
                (x + star_size//2, y + star_size),  # 下
                (x, y + star_size//2),  # 左
            ])
        
        # 绘制到屏幕 - 添加淡入淡出效果
        self.screen.blit(overlay, (pos_x, pos_y))
