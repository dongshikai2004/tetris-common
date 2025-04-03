import pygame
from core.board import Board
from blocks.block_factory import BlockFactory
from physics.engine import PhysicsEngine
from ui.renderer import GameRenderer
from sound.audio_manager import AudioManager
from analytics.statistics import GameStatistics
from copy import deepcopy

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.board = Board(10, 20)  # 10x20的游戏板
        self.block_factory = BlockFactory()
        self.physics = PhysicsEngine()
        self.renderer = GameRenderer(screen)
        self.audio = AudioManager()
        self.stats = GameStatistics()
        
        self.current_block = None
        self.next_block = None
        self.game_over = False
        self.score = 0
        self.level = 1
        self.mode = "classic"
        self.last_fall_time = 0
        self.fall_speed = 1000  # 初始下落速度 (毫秒)
        
        # 扩展按键状态跟踪，包含所有方向键
        self.last_key_states = {
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_SPACE: False,
            pygame.K_p: False,
            pygame.K_r: False
        }
        
        # 添加硬降状态跟踪
        self.is_hard_dropping = False
        self.hard_drop_speed = 10  # 硬降速度(毫秒)，普通下落是1000毫秒
        self.last_hard_drop_time = 0

        # 添加软降状态跟踪
        self.is_soft_dropping = False
        self.soft_drop_factor = 3  # 软降加速系数，下落速度会变为原来的1/5

        # 添加幽灵方块属性
        self.ghost_block = None
        self.show_ghost = True  # 可以通过设置选项控制是否显示幽灵方块

        # 添加限时模式的时间相关属性
        self.time_limit = 180  # 默认3分钟（180秒）
        self.time_remaining = self.time_limit
        self.last_time_tick = 0

        # 添加暂停、返回和结束显示状态
        self.paused = False
        self.return_confirm = False
        self.return_confirm_time = 0
        self.return_confirm_duration = 3000  # 确认等待时间3秒
        
        self.game_over_display = False
        self.game_over_time = 0
        self.game_over_duration = 2000  # 显示结束分数2秒（修改为2000毫秒，从原来的3000毫秒）

        # 添加连消相关属性
        self.combo_count = 0  # 连消计数器
        self.combo_timer = 0  # 连消计时器
        self.combo_display_duration = 2000  # 显示连消信息的时间(毫秒)
        self.combo_show = False  # 是否显示连消信息
        self.last_lines_cleared = 0  # 最后一次消除的行数
    
    def set_mode(self, mode):
        """设置游戏模式"""
        self.mode = mode
        self.game_over = False
        self.score = 0
        self.level = 1
        self.board.clear()
        self.current_block = self.block_factory.create_block(mode)
        self.next_block = self.block_factory.create_block(mode)
        self.audio.play_music(f"{mode}_theme")
        self.audio.set_music_volume(0.2)  # 设置背景音乐音量
        self.is_hard_dropping = False  # 重置硬降状态
        self.ghost_block = None
        
        # 获取此模式下的历史最高分
        self.highest_score = self.stats.get_highest_score(mode)
        
        # 重置时间（仅在限时模式下有效）
        if mode == "timed":
            self.time_remaining = self.time_limit
            self.last_time_tick = pygame.time.get_ticks()
        
        # 重置状态
        self.paused = False
        self.return_confirm = False
        self.game_over_display = False

        # 重置连消计数
        self.combo_count = 0
        self.combo_show = False
    
    def update(self):
        """更新游戏状态"""
        current_time = pygame.time.get_ticks()
        
        # 处理键盘输入 - 暂停和返回功能
        keys = pygame.key.get_pressed()
        
        # 检查P键按下（暂停/继续）
        if keys[pygame.K_p] and not self.last_key_states.get(pygame.K_p, False):
            self.paused = not self.paused
            if self.paused:
                self.audio.play_sound("menu_select")
            
        # 检查R键按下（返回确认）
        if keys[pygame.K_r] and not self.last_key_states.get(pygame.K_r, False):
            if self.return_confirm:
                # 已经在确认状态，确认返回
                return "return_to_menu"
            else:
                # 进入确认状态
                self.return_confirm = True
                self.return_confirm_time = current_time
                self.audio.play_sound("menu_select")
        
        # 更新按键状态
        self.last_key_states[pygame.K_p] = keys[pygame.K_p]
        self.last_key_states[pygame.K_r] = keys[pygame.K_r]
        
        # 检查返回确认超时
        if self.return_confirm and current_time - self.return_confirm_time > self.return_confirm_duration:
            self.return_confirm = False
            
        # 游戏结束显示处理
        if self.game_over and not self.game_over_display:
            self.game_over_display = True
            self.game_over_time = current_time
        
        # 如果游戏结束显示时间已到，返回菜单
        if self.game_over_display and current_time - self.game_over_time > self.game_over_duration:
            return "game_over"
            
        # 如果游戏暂停，只进行渲染，不更新游戏状态
        if self.paused:
            # 渲染暂停状态的游戏
            self.renderer.render_game(
                self.board, self.current_block, self.next_block,
                self.score, self.level, self.mode, self.ghost_block,
                self.time_remaining if self.mode == "timed" else None,
                paused=True, return_confirm=self.return_confirm,
                game_over=self.game_over_display
            )
            return "playing"
        
        # 如果处于硬降状态，执行快速下落
        if self.is_hard_dropping:
            # 高速下落
            if current_time - self.last_hard_drop_time > self.hard_drop_speed:
                # 尝试下移方块
                if not self._move_block(0, 1):
                    # 如果无法下移，说明已到达底部，结束硬降状态
                    self.is_hard_dropping = False
                self.last_hard_drop_time = current_time
        else:
            # 正常游戏逻辑
            # 处理键盘输入
            keys = pygame.key.get_pressed()
            
            # 修改所有方向键的处理逻辑，使用"按下抬起"模式
            # 左移动
            if keys[pygame.K_LEFT] and not self.last_key_states[pygame.K_LEFT]:
                self._move_block(-1, 0)
            
            # 右移动
            if keys[pygame.K_RIGHT] and not self.last_key_states[pygame.K_RIGHT]:
                self._move_block(1, 0)
            
            # 下移 - 移除"按下抬起"模式限制，支持长按
            # 设置软降状态，用于加速下落
            self.is_soft_dropping = keys[pygame.K_DOWN]
            if keys[pygame.K_DOWN]:
                self._move_block(0, 1)
                
            # 旋转和硬降
            if keys[pygame.K_UP] and not self.last_key_states[pygame.K_UP]:
                self._rotate_block()
            if keys[pygame.K_SPACE] and not self.last_key_states[pygame.K_SPACE]:
                self._hard_drop()
                
            # 更新所有按键状态记录
            self.last_key_states[pygame.K_LEFT] = keys[pygame.K_LEFT]
            self.last_key_states[pygame.K_RIGHT] = keys[pygame.K_RIGHT]
            self.last_key_states[pygame.K_DOWN] = keys[pygame.K_DOWN]
            self.last_key_states[pygame.K_UP] = keys[pygame.K_UP]
            self.last_key_states[pygame.K_SPACE] = keys[pygame.K_SPACE]
                
            # 自动下落 - 考虑软降状态，调整下落速度
            current_fall_speed = self.fall_speed
            if self.is_soft_dropping:
                current_fall_speed = self.fall_speed // self.soft_drop_factor
            
            if current_time - self.last_fall_time > current_fall_speed:
                self._move_block(0, 1)
                self.last_fall_time = current_time
            
        # 在限时模式下更新剩余时间
        if self.mode == "timed" and not self.game_over:
            elapsed = (current_time - self.last_time_tick) / 1000.0  # 转换为秒
            self.last_time_tick = current_time
            
            # 更新剩余时间
            self.time_remaining -= elapsed
            
            # 检查是否时间到
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.game_over = True
                self.audio.play_sound("game_over")
                self.stats.save_game_data(self.score, self.level, self.mode)
        
        # 检查连消显示是否应该隐藏
        if self.combo_show and current_time - self.combo_timer > self.combo_display_duration:
            self.combo_show = False

        # 更新幽灵方块位置
        if self.current_block and self.show_ghost:
            self._update_ghost_block()
        
        # 渲染游戏
        time_display = self.time_remaining if self.mode == "timed" else None
        self.renderer.render_game(
            self.board, self.current_block, self.next_block,
            self.score, self.level, self.mode, self.ghost_block,
            time_display, paused=False, return_confirm=self.return_confirm,
            game_over=self.game_over_display, 
            combo_info=(self.combo_count, self.combo_show, self.last_lines_cleared),
            highest_score=self.highest_score  # 传递最高分信息
        )
        
        if self.game_over_display:
            # 游戏结束时不再自动返回菜单，需按Q键返回
            return "playing"  
        return "game_over" if self.game_over else "playing"

    def _move_block(self, dx, dy):
        """移动当前方块，返回是否成功移动"""
        # 利用物理引擎检查移动是否有效
        if self.physics.can_move(self.current_block, self.board, dx, dy):
            self.current_block.move(dx, dy)
            result = True
        elif dy > 0:  # 无法继续下落
            self._place_block()
            result = False
        else:
            result = False
        
        # 如果方块位置变了，重新计算幽灵方块
        if self.show_ghost:
            self._update_ghost_block()
        
        return result
    
    def _rotate_block(self):
        """旋转当前方块，如果旋转无效，尝试左右平移找到有效位置"""
        # 保存原始位置和旋转状态，以便恢复
        original_x = self.current_block.x
        original_rotation = self.current_block.rotation
        
        # 先尝试旋转
        self.current_block.rotate()
        
        # 如果旋转位置有效，直接返回
        if self.physics.is_valid_position(self.current_block, self.board):
            # 如果旋转成功，重新计算幽灵方块
            if self.show_ghost:
                self._update_ghost_block()
            return
        
        # 旋转位置无效，尝试"壁踢"
        # 定义平移尝试顺序：先尝试小的移动，再尝试大的移动
        offsets = [
            (-1, 0), (1, 0),  # 左右移动1格
            (-2, 0), (2, 0),  # 左右移动2格
            (0, -1),          # 上移1格(用于特殊情况)
            (-1, -1), (1, -1) # 对角线移动
        ]
        
        for dx, dy in offsets:
            # 尝试平移
            self.current_block.x += dx
            self.current_block.y += dy
            
            # 检查平移后位置是否有效
            if self.physics.is_valid_position(self.current_block, self.board):
                # 找到有效位置，重新计算幽灵方块
                if self.show_ghost:
                    self._update_ghost_block()
                return
            
            # 位置仍无效，恢复位置继续尝试
            self.current_block.x -= dx
            self.current_block.y -= dy
        
        # 所有尝试都失败，恢复原始状态
        self.current_block.x = original_x
        self.current_block.rotation = original_rotation
    
    def _hard_drop(self):
        """硬降实现为极速下落，而不是瞬间到底"""
        # 设置硬降状态
        self.is_hard_dropping = True
        self.last_hard_drop_time = pygame.time.get_ticks()
        # 播放相应音效
        self.audio.play_sound("special_block")  # 或者创建一个专用的硬降音效
    
    def _place_block(self):
        """放置方块并检查消行"""
        self.board.place_block(self.current_block)
        self.audio.play_sound("block_placed")
        
        # 检查消行并更新分数
        lines_cleared = self.board.clear_lines()
        self.last_lines_cleared = lines_cleared  # 保存消除的行数
        
        if lines_cleared > 0:
            # 连消计数增加
            self.combo_count += 1
            self.combo_show = True  # 确保设置为True
            self.combo_timer = pygame.time.get_ticks()
            
            # 基础分数计算
            base_score = lines_cleared * 100 * self.level
            
            # 连消奖励计算 - 每次连消增加递增的奖励
            combo_bonus = 0
            if self.combo_count > 1:  # 第二次连消开始计算奖励
                combo_bonus = self.combo_count * 50 * self.level  # 连消倍数 * 50 * 等级
            
            # 行数奖励 - 一次消除多行有额外奖励
            line_bonus = 0
            if lines_cleared >= 4:  # 一次消4行
                line_bonus = 800 * self.level
            elif lines_cleared >= 3:  # 一次消3行
                line_bonus = 300 * self.level
            elif lines_cleared >= 2:  # 一次消2行
                line_bonus = 100 * self.level
                
            # 总分 = 基础分 + 连消奖励 + 行数奖励
            total_score = base_score + combo_bonus + line_bonus
            self.score += total_score
            
            # 播放连消音效
            if self.combo_count >= 3:
                self.audio.play_sound("combo_special")  # 特殊连消音效
            else:
                self.audio.play_sound("line_clear")
            
            # 每清除10行提升一个等级
            if self.score // 1000 > self.level - 1:
                self.level += 1
                self.fall_speed = max(100, 1000 -(self.level - 1) * 100)
                self.audio.play_sound("level_up")
        else:
            # 没有消行，重置连消计数
            self.combo_count = 0
            self.combo_show = False
        
        self.stats.update(lines_cleared, self.current_block.type)
        
        # 更改方块生成逻辑：首先检查是否可以放置下一个方块
        self.current_block = self.next_block
        
        # 检查游戏是否应该结束
        if not self.physics.is_valid_position(self.current_block, self.board):
            self.game_over = True
            self.audio.play_sound("game_over")
            self.stats.save_game_data(self.score, self.level, self.mode)
            # 不再直接返回game_over，而是启动显示结束分数的倒计时
            self.game_over_display = True
            self.game_over_time = pygame.time.get_ticks()
            # 游戏结束后不再生成新方块
            return
        
        # 只有游戏未结束时才生成新的下一个方块
        self.next_block = self.block_factory.create_block(self.mode)
        
        # 在更新分数后检查是否超过最高分
        if self.score > self.highest_score:
            self.highest_score = self.score
    
    def _update_ghost_block(self):
        """更新幽灵方块位置 - 计算当前方块直接落到底部的位置"""
        if not self.current_block:
            self.ghost_block = None
            return
            
        # 创建当前方块的深拷贝
        self.ghost_block = deepcopy(self.current_block)
        
        # 将幽灵方块移动到底部
        while self.physics.can_move(self.ghost_block, self.board, 0, 1):
            self.ghost_block.move(0, 1)
