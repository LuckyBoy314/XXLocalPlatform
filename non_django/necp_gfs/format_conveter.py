# -*- coding:utf-8 -*-
# @author: ZHU Feng

import Nio
import numpy as np
from datetime import datetime, timedelta
import os


# todo 判断文件是否下载完成最好不要使用这种方法，考虑后期同步处理问题

class File(object):
    """
    判断文件是否已经被其他程序打开，主要用来判断grib2文件是否已经下载完成。
    只能用于Linux系统
    代码来自https://segmentfault.com/q/1010000003765147/a-1020000003766138
    """
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise OSError('{file_path} not exist'.format(file_path=file_path))
        self.file_path = os.path.abspath(file_path)

    def is_opened(self):
        return self.status()['is_opened']

    def status(self):
        open_fd_list = self.__get_all_fd()
        open_count = len(open_fd_list)
        is_opened = open_count > 0

        return {'is_opened': is_opened, 'open_count': open_count}

    def __get_all_pid(self):
        """获取当前所有进程"""
        return [_i for _i in os.listdir('/proc') if _i.isdigit()]

    def __get_all_fd(self):
        """获取所有已经打开该文件的fd路径"""
        all_fd = []
        for pid in self.__get_all_pid():
            _fd_dir = '/proc/{pid}/fd'.format(pid=pid)
            if os.access(_fd_dir, os.R_OK) is False:
                continue

            for fd in os.listdir(_fd_dir):
                fd_path = os.path.join(_fd_dir, fd)
                if os.path.exists(fd_path) and os.readlink(fd_path) == self.file_path:
                    all_fd.append(fd_path)
        return all_fd


def test_rain_variable_name(init_time, grib2_dir):
    for i in range(6, 24, 6):
        f = os.path.join(grib2_dir, '%s.%03d.grib2' % (init_time, i))
        if os.path.exists(f):
            obj = Nio.open_file(f)
            for var in obj.variables:
                if var.startswith('APCP_P8_L1_GLL0'):
                    print(var, f)
                    print(obj.variables[var])
                    break
            obj.close()


def rain12h_to_micpas_txt(f1_path, f2_path, products_dir):
    """
    计算12小时间隔降水量,并转换为micaps文本格式
    :param f1_path: f1_path预报时效必须是12×n
    :param f2_path: f2_path预报时效是f1_path的前六个小时
    :param products_dir: 生成文件的存储目录
    :return:
    """

    f1 = Nio.open_file(f1_path)
    var = f1.variables['APCP_P8_L1_GLL0_acc6h']
    init_time = datetime.strptime(var.initial_time, '%m/%d/%Y (%H:%M)') + timedelta(hours=8)  # 起报时间
    forecast_hour = int(var.forecast_time)  # 预报时效
    forecast_time = init_time + timedelta(hours=forecast_hour)  # 预报时间

    # micaps dimond4头描述信息
    header = 'diamond 4 NECP_GFS_12小时降水(mm)(%s.%03d:%s)\n%s %d 0\n' % (init_time.strftime('%y%m%d%H'),
                                                                        forecast_hour,
                                                                        forecast_time.strftime('%d%H'),
                                                                        init_time.strftime('%y %m %d %H'),
                                                                        forecast_hour) \
             + '0.25 -0.25 0.00 180.00 80.00 -10.00 721 361 5.00 0.00 250.00 1.00 50.00'

    data1 = var.get_value()[40:401, 0:721]

    f2 = Nio.open_file(f2_path)
    var_name = 'APCP_P8_L1_GLL0_acc' if forecast_hour == 12 else 'APCP_P8_L1_GLL0_acc6h'
    data2 = f2.variables[var_name].get_value()[40:401, 0:721]

    data = data1 + data2
    data = data.data  # 只需要maskedarray的data部分

    out_file_name = init_time.strftime('%y%m%d%H') + '.%03d' % forecast_hour
    out_path = os.path.join(products_dir, out_file_name)
    np.savetxt(out_path, data, fmt='%.2f', delimiter=' ', header=header, comments='')

    f1.close()
    f2.close()


def produce_rain_12h(init_time, grib2_dir, products_dir):
    """
    批量生产12小时间隔降水micaps产品
    :param init_time: 起报时间，注意是世界时
    :param grib2_dir: 原始grib2格式的文件存储目录
    :param products_dir: 产品生产目录
    :return:
    """

    init_time_bjt = (datetime.strptime(init_time, '%Y%m%d%H') + timedelta(hours=8)).strftime('%y%m%d%H')
    for i in range(12, 252, 12):
        # 该函数可能会被多次重复执行，因此加上产品是否已经生产完成的判断
        if os.path.exists(os.path.join(products_dir, '%s.%03d' % (init_time_bjt, i))):
            continue

        f1 = os.path.join(grib2_dir, '%s.%03d.grib2' % (init_time, i))
        f2 = os.path.join(grib2_dir, '%s.%03d.grib2' % (init_time, i - 6))
        if os.path.exists(f1) and not File(f1).is_opened() and os.path.exists(f2) and not File(f2).is_opened():
            rain12h_to_micpas_txt(f1, f2, products_dir)


if __name__ == "__main__":
    produce_rain_12h('2018092600', '/home/zhuf/gfsdownload', '/media/sf_Share_Directory/ncep_gfs')
    # test_rain_variable_name('2018092400', '/home/zhuf/gfsdownload')
    # f = File('/home/zhuf/gfsdownload/2018092600.216.grib2')
    # print(f.status()['is_opened'])
