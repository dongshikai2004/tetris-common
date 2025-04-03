import pygame
import sys
from core.game import Game
from ui.menu import MainMenu
from utils.font_manager import FontManager
from utils.system_utils import switch_to_english_input  # 导入输入法切换功能

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 680))
    pygame.display.set_caption("创新俄罗斯方块")
    
    # 启动时尝试切换到英文输入法
    switch_to_english_input()
    
    # 初始化字体管理器
    font_manager = FontManager()
    
    # 创建主菜单和游戏实例
    main_menu = MainMenu(screen)
    game = Game(screen)
    
    current_screen = "menu"  # 初始界面为菜单
    
    # 主循环
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # 在游戏界面按Q返回菜单
                if event.key == pygame.K_q and current_screen == "game":
                    current_screen = "menu"
                # 处理菜单界面的R键
                elif event.key == pygame.K_r and current_screen == "menu":
                    # 不执行任何操作，因为已经在菜单
                    pass
                
        if current_screen == "menu":
            action = main_menu.update()
            if action:
                if action == "start_classic":
                    game.set_mode("classic")
                    current_screen = "game"
                elif action == "start_timed":
                    game.set_mode("timed")
                    current_screen = "game"
                elif action == "start_challenge":
                    game.set_mode("challenge")
                    current_screen = "game"
                elif action == "quit":
                    pygame.quit()
                    sys.exit()
        elif current_screen == "game":
            game_status = game.update()
            if game_status == "return_to_menu":
                # 直接返回菜单
                current_screen = "menu"
            # 游戏结束不再自动返回菜单，需要玩家按Q键
            # 删除了之前自动返回菜单的代码
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
