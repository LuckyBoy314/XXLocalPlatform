# from django.db import models
#
#
# class TimeSeriesModelToStations(models.Model):
#     start_time = models.CharField(verbose_name='起报时间', max_length=8)
#     model_name = models.CharField(verbose_name='模式名', max_length=20)
#     element = models.CharField(verbose_name='物理量', max_length=50)
#     level = models.CharField(verbose_name='层次', max_length=50)
#     interpolation = models.CharField(verbose_name='插值方法', max_length=50)
#
#     class Meta:
#         verbose_name = '模式站点插值时间序列'
#         verbose_name_plural = '模式站点插值时间序列'
#
#
# class SpanSeriesModelToStations(models.Model):
#     from_time_series = models.ForeignKey(TimeSeriesModelToStations, related_name='span_series')
#     start_hour = models.IntegerField(verbose_name='起始时刻')
#     span_hours = models.IntegerField(verbose_name='统计间隔')
#     stat_method = models.CharField(verbose_name='统计方法', max_length=50)
#
#     class Meta:
#         verbose_name = '模式站点插值时间间隔统计序列'
#         verbose_name_plural = '模式站点插值时间间隔统计序列'
#
#
# class TimeSeriesData(models.Model):
#     series_id = models.ForeignKey(TimeSeriesModelToStations, verbose_name='序列id', related_name='time_series')
#     time_index = models.IntegerField(verbose_name='时间索引')
#     station_0 = models.FloatField(verbose_name='封丘')
#     station_1 = models.FloatField(verbose_name='辉县')
#     station_2 = models.FloatField(verbose_name='新乡')
#     station_3 = models.FloatField(verbose_name='获嘉')
#     station_4 = models.FloatField(verbose_name='原阳')
#     station_5 = models.FloatField(verbose_name='卫辉')
#     station_6 = models.FloatField(verbose_name='延津')
#     station_7 = models.FloatField(verbose_name='长垣')
#
#
# class SpanSeriesData(models.Model):
#     series_id = models.ForeignKey(TimeSeriesModelToStations, verbose_name='序列id', related_name='span_series')
#     time_index = models.IntegerField(verbose_name='时间索引')
#     station_0 = models.FloatField(verbose_name='封丘')
#     station_1 = models.FloatField(verbose_name='辉县')
#     station_2 = models.FloatField(verbose_name='新乡')
#     station_3 = models.FloatField(verbose_name='获嘉')
#     station_4 = models.FloatField(verbose_name='原阳')
#     station_5 = models.FloatField(verbose_name='卫辉')
#     station_6 = models.FloatField(verbose_name='延津')
#     station_7 = models.FloatField(verbose_name='长垣')