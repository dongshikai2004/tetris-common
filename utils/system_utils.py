import ctypes
import sys

def switch_to_english_input():
    """
    将输入法切换为英文(美式键盘)
    
    此功能仅在Windows系统上有效，其他系统不执行任何操作
    """
    try:
        # 仅在Windows系统上尝试
        if sys.platform == 'win32':
            # 加载user32.dll
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # 美式键盘输入法的语言代码 (0x0409 是美国英语)
            # 0x4090409 是完整的键盘布局标识符，包含了语言ID和键盘布局
            LID = 0x4090409
            
            # 获取当前的输入法列表
            # GetKeyboardLayoutList函数获取所有已加载的输入法
            # 第一个参数是输出数组的大小，第二个参数是输出数组
            # 如果第一个参数为0，则返回系统中可用的输入法数量
            layouts_count = user32.GetKeyboardLayoutList(0, None)
            if layouts_count > 0:
                layouts = (ctypes.c_int * layouts_count)()
                user32.GetKeyboardLayoutList(layouts_count, layouts)
                
                # 检查英语键盘是否已经加载
                english_loaded = False
                for i in range(layouts_count):
                    if layouts[i] == LID:
                        english_loaded = True
                        break
                
                # 如果英语键盘已加载，则切换到英语键盘
                if english_loaded:
                    # 切换到英语键盘
                    # LoadKeyboardLayout加载指定的键盘布局
                    # 第一个参数是键盘布局名称，第二个参数是标志位
                    # 0x00000001 (KLF_ACTIVATE) 表示立即激活此键盘布局
                    user32.ActivateKeyboardLayout(LID, 0)
                    return True
                else:
                    # 如果英语键盘尚未加载，尝试加载它
                    # "00000409" 是美式英语键盘的字符串标识符
                    result = user32.LoadKeyboardLayoutW("00000409", 1)
                    if result:
                        return True
                    
            print("无法切换到英文输入法，请手动切换")
            return False
    except Exception as e:
        print(f"切换输入法时发生错误: {e}")
        return False
    
    # 非Windows系统
    return False
