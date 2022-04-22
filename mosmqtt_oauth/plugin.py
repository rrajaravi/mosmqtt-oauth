import os
import logging
import requests

import redis

from .lib import topic_matches_sub

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MOSQUITTO_LOG_DIR = "/var/log/mosquitto/"
PLUGIN_LOG_FILE_NAME = "mosmqtt_oauth.log"
PLUGIN_LOG_FILE = os.path.join(MOSQUITTO_LOG_DIR, PLUGIN_LOG_FILE_NAME)

fh = logging.FileHandler(PLUGIN_LOG_FILE if os.path.exists(
    MOSQUITTO_LOG_DIR) else PLUGIN_LOG_FILE_NAME)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

REDIS_CONN = None


def user_cache_key(token):
    return 'mosq:' + token


def user_acl_cache_key(token):
    return user_cache_key(token) + ':acl'


def userDetails(token: str) -> dict:
    MQTT_EXTERNAL_AUTH_URL = os.environ['MQTT_EXTERNAL_AUTH_URL']

    try:
        response = requests.get(MQTT_EXTERNAL_AUTH_URL,
                                headers={
                                    'Authorization': 'Bearer {}'.format(token),
                                    'Content-Type': 'application/json'
                                })
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.exception(e)
        return {}
    data = response.json()
    if not 'topics' in data or not 'email' in data:
        logger.error("Invalid response from auth system: %s", data)
        return {}
    return data


def plugin_init(opts):
    REDIS_HOST = os.environ['REDIS_HOST']
    REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
    REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
    REDIS_SSL = os.environ.get('REDIS_SSL') in {
        '1', 'true', 'True', 'TRUE', None
    }
    REDIS_DB = os.environ.get('REDIS_DB', 0)

    global REDIS_CONN

    REDIS_CONN = redis.StrictRedis(
        host=REDIS_HOST,
        ssl=REDIS_SSL,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
    )
    logger.info('redis initialized: %s %s', REDIS_HOST, REDIS_PORT)


def unpwd_check(username: str, password: str) -> bool:
    token = username
    user = userDetails(token)
    if not user:
        logger.error("Login failed for User: %s", password)
        return False

    REDIS_CONN.hset(user_cache_key(token), 'user', user["email"])
    REDIS_CONN.delete(user_acl_cache_key(token))
    for allowedTopic in user["topics"]:
        REDIS_CONN.lpush(user_acl_cache_key(token), allowedTopic)

    return True


def acl_check(client_id: str, username: str, topic: str, access: str,
              payload) -> bool:
    if username is None:
        logger.error('Authentication required for acl check')
        return False
    logger.debug("Checking User ACL")

    user = REDIS_CONN.hget(user_cache_key(username), 'user')
    if user:
        allowedTopics = REDIS_CONN.lrange(user_acl_cache_key(username), 0, -1)
        if not allowedTopics:
            logger.warn('No ACL found for User: %s', user)
            return False

        matches = False
        for allowedTopic in allowedTopics:
            matches = topic_matches_sub(allowedTopic.decode(),
                                        topic)
            if matches:
                break
        if matches is False:
            logger.info(
                "User: %s requested topic: %s not allowed. Allowed Topics: %s",
                user, topic, allowedTopics)

    logger.info('ACL: user=%s topic=%s, matches = %s, payload = %r' %
                (user, topic, matches, payload))
    return matches
