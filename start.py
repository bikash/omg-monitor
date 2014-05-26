#!/usr/bin/env python

import sys
import multiprocessing
import logging
import json
from monitor import monitor
from utils import pingdom # Pingdom API wrapper
import redis

# Connect to redis server
_REDIS_SERVER = redis.Redis("localhost")

# Use logging
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s/%(processName)s][%(asctime)s] %(name)s %(message)s',
                    filename="server/public/log/monitor.log",
                    maxBytes=1024*1024*2, 
                    backupCount=10)
logger = logging.getLogger(__name__)
multiprocessing.log_to_stderr(logging.DEBUG)

# Test the redis server
try:
    response = _REDIS_SERVER.client_list()
except redis.ConnectionError:
    logger.error("Redis server is down.")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Usage: start.py [username] [password] [appkey] [CHECK_ID_1] [CHECK_ID_2] ..."
        sys.exit(0)
    elif len(sys.argv) == 4:
        username = sys.argv[1]
        password = sys.argv[2]
        appkey = sys.argv[3]

        # Pingdom instance
        ping = pingdom.Pingdom(username=username, password=password, appkey=appkey)

        # Get accounts checks
        try:
            checks = ping.method('checks')
        except Exception:
            logger.error("Could not connect to Pingdom")
            sys.exit(0)

        # get just the checks
        checks = checks['checks']

        # flush redis db and write the checks in it
        _REDIS_SERVER.flushdb()
        for check in checks:
            _REDIS_SERVER.rpush("checks", check['id'])
            _REDIS_SERVER.set("check:%s" % check['id'], check['name'])

        # Start the monitors sessions
        for check in checks:
            check_id = int(check['id'])
            check_name = check['name']
            
            logger.info("[%s] Starting..." % check_name)
            
            job = multiprocessing.Process(target=monitor.run, args=(check_id, check_name, username, password, appkey))
            job.start()
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        appkey = sys.argv[3]

        # Pingdom instance
        ping = pingdom.Pingdom(username=username, password=password, appkey=appkey)

        # Get accounts checks
        try:
            checks = ping.method('checks')
        except Exception:
            logger.error("Could not connect to Pingdom")
            sys.exit(0)
        
        # get just the checks
        checks = checks['checks']
        
        _REDIS_SERVER.flushdb()
         
        jobs_list = []
        # Start the monitors sessions
        for id in sys.argv[4:]:
            check_id = int(id)
            check_name = None

            # Check if ID exist
            for check in checks:
                if check_id == check['id']:
                    check_name = check['name']
        
            if check_name == None:
                logger.warn("Check ID %s doesn't exist. Skipping this one." % check_id)
                continue
            else: # Write check to Redis only if it exists and if is monitoring
                _REDIS_SERVER.rpush("checks", check_id)
                _REDIS_SERVER.set("check:%s" % check_id, check_name)
            
            logger.info("[%s] Starting..." % check_name)
            
            jobs_list.append(multiprocessing.Process(target=monitor.run, args=(check_id, check_name, username, password, appkey)))
            jobs_list[len(jobs_list) - 1].start()

    for job in jobs_list:
        logger.info("Joining %s." % job.name)
        job.join()