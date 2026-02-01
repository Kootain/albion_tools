import os
from base.base2 import event_parsers, GameEvent, EventParserBase
import importlib.util
import inspect


def find_classes_inherit_from(base_class, target_dir):
    """
    在指定目录下找到所有继承自base_class（X类）的类（包括直接/间接继承）
    :param base_class: 基类（X类），如 MyBaseClass
    :param target_dir: 目标目录路径（绝对/相对路径）
    :return: 列表，包含所有符合条件的类对象
    """
    # 存储符合条件的类
    matched_classes = []
    # 规范化目标目录路径（处理相对路径→绝对路径）
    target_dir = os.path.abspath(target_dir)
    
    # 递归遍历目录下的所有.py文件
    for root, dirs, files in os.walk(target_dir):
        # 排除无关目录（可根据需要添加/删除）
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'venv', 'env')]
        
        for file in files:
            # 只处理.py文件，排除__init__.py外的空文件（可选）
            if file.endswith('.py') and not file.startswith('.'):
                file_path = os.path.join(root, file)
                # 跳过空文件
                if os.path.getsize(file_path) == 0:
                    continue
                
                try:
                    # ------------------- 关键：动态导入模块 -------------------
                    # 1. 计算模块名（将文件路径转换为包路径格式）
                    # 例如：/project/test/foo.py → test.foo
                    rel_path = os.path.relpath(file_path, target_dir)
                    module_name = os.path.splitext(rel_path)[0].replace(os.sep, '.')
                    
                    # 2. 创建模块规范并导入
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # ------------------- 筛选类并检查继承关系 -------------------
                    # 遍历模块中的所有属性
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        # 筛选：是类 + 不是base_class本身 + 是base_class的子类
                        if (inspect.isclass(attr) and 
                            attr is not base_class and 
                            issubclass(attr, base_class)):
                            matched_classes.append(attr)
                
                except Exception as e:
                    # 捕获导入/解析错误，打印提示但不中断整体扫描
                    print(f"⚠️ 处理文件 {file_path} 时出错: {str(e)}")
                    continue
    
    return matched_classes


def register_event_parsers():
    # event_parsers = find_classes_inherit_from(EventParserBase, os.path.join(os.path.dirname(__file__), 'event'))
    # request_parsers = find_classes_inherit_from(EventParserBase, os.path.join(os.path.dirname(__file__), 'request'))
    # response_parsers = find_classes_inherit_from(EventParserBase, os.path.join(os.path.dirname(__file__), 'response'))
    # print(f"事件解析器 {event_parsers}")
    # print(f"请求解析器 {request_parsers}")
    # print(f"响应解析器 {response_parsers}")
    pass


def parse(event: GameEvent) -> GameEvent:
    parser = event_parsers[event.type][event.code]
    if parser is None:
        return event
    event = parser.parse(event)
    if parser.debug:
        print(f"事件解析器 {event.type} {event.code} {parser.__class__} {event}")
    return event