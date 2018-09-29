import os
import ftputil
from datetime import datetime, timedelta
from collections import deque

def latest_forecast_init_time(now=None, year_label='y', UTC=False):
    """
    根据当前时间返回最近起报时间，默认格式为'yymmddhh'
    :param now: 当前时间，datetime.datetime类型，默认为当前计算机系统的时间
    :param year_label: 指定返回时间的年份的格式，默认为两位数年份'yy',也可以指定为'Y',则返回四位数年份'yyyyy'
    :return: 字符串格式的最近起报时间，'yymmddhh'或者'yyyymmddhh'
    """
    if not now:
        now = datetime.now()
    
    today = now.strftime('%'+year_label+'%m%d')
    now_time = now.strftime('%'+year_label+'%m%d%H')
    if now_time < today + "12":
        yesterday = now - timedelta(days=1)
        start_predict = yesterday.strftime('%'+year_label+'%m%d') + '20'
    else:
        start_predict = today + '08'
    if UTC:
        start_predict = (datetime.strptime(start_predict,'%'+year_label+'%m%d%H')-timedelta(hours=8)).strftime('%'+year_label+'%m%d%H')
    return start_predict


def gfs_download(target_dir, source_dir='/pub/data/nccf/com/gfs/prod/', timeout=24):
    '''

    :param target_dir: # 下载文件存放目录
    :param source_dir: # 远程目录
    :param timeout: 运行时间控制
    :return:
    '''

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with ftputil.FTPHost('ftp.ncep.noaa.gov','anonymous','') as ftp:
        ftp.chdir(source_dir)

        init_time = latest_forecast_init_time(year_label='Y', UTC=True)
        cycle_runtime = init_time[-2:]  # 起报时次
        # 将预报时效为6×n的放在前面，12h降水计算依赖这些数据
        forecast_time_deque = deque(['%03d' % i for i in list(range(0, 246, 6)) + list(range(3, 243, 6))])  # 预报时效

        begin_t = datetime.now()
        while len(forecast_time_deque) > 0 and datetime.now()-begin_t < timedelta(hours=timeout):

            forecast_time = forecast_time_deque.popleft()

            source_file = 'gfs.%s/gfs.t%sz.pgrb2.0p25.f%s' % (init_time, cycle_runtime, forecast_time)
            target_file = '%s.%s.grib2' % (init_time, forecast_time)

            target = os.path.join(target_dir, target_file)  # 本地文件名，全路径

            if ftp.path.exists(source_file):
                if not os.path.exists(target):
                    print(source_file,'is downloading……')
                    ftp.download(source_file, target)
                    print(target, 'successfully downloaded!')
                    print('*'*20)
                else:
                    print(target, 'has downloaded!')
                    print('*'*20)
            else:  # 如果不存在，则将其再次加入到下载队列中
                forecast_time_deque.append(forecast_time)

        if len(forecast_time_deque) > 0:
            print('有数据没有下载完成')


if __name__ == "__main__":
    #print(latest_forecast_init_time(UTC=True))
    gfs_download('/home/zhuf/gfsdownload')