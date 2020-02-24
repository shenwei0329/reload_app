# coding:utf-8
#
#   具有模块自动加载的执行器
#   -------------------
#   Version: V1.0
#   Created: 2020.2.22 by shenwei @Home
#
#   要求：
#   1）模块统一存放在pool下
#   2）模块必须定义mod_info={'name': "模块名称", 'version': "版本"， 'desc': "说明")
#   3）模块必须包含main()，注：不带参数项
#   4）模块必须是一个单次执行的处理流程
#   5）在线程中，模块main()是被循环调用的
#   6）模块必须判别自己的处理条件
#   7）模块必须设定自己的等待周期间隔，不允许"空转"
#
#   功能：
#   1）自动加载pool目录下的python模块
#   2）启动一个线程处理模块的main()入口
#   3）自动重新加载更新/更改的模块，关闭原有线程，重新启动新线程处理模块main()入口
#   4）自动停止移除模块的线程
#

import sys
import time
import hashlib
import os

# 线程
import threading

#
# 全局参量定义
# ==========
#
info = {
    'name': "Loader",
    'version': "V1.0",
    'desc': "模块自动装载执行器"
}

# 模块列表：用于维护已装载模块文件
file_list = []
# 模块hash值：用于维护模块的hash
file_hash = {}
# 模块线程：用于维护模块的线程实例
file_thread = {}
# 模块：用于维护模块类实体
file_class = {}


def _print(_str):
    """
    公共print模块，可用log取代
    """
    print(_str)


def scan_files(directory):
    files_list = []

    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            _file = special_file.split('/')[-1]
            _mod = _file.split('.')
            _type = _mod[-1]
            if "py" == _type and "__" not in _file:
                files_list.append(_mod[0])
    return files_list


def get_file_hash(fn):
    """
    计算指定文件内容的hash值
    """
    try:
        _f = open(fn, 'rb')
        _str = _f.read()
        _f.close()
        m = hashlib.md5()
        m.update(_str)
        return m.hexdigest()
    except Exception as e:
        _print("Err: {}".format(e))
        return 0


class AppThread:
    """
    应用线程：用于实现线程退出管理
    """

    def __init__(self, mod):
        self._running = True
        self.mod = mod
        self.info = mod.mod_info
        _print("T[{0}] V:{1} D:{2}".format(self.info["name"], self.info["version"], self.info["desc"]))

    def stop(self):
        # 退出
        self._running = False

    def run(self):
        while self._running:
            # 线程主循环，执行模块的main()入口
            self.mod.main()


def load_mod(mod):
    """
    装载模块
    """

    # 卸载原有模块
    if mod in sys.modules:
        del (sys.modules[mod])

    # 装载新模块
    exec ("import {}".format(mod))

    # 创建模块线程
    _class = AppThread(sys.modules[mod])
    _t = threading.Thread(target=_class.run)
    _t.setDaemon(True)
    return _class, _t


def main():
    """
    主程序
    """

    while True:

        # 扫描资源目录，获取模块列表
        _files = scan_files('./pool')

        for _f in _files:

            if _f not in file_list: 
                # 新模块
                file_list.append(_f)
                _hash = get_file_hash("./pool/{}.py".format(_f))
                file_hash[_f] = _hash
                _mod_name = "pool.{}".format(_f)

                # 装载模块
                _class, _t = load_mod(_mod_name)
                file_thread[_f] = _t
                file_class[_f] = _class

                # 启动模块线程
                _t.start()

            else:
                # 计算模块hash，判断是否变更
                _hash = get_file_hash("./pool/{}.py".format(_f))
                _print("{0}: now({1}).old({2})".format(_f, _hash, file_hash[_f]))
                if _hash != file_hash[_f]:
                    # 有变更
                    # 停止线程
                    file_class[_f].stop()
                    file_thread[_f].join()

                    # 记录新hash
                    file_hash[_f] = _hash

                    # 模块更新
                    _mod_name = "pool.{}".format(_f)
                    _class, _t = load_mod(_mod_name)
                    file_thread[_f] = _t
                    file_class[_f] = _class

                    # 启动新模块线程
                    _t.start()

            _print("T.id = {}".format(file_thread[_f].ident))

        for _f in file_list:
            # 判断是否有模块被移除
            if _f not in _files:
                # 停止被移除模块的线程
                file_class[_f].stop()
                file_thread[_f].join()
                _print("> {} be shutdown!".format(_f))

                # 清除被移除模块的记录
                file_list.remove(_f)
                file_hash.pop(_f)
                file_thread.pop(_f)
                file_class.pop(_f)

        # 扫描周期
        time.sleep(60)


if __name__ == "__main__":
    print("\nAuto-loader executor[{0}], version: {1}".format(info['name'], info['version']))
    print("Desc: {0}\n\n".format(info['desc']))
    time.sleep(1)

    main()

# Eof
