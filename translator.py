"""
自动翻译模块 - 中文转英文
"""
import re

class SimpleTranslator:
    """简单的中英文翻译器"""
    
    def __init__(self):
        # 常用词汇对照表
        self.translation_dict = {
            # 动物类
            '猫': 'cat',
            '狗': 'dog', 
            '老鼠': 'mouse',
            '鸟': 'bird',
            '鱼': 'fish',
            '兔子': 'rabbit',
            '熊': 'bear',
            '狮子': 'lion',
            '老虎': 'tiger',
            '大象': 'elephant',
            '鳄鱼': 'crocodile',
            '蛇': 'snake',
            '马': 'horse',
            '牛': 'cow',
            '羊': 'sheep',
            '猪': 'pig',
            '鸡': 'chicken',
            '鸭': 'duck',
            '蝴蝶': 'butterfly',
            '蜜蜂': 'bee',
            
            # 物品类
            '房子': 'house',
            '树': 'tree',
            '花': 'flower',
            '太阳': 'sun',
            '月亮': 'moon',
            '星星': 'star',
            '云': 'cloud',
            '山': 'mountain',
            '海': 'ocean',
            '河': 'river',
            '桥': 'bridge',
            '车': 'car',
            '飞机': 'airplane',
            '船': 'boat',
            '自行车': 'bicycle',
            '书': 'book',
            '笔': 'pen',
            '杯子': 'cup',
            '桌子': 'table',
            '椅子': 'chair',
            '门': 'door',
            '窗户': 'window',
            
            # 人物类
            '人': 'person',
            '男人': 'man',
            '女人': 'woman',
            '孩子': 'child',
            '老人': 'old person',
            '医生': 'doctor',
            '老师': 'teacher',
            '学生': 'student',
            
            # 食物类
            '苹果': 'apple',
            '香蕉': 'banana',
            '橙子': 'orange',
            '草莓': 'strawberry',
            '蛋糕': 'cake',
            '面包': 'bread',
            '米饭': 'rice',
            
            # 连接词和助词
            '的': '',  # 删除"的"
            '和': 'and',
            '与': 'and', 
            '或': 'or',
            '在': 'in',
            '上': 'on',
            '下': 'under',
            '里': 'in',
            
            # 形容词
            '大': 'big',
            '小': 'small',
            '高': 'tall',
            '矮': 'short',
            '胖': 'fat',
            '瘦': 'thin',
            '美丽': 'beautiful',
            '可爱': 'cute',
            '漂亮': 'pretty',
            '简单': 'simple',
            '复杂': 'complex',
            
            # 运动类
            '篮球': 'basketball',
            '足球': 'football',
            '网球': 'tennis',
            '游泳': 'swimming',
            '跑步': 'running',
            '跳舞': 'dancing',
            '打': 'play',
            '踢': 'kick',
            '游': 'swim',
            '跑': 'run',
            '跳': 'jump',
            
            # 绘画相关
            '简笔画': 'simple drawing',
            '素描': 'sketch',
            '画': 'drawing',
            '图': 'picture',
            '线条': 'line art',
            '黑白': 'black and white',
            '彩色': 'colorful',
            '卡通': 'cartoon',
            '动漫': 'anime',
            '手绘': 'hand drawn'
        }
    
    def translate_to_english(self, chinese_text):
        """
        将中文翻译成英文
        
        Args:
            chinese_text: 中文文本
            
        Returns:
            str: 英文翻译结果
        """
        if not chinese_text:
            return ""
        
        # 如果已经是英文，直接返回
        if self._is_english(chinese_text):
            return chinese_text.strip()
        
        # 分词并翻译
        words = self._segment_chinese(chinese_text)
        translated_words = []
        
        for word in words:
            if word in self.translation_dict:
                translated_words.append(self.translation_dict[word])
            else:
                # 未找到翻译的词保持原样
                translated_words.append(word)
        
        result = ' '.join(translated_words)
        
        # 清理结果
        result = self._clean_translation(result)
        
        print(f"🌐 翻译: '{chinese_text}' → '{result}'")
        return result
    
    def _is_english(self, text):
        """判断是否为英文"""
        # 如果包含中文字符，则不是纯英文
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        return not chinese_pattern.search(text)
    
    def _segment_chinese(self, text):
        """简单的中文分词"""
        words = []
        i = 0
        
        while i < len(text):
            # 尝试匹配最长的词
            matched = False
            for length in range(min(4, len(text) - i), 0, -1):
                word = text[i:i+length]
                if word in self.translation_dict:
                    words.append(word)
                    i += length
                    matched = True
                    break
            
            if not matched:
                # 单个字符
                char = text[i]
                if char.strip():  # 忽略空白字符
                    words.append(char)
                i += 1
        
        return words
    
    def _clean_translation(self, text):
        """清理翻译结果"""
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        # 移除首尾空格
        text = text.strip()
        # 移除标点符号周围的空格
        text = re.sub(r'\s*([,.!?])\s*', r'\1 ', text)
        # 移除孤立的中文字符（未翻译的）
        text = re.sub(r'\s+[\u4e00-\u9fff]\s+', ' ', text)
        # 移除开头和结尾的中文字符
        text = re.sub(r'^[\u4e00-\u9fff]+\s*', '', text)
        text = re.sub(r'\s*[\u4e00-\u9fff]+$', '', text)
        return text
    
    def add_drawing_style(self, translated_text):
        """添加绘画风格描述"""
        if not translated_text:
            return "simple drawing"
        
        # 如果已经包含绘画相关词汇，直接返回
        drawing_keywords = ['drawing', 'sketch', 'art', 'line', 'picture']
        if any(keyword in translated_text.lower() for keyword in drawing_keywords):
            return translated_text
        
        # 添加简笔画风格
        return f"{translated_text} sketch"


# 测试代码
if __name__ == "__main__":
    translator = SimpleTranslator()
    
    test_cases = [
        "小猫",
        "可爱的小狗",
        "房子简笔画", 
        "鳄鱼",
        "美丽的花朵",
        "cat drawing",  # 英文测试
        "大象和老鼠",
        "太阳和月亮",
        "简单的树"
    ]
    
    print("=" * 60)
    print("🌐 翻译测试")
    print("=" * 60)
    
    for text in test_cases:
        translated = translator.translate_to_english(text)
        with_style = translator.add_drawing_style(translated)
        print(f"原文: {text}")
        print(f"翻译: {translated}")
        print(f"加风格: {with_style}")
        print("-" * 40)
