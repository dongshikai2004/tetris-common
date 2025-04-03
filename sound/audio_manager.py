import pygame
import os

class AudioManager:
    def __init__(self):
        # 确保pygame混音器已初始化
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # 音效和音乐目录
        self.sound_dir = os.path.join("d:\\Github Doc\\tetris-common", "assets", "sounds")
        self.music_dir = os.path.join("d:\\Github Doc\\tetris-common", "assets", "music")
        
        # 创建目录（如果不存在）
        os.makedirs(self.sound_dir, exist_ok=True)
        os.makedirs(self.music_dir, exist_ok=True)
        
        # 加载声音效果（如果文件存在）
        self.sounds = {}
        self._load_default_sounds()
        
        # 音乐曲目
        self.music_tracks = {
            "classic_theme": os.path.join(self.music_dir, "classic_theme.wav"),
            "timed_theme": os.path.join(self.music_dir, "timed_theme.mp3"),
            "challenge_theme": os.path.join(self.music_dir, "challenge_theme.mp3")
        }
        
        # 音量设置
        self.sound_volume = 0.7
        self.music_volume = 0.5
        
        # 应用音量设置
        pygame.mixer.music.set_volume(self.music_volume)
    
    def _load_default_sounds(self):
        """加载默认音效或创建占位音效文件"""
        sound_files = {
            "block_placed": "block_placed.ogg",
            "line_clear": "line_clear.mp3",
            "game_over": "game_over.mp3",
            "level_up": "level_up.wav",
            "menu_select": "menu_select.ogg",
            "special_block": "special_block.wav",
            "combo_special": "combo_special.wav",  # 添加连消特殊音效
            "perfect": "perfect.mp3"  # 完美消行音效
        }
        
        for key, filename in sound_files.items():
            full_path = os.path.join(self.sound_dir, filename)
            
            # 检查文件是否存在
            if os.path.exists(full_path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(full_path)
                    self.sounds[key].set_volume(self.sound_volume)
                except:
                    print(f"无法加载音效: {filename}")
            else:
                # 如果文件不存在，创建一个提示
                print(f"音效文件不存在: {full_path}")
                # 创建一个静音的音效作为占位符
                empty_sound = pygame.mixer.Sound(buffer=bytes([0] * 44))
                self.sounds[key] = empty_sound
    
    def play_sound(self, sound_name):
        """播放指定的音效"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_music(self, track_name):
        """播放指定的背景音乐"""
        if track_name in self.music_tracks and os.path.exists(self.music_tracks[track_name]):
            try:
                pygame.mixer.music.load(self.music_tracks[track_name])
                pygame.mixer.music.play(-1)  # 循环播放
            except:
                print(f"无法播放音乐: {track_name}")
        else:
            # 尝试停止正在播放的音乐
            pygame.mixer.music.stop()
            print(f"音乐文件不存在: {track_name}")
    
    def set_sound_volume(self, volume):
        """设置音效音量"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def set_music_volume(self, volume):
        """设置音乐音量"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def stop_music(self):
        """停止背景音乐"""
        pygame.mixer.music.stop()
