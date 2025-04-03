import json
import os
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame
import numpy as np

class GameStatistics:
    def __init__(self):
        self.current_stats = {
            "lines_cleared": 0,
            "blocks_placed": 0,
            "block_types": {},  # 各类型方块的使用次数
            "start_time": time.time()
        }
        
        # 确保数据目录存在
        self.data_dir = os.path.join("d:\\Github Doc\\tetris-common", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 历史数据文件
        self.history_file = os.path.join(self.data_dir, "game_history.json")
        
        # 加载历史数据
        self.history = self._load_history()
    
    def update(self, lines_cleared, block_type):
        """更新当前游戏统计数据"""
        self.current_stats["lines_cleared"] += lines_cleared
        self.current_stats["blocks_placed"] += 1
        
        # 更新方块类型统计
        if block_type not in self.current_stats["block_types"]:
            self.current_stats["block_types"][block_type] = 0
        self.current_stats["block_types"][block_type] += 1
    
    def save_game_data(self, score, level, mode):
        """保存游戏结束时的数据"""
        game_duration = time.time() - self.current_stats["start_time"]
        
        # 创建游戏记录
        game_record = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "score": score,
            "level": level,
            "mode": mode,
            "duration": round(game_duration, 2),
            "lines_cleared": self.current_stats["lines_cleared"],
            "blocks_placed": self.current_stats["blocks_placed"],
            "block_types": self.current_stats["block_types"]
        }
        
        # 添加到历史记录
        self.history.append(game_record)
        
        # 保存历史记录
        self._save_history()
        
        # 重置当前游戏统计
        self.current_stats = {
            "lines_cleared": 0,
            "blocks_placed": 0,
            "block_types": {},
            "start_time": time.time()
        }
        
        return game_record
    
    def generate_statistics_surface(self, width, height):
        """生成包含游戏统计图表的pygame surface"""
        # 创建matplotlib图表
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        fig.patch.set_facecolor('#333333')  # 设置背景色
        
        # 设置图表标题颜色
        title_color = '#EEEEEE'
        text_color = '#CCCCCC'
        
        # 1. 分数随时间变化
        if len(self.history) >= 2:
            dates = [game["date"] for game in self.history[-10:]]
            scores = [game["score"] for game in self.history[-10:]]
            
            axs[0, 0].plot(range(len(dates)), scores, 'o-', color='#5599FF')
            axs[0, 0].set_title('最近10局分数趋势', color=title_color)
            axs[0, 0].set_xticks(range(len(dates)))
            axs[0, 0].set_xticklabels([d[-8:] for d in dates], rotation=45, color=text_color)
            axs[0, 0].tick_params(axis='y', colors=text_color)
            axs[0, 0].set_facecolor('#222222')
        else:
            axs[0, 0].text(0.5, 0.5, '需要更多游戏数据', 
                         horizontalalignment='center', verticalalignment='center',
                         color=text_color)
            axs[0, 0].set_title('分数趋势', color=title_color)
            axs[0, 0].set_facecolor('#222222')
        
        # 2. 方块类型分布饼图
        if self.history:
            # 合并所有历史记录中的方块类型数据
            all_blocks = {}
            for game in self.history:
                for block_type, count in game.get("block_types", {}).items():
                    if block_type not in all_blocks:
                        all_blocks[block_type] = 0
                    all_blocks[block_type] += count
            
            if all_blocks:
                labels = list(all_blocks.keys())
                sizes = list(all_blocks.values())
                
                axs[0, 1].pie(sizes, labels=None, autopct='%1.1f%%',
                           startangle=90, colors=plt.cm.Paired(np.linspace(0, 1, len(sizes))))
                axs[0, 1].set_title('方块类型分布', color=title_color)
                axs[0, 1].legend(labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                               fontsize='small')
                axs[0, 1].set_facecolor('#222222')
            else:
                axs[0, 1].text(0.5, 0.5, '无方块数据', 
                             horizontalalignment='center', verticalalignment='center',
                             color=text_color)
                axs[0, 1].set_title('方块类型分布', color=title_color)
                axs[0, 1].set_facecolor('#222222')
        
        # 3. 不同游戏模式的平均分数
        if self.history:
            mode_scores = {}
            mode_counts = {}
            
            for game in self.history:
                mode = game.get("mode", "unknown")
                score = game.get("score", 0)
                
                if mode not in mode_scores:
                    mode_scores[mode] = 0
                    mode_counts[mode] = 0
                    
                mode_scores[mode] += score
                mode_counts[mode] += 1
            
            # 计算平均分
            avg_scores = {mode: mode_scores[mode] / mode_counts[mode] 
                         for mode in mode_scores.keys()}
            
            modes = list(avg_scores.keys())
            scores = list(avg_scores.values())
            
            axs[1, 0].bar(range(len(modes)), scores, color='#66CCAA')
            axs[1, 0].set_title('各模式平均分数', color=title_color)
            axs[1, 0].set_xticks(range(len(modes)))
            axs[1, 0].set_xticklabels(modes, color=text_color)
            axs[1, 0].tick_params(axis='y', colors=text_color)
            axs[1, 0].set_facecolor('#222222')
        else:
            axs[1, 0].text(0.5, 0.5, '需要更多游戏数据', 
                         horizontalalignment='center', verticalalignment='center',
                         color=text_color)
            axs[1, 0].set_title('各模式平均分数', color=title_color)
            axs[1, 0].set_facecolor('#222222')
        
        # 4. 游戏持续时间与分数关系散点图
        if len(self.history) >= 3:
            durations = [game.get("duration", 0) / 60 for game in self.history]  # 转换为分钟
            scores = [game.get("score", 0) for game in self.history]
            
            axs[1, 1].scatter(durations, scores, alpha=0.7, c='#FF6699')
            axs[1, 1].set_title('游戏时长与分数关系', color=title_color)
            axs[1, 1].set_xlabel('时长(分钟)', color=text_color)
            axs[1, 1].set_ylabel('分数', color=text_color)
            axs[1, 1].tick_params(axis='both', colors=text_color)
            axs[1, 1].set_facecolor('#222222')
        else:
            axs[1, 1].text(0.5, 0.5, '需要更多游戏数据', 
                         horizontalalignment='center', verticalalignment='center',
                         color=text_color)
            axs[1, 1].set_title('游戏时长与分数关系', color=title_color)
            axs[1, 1].set_facecolor('#222222')
        
        # 调整布局
        plt.tight_layout()
        
        # 将matplotlib图表转换为pygame surface
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        
        plt.close(fig)  # 关闭matplotlib图表
        
        # 创建pygame surface
        surf = pygame.image.fromstring(raw_data, canvas.get_width_height(), "RGB")
        
        # 缩放到目标大小
        return pygame.transform.scale(surf, (width, height))
    
    def get_highest_score(self, mode=None):
        """获取历史最高分，可按游戏模式筛选"""
        if not self.history:
            return 0
            
        if mode:
            # 按模式筛选
            mode_history = [game for game in self.history if game.get("mode") == mode]
            if not mode_history:
                return 0
            return max(game.get("score", 0) for game in mode_history)
        else:
            # 所有模式的最高分
            return max(game.get("score", 0) for game in self.history)
    
    def get_recent_scores(self, limit=5, mode=None):
        """获取最近几局的分数，可按游戏模式筛选"""
        if not self.history:
            return []
            
        if mode:
            # 按模式筛选
            mode_history = [game for game in self.history if game.get("mode") == mode]
            # 返回最近的几局（按日期倒序）
            sorted_games = sorted(mode_history, key=lambda x: x.get("date", ""), reverse=True)
            return sorted_games[:limit]
        else:
            # 返回最近的几局（按日期倒序）
            sorted_games = sorted(self.history, key=lambda x: x.get("date", ""), reverse=True)
            return sorted_games[:limit]
    
    def _load_history(self):
        """加载历史数据"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        """保存历史数据"""
        # 限制历史记录数量
        if len(self.history) > 100:
            self.history = self.history[-100:]
            
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)
