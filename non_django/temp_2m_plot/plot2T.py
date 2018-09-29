# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
import os, time
from math import sqrt, fabs
import cPickle as pickle

from collections import OrderedDict
import pandas as pd

from bokeh.plotting import figure, output_file, save, ColumnDataSource  # ,show
from bokeh.models import Range1d, Span, BoxAnnotation, HoverTool, DatetimeTicker, DatetimeTickFormatter
from bokeh.models.widgets import Panel, Tabs


class Diamond4(object):
    """

    """
    diamond = 4

    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            data_raw = [word for line in f.readlines() if line[:-1].strip() for word in
                        line.split()]  # 去除空行读入,将原文件分割成一维字符串数组

            self.doc = data_raw[2].decode('gbk')  # 说明字符串

            (self.size_lon,  # 经度（x方向）格距
             self.size_lat,  # 纬度（y方向）格距
             self.lon_start,  # 起始经度
             self.lon_end,  # 终止经度
             self.lat_start,  # 起始纬度
             self.lat_end) = [float(i) for i in data_raw[9:15]]  # 终止纬度

            (self.nums_lon,  # 纬向(x方向)格点数目，即列数
             self.nums_lat) = [int(i) for i in data_raw[15:17]]  # 经向(y方向)格点数目，即行数

            # 日期时间处理
            (month, day, hour, interval) = data_raw[4:8]
            year = data_raw[3]
            if len(year) == 2:
                year = ('20' + year) if int(year) < 49 else ('19' + year)
            elif len(year) == 4:
                pass
            else:
                raise Exception('year parameter error!')

            self.start_time = datetime(int(year), int(month), int(day), int(hour))
            self.valid_time = self.start_time + timedelta(hours=int(interval))

            # 数据部分，以一维数组表示
            self.data = [float(i) for i in data_raw[22:]]

            del data_raw

    def value(self, row, col):
        '''将格点数据看成self.nums_lon*self.nums_lat的二维数组，返回第row行，第col列的值，
        row和col必须为整数，从0开始计数，坐标原点在左上角'''
        if row < 0 or row >= self.nums_lat or col < 0 or col >= self.nums_lon:
            raise Exception('out of data spatial range')
        return self.data[row * self.nums_lon + col]

    def IDW(self, lon_lat_s, power=2):
        """
        反距离加权法提取站点数据
        :param lon_lat_s: 以[(lon1,lat1）,(lon2,lat2),……]形式传入的一系列站点位置,经纬度必须是弧度形式
        :param power:
        :return: 对应站点位置的插值结果列表
        """
        extracted_values = []
        for lon, lat in lon_lat_s:
            # 根据目标位置经纬度计算其周围四个格点在二维数组中的起始和终止行列号
            col_beg = int(fabs((lon - self.lon_start) / self.size_lon))
            row_beg = int(fabs((lat - self.lat_start) / self.size_lat))
            col_end = col_beg + 1
            row_end = row_beg + 1

            # 计算包围目标位置的经纬度范围,即起始和终止行列号的对应经纬度，行号与纬度对应，列号与经度对应
            lon_beg = self.lon_start + self.size_lon * col_beg
            lon_end = self.lon_start + self.size_lon * col_end
            lat_beg = self.lat_start + self.size_lat * row_beg
            lat_end = self.lat_start + self.size_lat * row_end

            # 根据目标位置与周围四个格点的经纬度距离计算权重
            w1 = 1.0 / (sqrt((lon_beg - lon) ** 2 + (lat_beg - lat) ** 2)) ** power
            w2 = 1.0 / (sqrt((lon_beg - lon) ** 2 + (lat_end - lat) ** 2)) ** power
            w3 = 1.0 / (sqrt((lon_end - lon) ** 2 + (lat_beg - lat) ** 2)) ** power
            w4 = 1.0 / (sqrt((lon_end - lon) ** 2 + (lat_end - lat) ** 2)) ** power

            # 目标位置周围四个格点的值
            d1 = self.value(row_beg, col_beg)
            d2 = self.value(row_end, col_beg)
            d3 = self.value(row_beg, col_end)
            d4 = self.value(row_end, col_end)

            # 根据反距离加权计算最终值，注意权重与格点要一一对应
            z = (d1 * w1 + d2 * w2 + d3 * w3 + d4 * w4) / (w1 + w2 + w3 + w4)

            extracted_values.append(z)

        return extracted_values

    def extract_station_value(self, lon_lat_s, method):
        '提取站点数据'
        pass


def searchProductFiles(date_time, directories):
    """
    按照起报时间搜索相应文件
    :param date_time: 起报时间
    :param directories: 搜索目录，要提供产品的最终目录
    :return:
    """
    files_list = []  # os.path.join(root,f)
    for dir in directories:
        for root, dirs, files in os.walk(dir, topdown=True):
            if files:  # 当files不为空的时候，root为存储数据的最终目录
                files_list.extend(
                    [os.path.join(root, f) for f in files
                     if f.startswith(date_time) and f not in [os.path.basename(each) for each in files_list]]
                )  # 前面目录中的模式产品文件优先

    return files_list


def plot_2T(date_time, stations, models):
    """

    :param date_time: 必须是'YYMMDDHH'形式
    :param stations:
    :param models:
    :return:
    """
   
    tabs = []
    output_file('D:/LPWF/2T_Forecast.html', title=u'2米温度预报', mode='inline')

    names = [name for name in stations] + ['date_time_X', 'date_time_str']
    
    tools_to_show = 'hover,box_zoom,pan,save,resize,reset,wheel_zoom'
    
    #注意颜色的个数一定要与站点个数相同，不然以少的为准
    colors = ['red', 'blue', 'green', 'orange', 'yellow', 'purple', 'pink', 'violet'] 

    for model in models:
        #######添加新模式需要注意修改的地方：
        # 处理u'河南WRF_RUC'的'YYYYMMDDHH'形式
        if model == u'河南WRF_RUC':
            date_time_condition = (datetime.strptime('20' + date_time, '%Y%m%d%H') - timedelta(hours=8)).strftime(
                '%Y%m%d%H')
        elif model == u'GRAPES_MESO集合平均':
            date_time_condition = (datetime.strptime('20' + date_time, '%Y%m%d%H') - timedelta(hours=8)).strftime(
                '%y%m%d%H')
        else:
            date_time_condition = date_time

        data = []
        files_list = searchProductFiles(date_time_condition, models[model])

        for each in files_list:
            d = Diamond4(each)
            lon_lat_s = [stations[name][1] for name in stations]
            extracted_values = d.IDW(lon_lat_s)
            
            #######添加新模式需要注意修改的地方：
            # 处理时间索引
            date_time_index = d.valid_time
            if model in [u'河南WRF_RUC', u'GRAPES_GFS', u'GRAPES_MESO', u'T639粗',u'GRAPES_MESO集合平均']:
                date_time_index += timedelta(hours=8)

            # 注意bokeh在将时间对象作为X轴时会将本地时间转换为世界时，为了避免这种转换，需要再本地时间上再加上8h（北京时比世界时快8h）
            extracted_values.extend([date_time_index + timedelta(hours=8), date_time_index.strftime("%m/%d %Hh")])
            data.append(pd.DataFrame(extracted_values, index=names).T)

        # 如果没有数据，则返回，防止出错
        if not data:
            continue

        df = pd.concat(data).sort_values('date_time_X', ascending=False)
        del data

        n_series = len(df)

        p = figure(plot_width=1920 - 140, plot_height=1200 - 250,
                   x_axis_type="datetime", tools=tools_to_show, active_scroll="wheel_zoom")

        # 分别为每个站点绘制时间序列变化曲线
        for name, color in zip(stations, colors):
            source = ColumnDataSource(data={
                'dateX': df['date_time_X'],
                'v': df[name],
                'dateX_str': df['date_time_str'],
                'name': [name for n in xrange(n_series)]
            })

            p.line('dateX', 'v', color=color, legend=name, source=source)
            circle = p.circle('dateX', 'v', fill_color="white", size=8, color=color, legend=name, source=source)
            p.tools[0].renderers.append(circle)

        # 图例显示策略
        p.legend.click_policy = "hide"
        # 显示标签
        hover = p.select(dict(type=HoverTool))
        hover.tooltips = [(u"温度", "@v{0.0}"), (u"站点", "@name"), (u"时间", "@dateX_str")]
        hover.mode = 'mouse'

        # 标题设置
        if model == u'EC细 2TMax_3h':
            title = ' '.join([date_time, u'EC细', u'过去3小时2米最高温度预报'])
        elif model == u'EC细 2TMin_3h':
            title = ' '.join([date_time, u'EC细', u'过去3小时2米最低温度预报'])
        else:
            title = ' '.join([date_time, model, u'2米温度预报'])
        p.title.text = title

        p.title.align = "center"
        p.title.text_font_size = "25px"
        # p.title.background_fill_color = "#aaaaee"
        # p.title.text_color = "orange"
        p.xaxis.axis_label = u'日期/时间'
        p.yaxis.axis_label = u'温度(℃)'
        
        p.xaxis[0].formatter = DatetimeTickFormatter(hours=['%m/%d %Hh', '%m/%d %H:%M'], days=['%m/%d %Hh'])
        p.xaxis[0].ticker = DatetimeTicker(desired_num_ticks=20, num_minor_ticks=4)

        # todo.根据上午还是下午确定不同的日界线
        #location使用实数表示，所以必须把时间转换成时间戳，但不清楚为什么要乘以1000
        dateX = df['date_time_X'].tolist()
        del df
        n_days = (dateX[0] - dateX[-1]).days + 1
       
        forecast_span = [
            Span(location=time.mktime((dateX[-1] + timedelta(days=i) + timedelta(hours=12)).timetuple()) * 1000,
                 dimension='height', line_color='red', line_dash='dashed', line_width=2)
            for i in xrange(n_days)]
        for span in forecast_span:
            p.add_layout(span)

        tab = Panel(child=p, title=model)
        tabs.append(tab)
    tabs = Tabs(tabs=tabs)
    save(tabs)  # 直接保存就行


if __name__ == "__main__":

    # f = file('stations.pkl','rb')
    # stations = pickle.load(f)
    # models = pickle.load(f)
    # f.close()
    #
    stations = OrderedDict([
        (u'封丘', ['53983', (114.4166667, 35.03333333)]),
        (u'辉县', ['53985', (113.8166667, 35.45)]),
        (u'新乡', ['53986', (113.8833333, 35.31666667)]),
        (u'获嘉', ['53988', (113.6666667, 35.26666667)]),
        (u'原阳', ['53989', (113.95, 35.05)]),
        (u'卫辉', ['53994', (114.0666667, 35.38333333)]),
        (u'延津', ['53997', (114.1833333, 35.15)]),
        (u'长垣', ['53998', (114.6666667,35.2)]),
    ])
    #######添加新模式需要注意修改的地方：
    models = OrderedDict([
        (u'EC细', ['D:/MICAPSData/ECMWF_HR/2T/999', 'X:/MICAPS/ecmwf_thin/2T/999']),
        (u'EC细 2TMax_3h', ['D:/MICAPSData/ECMWF_HR/MX2T3/999']),
        (u'EC细 2TMin_3h', ['D:/MICAPSData/ECMWF_HR/MN2T3/999']),
        (u'GRAPES_GFS', ['D:/MICAPSData/GRAPES_GFS/T2M_4']),
        (u'GRAPES_MESO', ['D:/MICAPSData/GRAPES_MESO/T2M_4']),
        (u'GRAPES_MESO集合平均',['D:/MICAPSData/SEVP/NWPR/SENGRA/ET0/L20']),
        (u'Japan细', ['D:/MICAPSData/JAPAN_HR/TMP/2']),
        (u'T639细', ['D:/MICAPSData/T639_HR/2T/2','X:/MICAPS/t639_thin/2T/2']),
        (u'T639粗', ['D:/MICAPSData/T639_LR/T2M_4', 'X:/MICAPS/T639/T2M_4']),
        (u'GERMAN细', ['D:/MICAPSData/GERMAN_HR/TMP_2M/2'])
    ])

    now = datetime.now()
    today = now.strftime('%y%m%d')
    nowtime = now.strftime('%y%m%d%H')
    if nowtime < today + "12":
        yesterday = now - timedelta(days=1)
        start_predict = yesterday.strftime('%y%m%d') + '20'
    else:
        start_predict = today + '08'
    #start_predict = "17120920"

    logfile = r'D:\LPWF\log.txt'
    f = open(logfile, 'a')
    f.write("now is:" + now.strftime('%Y_%m_%d %H:%M:%S') + '\n')
    start = time.clock()
    # ***********************测试程序*********************************"
    plot_2T(start_predict, stations, models)
    # ***********************测试程序*********************************"
    end = time.clock()
    elapsed = end - start

    f.write("start is:" + start_predict + '\n')
    f.write("Time used: %.6fs, %.6fms\n" % (elapsed, elapsed * 1000))
    f.write("*****************\n")
    f.close()
