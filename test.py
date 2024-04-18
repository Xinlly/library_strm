import json
import logging.handlers
import os
import shutil
import urllib.parse

import yaml
import logging

from pathlib import Path

# logging.basicConfig(filename="/log/test.log", filemode='w',
#                     format='%(asctime)s - %(name)s - %(levelname)s -%(module)s:  %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S ',
#                     level=logging.INFO)
logFormat = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s -%(module)s:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S ",
)

fileHandler_test = logging.handlers.RotatingFileHandler(
    filename="/log/test.log", maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
)
fileHandler_test.setLevel(logging.INFO)
fileHandler_test.setFormatter(logFormat)
logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler_test)

fileHandler_testPrint = logging.handlers.RotatingFileHandler(
    filename="/log/test.print.log",
    maxBytes=1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
fileHandler_testPrint.setLevel(logging.INFO)
fileHandler_testPrint.setFormatter(logFormat)
loggerPrint = logging.getLogger("testPrint")
loggerPrint.setLevel(logging.DEBUG)
loggerPrint.addHandler(fileHandler_testPrint)

fileHandler_run = logging.handlers.RotatingFileHandler(
    filename="/log/test.run.log",
    maxBytes=1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
fileHandler_run.setLevel(logging.DEBUG)
fileHandler_run.setFormatter(logFormat)
loggerRun = logging.getLogger("run")
loggerRun.setLevel(logging.DEBUG)
loggerRun.addHandler(fileHandler_run)

def create_strm_file(
    dest_file,
    dest_dir,
    source_file,
    library_dir,
    cloud_type=None,
    cloud_path=None,
    cloud_url=None,
):
    """
    生成strm文件
    :param dest_file:
    :param dest_dir:
    :param library_dir:
    :return:
    """
    try:
        # 获取视频文件名和目录
        video_name = Path(dest_file).name

        dest_path = Path(dest_file).parent

        # 构造.strm文件路径
        strm_path = os.path.join(dest_path, f"{os.path.splitext(video_name)[0]}.strm")
        logger.info(f"替换前本地路径:::{dest_file}")

        if os.path.exists(strm_path):
            loggerPrint.info(f"strm文件已存在，跳过处理::: {strm_path}")
            return

        # 云盘模式
        if cloud_type:
            # 替换路径中的\为/
            dest_file = dest_file.replace(dest_dir, cloud_path)
            dest_file = dest_file.replace("\\", "/")
            dest_file = dest_file.replace("////", "/")
            dest_file = dest_file.replace("///", "/")
            dest_file = dest_file.replace("//", "/")
            loggerPrint.info(f"替换后本地路径:::{dest_file}")
            # dest_file = source_file.replace("\\", "/")
            # dest_file = dest_file.replace(cloud_path, "")
            # 对盘符之后的所有内容进行url转码
            dest_file = urllib.parse.quote(dest_file, safe="")
            if str(cloud_type) == "cd2":
                # 将路径的开头盘符"/mnt/user/downloads"替换为"http://localhost:19798/static/http/localhost:19798/False/"
                dest_file = f"{cloud_url}/static/http/{cloud_url}/False/{dest_file}"
                logger.info(f"替换后cd2路径:::{dest_file}")
            elif str(cloud_type) == "alist":
                dest_file = f"{cloud_url}/d{dest_file}"
                logger.info(f"替换后alist路径:::{dest_file}")
            else:
                logger.error(f"云盘类型 {cloud_type} 错误")
                return
        else:
            # 本地挂载路径转为emby路径
            dest_file = dest_file.replace(dest_dir, library_dir)
            logger.info(f"替换后emby容器内路径:::{dest_file}")

        loggerPrint.info(f"video_name 文件名字::: {video_name}")
        loggerPrint.info(f"dest_path parent 文件目录::: {dest_path}")
        loggerPrint.info(f"strm_path strm路径::: {strm_path}")
        loggerPrint.info(f"emby_play_path emby播放地址::: {dest_file}")

        # 写入.strm文件
        with open(strm_path, "w") as f:
            f.write(dest_file)

        loggerPrint.info(f"已写入 {strm_path}::: {dest_file}")
    except Exception as e:
        loggerPrint.info(str(e))


def copy_files(
    source_dir,
    dest_dir,
    library_dir,
    cloud_type=None,
    cloud_path=None,
    cloud_url=None,
    img_conf=True,
    strm_conf=True,
):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    video_formats = (
        ".mp4",
        ".avi",
        ".rmvb",
        ".wmv",
        ".mov",
        ".mkv",
        ".flv",
        ".ts",
        ".webm",
        ".iso",
        ".mpg",
        ".m2ts",
    )
    # 图片文件识别
    img_formats = (".jpg", ".png", ".jpeg", ".bmp", ".gif", ".webp")
    # 其他文件识别
    nfo_formats = (".nfo", ".xml", ".txt", ".srt", ".ass", ".sub", ".smi", ".ssa")
    for root, dirs, files in os.walk(source_dir):
        # 如果遇到名为'extrafanart'的文件夹，则跳过处理该文件夹，继续处理其他文件夹
        if "extrafanart" in dirs:
            dirs.remove("extrafanart")
        if "BDMV" in dirs:
            loggerPrint.info(f"源文件夹是原盘文件夹,跳过处理::: {source_dir}")
            dirs.remove("BDMV")
        if "CERTIFICATE" in dirs:
            loggerPrint.info(f"源文件夹是原盘文件夹,跳过处理::: {source_dir}")
            dirs.remove("CERTIFICATE")

        for file in files:
            try:
                source_file = os.path.join(root, file)
                loggerPrint.info(f"处理源文件::: {source_file}")

                dest_file = os.path.join(
                    dest_dir, os.path.relpath(source_file, source_dir)
                )
                loggerPrint.info(f"开始生成目标文件::: {dest_file}")

                # 创建目标目录中缺少的文件夹
                if not os.path.exists(Path(dest_file).parent):
                    os.makedirs(Path(dest_file).parent)

                # 如果目标文件已存在，跳过处理
                if os.path.exists(dest_file):
                    loggerPrint.info(f"文件已存在，跳过处理::: {dest_file}")
                    continue

                if file.lower().endswith(video_formats):
                    if not strm_conf:
                        loggerPrint.info(f"视频strm处理未开，复制视频文件到: {dest_file} ")
                        shutil.copy2(source_file, dest_file)
                    # 如果视频文件小于1MB，则直接复制，不创建.strm文件
                    elif os.path.getsize(source_file) < 1024 * 1024:
                        loggerPrint.info(f"视频文件小于1MB的视频文件到:::{dest_file}")
                        shutil.copy2(source_file, dest_file)
                    else:
                        # 创建.strm文件
                        create_strm_file(
                            dest_file=dest_file,
                            dest_dir=dest_dir,
                            source_file=source_file,
                            library_dir=library_dir,
                            cloud_type=cloud_type,
                            cloud_path=cloud_path,
                            cloud_url=cloud_url,
                        )
                elif file.lower().endswith(img_formats):
                    if not img_conf:
                        loggerPrint.info(f"图片处理未开，跳过处理: {source_file} ")
                        return
                    # 图片文件复制
                    shutil.copy2(source_file, dest_file)
                    loggerPrint.info(f"复制图片文件 {source_file} 到 {dest_file}")
                elif file.lower().endswith(nfo_formats):
                    # 元数据、字幕等文件复制
                    shutil.copy2(source_file, dest_file)
                    loggerPrint.info(f"复制其他文件 {source_file} 到 {dest_file}")
            except Exception as e:
                logger.error(f"copy_files error: {e}")
                loggerPrint.info(str(e))


loggerRun.info("开始运行")

filepath = os.path.join("/mnt", "config.yaml")

with open(filepath, "r") as f:  # 用with读取文件更好
    configs = yaml.load(f, Loader=yaml.FullLoader)  # 按字典格式读取并返回

monitor_confs = configs["sync"]["monitor_confs"]
if not isinstance(monitor_confs, list):
    monitor_confs = [monitor_confs]
# 存储目录监控配置
for monitor_conf in monitor_confs:
    if not isinstance(monitor_conf, dict):
        monitor_conf = json.loads(monitor_conf)
    source_dir = monitor_conf.get("source_dir")
    dest_dir = monitor_conf.get("dest_dir")
    library_dir = monitor_conf.get("library_dir")
    cloud_type = monitor_conf.get("cloud_type")
    cloud_path = monitor_conf.get("cloud_path")
    cloud_url = monitor_conf.get("cloud_url")
    img_conf = monitor_conf.get("copy_img")
    strm_conf = monitor_conf.get("create_strm")

    loggerPrint.info(f"source::: {source_dir}")
    loggerPrint.info(f"dest_dir::: {dest_dir}")
    loggerPrint.info(f"library_dir::: {library_dir}")

    loggerPrint.info(f"开始初始化处理文件 {source_dir}")

    # 批量生成strm文件
    copy_files(
        source_dir,
        dest_dir,
        library_dir,
        cloud_type=cloud_type,
        cloud_path=cloud_path,
        cloud_url=cloud_url,
        img_conf=img_conf,
        strm_conf=strm_conf,
    )

    loggerPrint.info(f"{source_dir} 初始化处理文件完成")
