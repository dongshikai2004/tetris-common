import pygame
from utils.font_manager import FontManager

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 使用字体管理器
        self.font_manager = FontManager()
        
        # 添加模式描述
        self.mode_descriptions = {
            "start_classic": "经典模式：传统俄罗斯方块玩法，随着等级提升，方块下落速度加快。",
            "start_timed": "限时模式：在规定时间内消除尽可能多的行，有更多特殊方块出现。",
            "start_challenge": "挑战模式：随机出现的特殊方块和递增的下落速度，看你能坚持多久！"
        }
        
        # 菜单选项
        self.options = [
            {"text": "经典模式", "action": "start_classic", "pos": (self.width // 2, 200)},
            {"text": "限时模式", "action": "start_timed", "pos": (self.width // 2, 280)},
            {"text": "挑战模式", "action": "start_challenge", "pos": (self.width // 2, 360)},
            {"text": "退出游戏", "action": "quit", "pos": (self.width // 2, 440)}
        ]
        
        self.selected_option = 0
        self.last_key_time = 0
        self.key_delay = 200  # 按键延迟(毫秒)
    
    def update(self):
        self._handle_input()
        self._render()
        
        # 如果按下回车，返回选中选项的动作
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            return self.options[self.selected_option]["action"]
        
        return None
    
    def _handle_input(self):
        """处理键盘输入"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_key_time < self.key_delay:
            return
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.selected_option > 0:
            self.selected_option -= 1
            self.last_key_time = current_time
        elif keys[pygame.K_DOWN] and self.selected_option < len(self.options) - 1:
            self.selected_option += 1
            self.last_key_time = current_time
    
    def _render(self):
        """渲染菜单界面"""
        # 背景
        self.screen.fill((0, 0, 0))
        
        # 标题
        title_surface = self.font_manager.render_text("创新俄罗斯方块", 72, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # 菜单选项
        for i, option in enumerate(self.options):
            # 选中项用不同颜色
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text_surface = self.font_manager.render_text(option["text"], 48, color)
            rect = text_surface.get_rect(center=option["pos"])
            self.screen.blit(text_surface, rect)
        
        # 显示当前选中模式的描述（只对游戏模式显示描述）
        if self.selected_option < 3:  # 前三个选项是游戏模式
            selected_action = self.options[self.selected_option]["action"]
            if selected_action in self.mode_descriptions:
                description = self.mode_descriptions[selected_action]
                
                # 将描述文本拆分成多行，每行最多40个字符
                wrapped_text = self._wrap_text(description, 40)
                
                # 渲染每一行
                description_y = 500
                for line in wrapped_text:
                    desc_surface = self.font_manager.render_text(line, 24, (180, 180, 180))
                    desc_rect = desc_surface.get_rect(center=(self.width // 2, description_y))
                    self.screen.blit(desc_surface, desc_rect)
                    description_y += 30
        
        # 添加回车键选择的提示
        enter_tip = self.font_manager.render_text("按回车键选择", 32, (255, 165, 0))  # 使用橙色使其醒目
        enter_tip_rect = enter_tip.get_rect(center=(self.width // 2, self.height - 100))
        self.screen.blit(enter_tip, enter_tip_rect)
    
    def _wrap_text(self, text, max_chars_per_line):
        """将文本按最大字符数换行"""
        words = text.split(' ')
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            # 如果加上这个词会超过最大长度，则开始新行
            if current_length + len(word) + len(current_line) > max_chars_per_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word)
        
        # 添加最后一行
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
