#!/usr/bin/env python3
"""
TrevanQuant 启动脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入并运行主程序
if __name__ == '__main__':
    from trevanquant.scheduler.runner import main
    main()