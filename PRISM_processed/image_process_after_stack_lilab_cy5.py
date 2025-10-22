import sys
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from tqdm import tqdm
import numpy as np
# 添加lib目录到Python路径
# lib_path = Path(r"D:\3_PRISM\PRISM_Code-main\Image_process\lib")
# if str(lib_path) not in sys.path:
#     sys.path.insert(0, str(lib_path))
from lib.utils.io_utils import get_tif_list
from lib.fstack import stack_cyc
from lib.cidre import cidre_walk
from lib.register import register_meta
from lib.stitch import patch_tiles
from lib.stitch import template_stitch
from lib.stitch import stitch_offset
from lib.os_snippets import try_mkdir
from lib.register import register_manual
from lib.stitch import stitch_manual
from skimage.transform import resize
from skimage.util import img_as_uint

import shutil
from skimage.io import imread
from skimage.io import imsave


SRC_DIR = Path(r"D:\3_PRISM")
BASE_DIR = Path(r"D:\3_PRISM")
RUN_ID = '20251021_2dmouse_huanglab/20220918_PRISM_Brain_30plex_DAPI'
src_dir = SRC_DIR / RUN_ID
dest_dir = BASE_DIR / f'{RUN_ID}_processed'

aif_dir = dest_dir / 'focal_stacked'
sdc_dir = dest_dir / 'background_corrected'
rgs_dir = dest_dir / 'registered'
stc_dir = dest_dir / 'stitched'
rsz_dir = dest_dir / 'resized'

TileX, TileY = 28, 22

def resize_pad(img, size):
    img_resized = resize(img, size, anti_aliasing=True)
    img_padded = np.zeros(img.shape)
    y_start, x_start = (img.shape[0] - size[0]) // 2, (img.shape[1] - size[1]) // 2
    img_padded[y_start:y_start+size[0], x_start:x_start+size[1]] = img_resized
    img_padded = img_as_uint(img_padded)
    return img_padded


def resize_dir(in_dir, out_dir, chn):
    Path(out_dir).mkdir(exist_ok=True)
    # chn_sizes = {'cy5': 2046, 'TxRed': 2047, 'FAM': 2045, 'DAPI': 2044}
    chn_sizes = {'cy5': 2302, 'TxRed': 2303, 'FAM': 2301, 'DAPI': 2300}
    size = chn_sizes[chn]
    im_list = list(Path(in_dir).glob(f'*.tif'))
    for im_path in tqdm(im_list, desc=Path(in_dir).name):
        im = imread(im_path)
        im = resize_pad(im, (size, size))
        imsave(Path(out_dir)/im_path.name, im, check_contrast=False)


def resize_batch(in_dir, out_dir):
    try_mkdir(out_dir)
    cyc_paths = list(Path(in_dir).glob('cyc_*_*'))
    for cyc_path in cyc_paths:
        chn = cyc_path.name.split('_')[-1]
        if chn == 'cy5':
            shutil.copytree(cyc_path, Path(out_dir)/cyc_path.name)
        else:
            resize_dir(cyc_path, Path(out_dir)/cyc_path.name, chn)


def main():
    # 焦点堆叠（如果还没处理的话）
    # raw_cyc_list = list(src_dir.glob('cyc_*'))
    # for cyc in raw_cyc_list:
    #   cyc_num = int(cyc.name.split('_')[1])
    #   stack_cyc(src_dir, aif_dir, cyc_num)

    # 背景校正
    cidre_walk(aif_dir, sdc_dir)

    # 创建注册目录
    rgs_dir.mkdir(exist_ok=True)
    
    # 修改参考通道：从cy3改为cy5
    ref_cyc = 1
    ref_chn = 'cy5'  # 主参考通道改为cy5
    ref_chn_1 = 'cy5'  # 模板拼接通道
    
    # 使用cy5通道获取图像列表
    ref_dir = sdc_dir / f'cyc_{ref_cyc}_{ref_chn}'
    im_names = get_tif_list(ref_dir)

    # 修改通道列表：只使用存在的cy5通道
    meta_df = register_meta(str(sdc_dir), str(rgs_dir), ['cy5'], im_names, ref_cyc, ref_chn)
    meta_df.to_csv(rgs_dir / 'integer_offsets.csv')
    
    # 修改手动配准：将所有参考通道改为cy5
    register_manual(rgs_dir/'cyc_1_cy5', sdc_dir / 'cyc_1_FAM', rgs_dir/'cyc_1_FAM')
    register_manual(rgs_dir/'cyc_1_cy5', sdc_dir / 'cyc_1_TxRed', rgs_dir/'cyc_1_TxRed')
    register_manual(rgs_dir/'cyc_1_cy5', sdc_dir / 'cyc_1_DAPI', rgs_dir/'cyc_1_DAPI')
    
    # 分块处理
    patch_tiles(rgs_dir/f'cyc_{ref_cyc}_{ref_chn}', TileX * TileY)

    # 尺寸调整
    resize_batch(rgs_dir, rsz_dir)

    # 模板拼接
    stc_dir.mkdir(exist_ok=True)
    template_stitch(rsz_dir/f'cyc_{ref_cyc}_{ref_chn_1}', stc_dir, TileX, TileY)

    # 偏移拼接
    offset_df = pd.read_csv(rgs_dir / 'integer_offsets.csv', index_col=0)
    stitch_offset(rgs_dir, stc_dir, offset_df)


def test():
    rgs_dir.mkdir(exist_ok=True)
    ref_cyc = 1
    ref_chn = 'cy5'  # 修改为cy5
    ref_dir = sdc_dir / f'cyc_{ref_cyc}_{ref_chn}'
    im_names = get_tif_list(ref_dir)
    
    # stc_dir.mkdir(exist_ok=True)
    # patch_tiles(rgs_dir/'cyc_1_cy5', 29 * 19)  # 修改为cy5
    # template_stitch(rgs_dir/'cyc_1_cy5', stc_dir, 29, 19)  # 修改为cy5
    stc_dir.mkdir(exist_ok=True)
    patch_tiles(rgs_dir/f'cyc_{ref_cyc}_{ref_chn}', TileX * TileY)  # 使用全局TileX, TileY
    template_stitch(rsz_dir/f'cyc_{ref_cyc}_{ref_chn_1}', stc_dir, TileX, TileY)  # 使用全局TileX, TileY

    offset_df = pd.read_csv(rgs_dir / 'integer_offsets.csv')
    offset_df = offset_df.set_index('Unnamed: 0')
    offset_df.index.name = None
    stitch_offset(rgs_dir, stc_dir, offset_df)


def stitch_test():
    offset_df = pd.read_csv(rgs_dir / 'integer_offsets.csv')
    offset_df = offset_df.set_index('Unnamed: 0')
    offset_df.index.name = None
    register_manual(rgs_dir/'cyc_10_DAPI', sdc_dir / 'cyc_11_DAPI', rgs_dir/'cyc_11_DAPI')
    stitch_manual(rgs_dir/'cyc_11_DAPI', stc_dir, offset_df, 10, bleed=30)
    im = imread(stc_dir/'cyc_11_DAPI.tif')
    im_crop = im[10000:20000, 10000:20000]
    imsave(stc_dir/'cyc_11_DAPI_crop.tif', im_crop)


if __name__ == "__main__":
    main()