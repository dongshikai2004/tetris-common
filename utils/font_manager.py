import pygame
import os
import sys

class FontManager:
    def __init__(self):
        # 字体目录
        self.fonts_dir = os.path.join("d:\\Github Doc\\tetris-common", "assets", "fonts")
        os.makedirs(self.fonts_dir, exist_ok=True)
        
        # 尝试加载自定义字体，如果存在
        self.custom_font_path = os.path.join(self.fonts_dir, "simhei.ttf")
        
        # 尝试找到系统中支持中文的字体
        self.system_fonts = self._find_system_fonts()
        
    def _find_system_fonts(self):
        """寻找系统中可能支持中文的字体"""
        system_fonts = []
        
        # Windows系统常见中文字体
        windows_fonts = [
            "simhei.ttf",       # 黑体
            "simsun.ttc",       # 宋体
            "msyh.ttc",         # 微软雅黑
            "msyhbd.ttc",       # 微软雅黑粗体
            "simkai.ttf"        # 楷体
        ]
        
        # 检查Windows字体目录
        if sys.platform == "win32":
            fonts_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts")
            for font in windows_fonts:
                if os.path.exists(os.path.join(fonts_dir, font)):
                    system_fonts.append(os.path.join(fonts_dir, font))
        
        # 在Linux/MacOS上查找字体
        elif sys.platform in ["linux", "darwin"]:
            common_font_dirs = [
                "/usr/share/fonts",
                "/usr/local/share/fonts",
                os.path.expanduser("~/.fonts"),
                "/Library/Fonts",
                "/System/Library/Fonts"
            ]
            
            for font_dir in common_font_dirs:
                if os.path.exists(font_dir):
                    for root, dirs, files in os.walk(font_dir):
                        for file in files:
                            if file.endswith(('.ttf', '.ttc', '.otf')):
                                system_fonts.append(os.path.join(root, file))
        
        return system_fonts
    
    def get_font(self, size, bold=False):
        """获取支持中文的字体"""
        # 首先尝试加载自定义字体
        if os.path.exists(self.custom_font_path):
            try:
                return pygame.font.Font(self.custom_font_path, size)
            except:
                pass
        
        # 尝试使用系统字体
        for font_path in self.system_fonts:
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
        
        # 如果没有找到合适的字体，尝试使用pygame的默认字体并打印警告
        print("警告：未找到支持中文的字体，中文显示可能会有问题")
        
        # 尝试使用Pygame内置的默认字体
        if bold:
            return pygame.font.SysFont(None, size, bold=True)
        return pygame.font.SysFont(None, size)
    
    def render_text(self, text, size, color, bold=False):
        """渲染文本并返回Surface对象"""
        font = self.get_font(size, bold)
        return font.render(text, True, color)
