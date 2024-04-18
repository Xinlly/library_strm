#!/bin/bash
docker compose down
docker compose create\
&& docker cp ./alipan_strm/filechange.py library_strm:/alipan_strm/\
&& docker cp ./alipan_strm/test.py library_strm:/alipan_strm/\
&& docker cp ./alipan_strm/main.py library_strm:/alipan_strm/\
&& docker compose start
# && docker exec -itd library_strm bash -c "nohup python test.py > /log/test.nohup.log 2>&1"