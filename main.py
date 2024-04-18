import multiprocessing

from fastapi import FastAPI
import uvicorn as uvicorn
from uvicorn import Config

import filechange
import os

if __name__ == '__main__':
    os.system('nohup python test.py > /log/test.run.log 2>&1 &')
    # 文件监控
    filechange.FileChange().start()
    # App
    App = FastAPI(title='library_strm',
                  openapi_url="/api/v1/openapi.json")

    # uvicorn服务
    Server = uvicorn.Server(Config(App, host='0.0.0.0', port=33455,
                                   reload=False, workers=multiprocessing.cpu_count()))
    # 启动服务
    Server.run()
