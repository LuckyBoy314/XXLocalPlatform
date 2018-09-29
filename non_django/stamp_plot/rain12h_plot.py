# -*- coding:utf-8 -*-

from pyMicaps import Diamond4
import datetime, os
import arcpy.mapping as mp

def produce_arcgis_asc(init_time)

    #init_time = '18081620'  # 起报时间
    micaps_source_dir = 'D:/MICAPSData/'
    temp_dir = 'D:/rain_model/%s/' % init_time
    product_dir = 'Y:/model_rain/'
    mxd_path = os.getcwd() + u'/data/多模式降水对比模板.mxd'

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for valid_h in range(12, 132, 12):

        if valid_h == 12:
            fs = [r'%sECMWF_HR\RAIN12\999\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sGERMAN_HR\APCP\999\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sGRAPES_GFS\RAIN12_4\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sGRAPES_MESO\RAIN_4\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sJAPAN_HR\APCP\0\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sT639_HR\RAIN12\999\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  ]
        else:
            fs = [r'%sECMWF_HR\RAIN12\999\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sGERMAN_HR\RAIN12\999\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sGRAPES_GFS\RAIN12_4\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sGRAPES_MESO\RAIN12_4\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sJAPAN_HR\RAIN12\0\%s.%03d' % (micaps_source_dir, init_time, valid_h),
                  r'%sT639_HR\RAIN12\999\%s.%03d' % (micaps_source_dir, init_time, valid_h), 
                  ]
        for f in fs:
            if os.path.exists(f):
                f_cut_source = f[len(micaps_source_dir):]
                out = ''.join(
                    [temp_dir, f_cut_source[0:f_cut_source.find('\\')], '_', '%03d' % valid_h, '.asc'])
                if not os.path.exists(out):
                    d = Diamond4(f)
                    d.convert_to_EsriAscii(out)


    
def plot_with_arcpy(init_time, replace_workspace_dir,origin_workspace_dir, images_dir, mxd_path, resolution=100):
    mxd = mp.MapDocument(mxd_path)
    
    # 修改预报时效
    txts = mp.ListLayoutElements(mxd, "TEXT_ELEMENT")
    init_time_datetime = datetime.datetime.strptime(init_time, '%y%m%d%H')
    for valid_h, i in zip(range(0, 132, 12), range(23, 12, -1)):
        beg = (init_time_datetime + datetime.timedelta(hours=valid_h)).strftime('%d%H')
        end = (init_time_datetime + datetime.timedelta(hours=valid_h + 12)).strftime('%d%H')
        txts[i].text = beg + '-' + end

    # 替换数据源
    mxd.replaceWorkspaces(origin_workspace_dir, "RASTER_WORKSPACE", replace_workspace_dir, "RASTER_WORKSPACE", False)
    # 处理缺失数据
    broken_lyrs = mp.ListBrokenDataSources(mxd)
    for broken_lyr in broken_lyrs:
        # 让缺失数据图层及与其同在一个dataframe里其他的图层不显示
        broken_df = mp.ListDataFrames(mxd, broken_lyr.name)
        if len(broken_dfs) > 0:
            lyrs_in_broken_df = mp.ListLayers(mxd, "", broken_df[0])
            for lyr in lyrs_in_broken_df:
                lyr.visible = False
                
    #mxd.save() 不要保存
    mp.ExportToJPEG(mxd, os.path.join(images_dir, init_time), resolution=resolution)
    
    
if __name__ == "__main__":
    pass
