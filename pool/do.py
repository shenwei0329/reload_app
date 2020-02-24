# coding: utf-8
#
#   模块样板
#   ======
#
#   程序包含：
#   1、信息定义
#   2、主入口main()
#   3、执行流程
#   4、等待周期
#


import time

# 模块信息定义
mod_info = {
    'name': 'mod_sample',
    'version': 'V1.0',
    'desc': '模块样板，用于对模块整体结构进行示意'
}


def main():
    """
    模块主入口
    """

    # 1、判断执行条件

    # 2、进入执行流程
    print("Hi! my name is {0}: {1}]".format(mod_info['name'], mod_info['version']))

    # 3、等待下一次执行
    time.sleep(8)

#
# Eof
#
