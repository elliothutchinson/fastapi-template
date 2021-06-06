import logging

import requests
from couchbase import LOCKMODE_WAIT
from couchbase.bucket import Bucket
from couchbase.cluster import Cluster, PasswordAuthenticator
from requests.auth import HTTPBasicAuth

from app.core.db.config import couchbase_config
from app.core.db.models import CouchbaseConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_couchbase_ready(cluster_http_url):
    logger.debug("is_couchbase_ready()")
    r = requests.get(cluster_http_url)
    return r.status_code == 200


def setup_couchbase_services(cluster_http_url, username, password):
    logger.debug("setup_couchbase_services()")
    auth = HTTPBasicAuth(username, password)
    url = f"{cluster_http_url}/node/controller/setupServices"
    r = requests.post(url, data={"services": "kv,index,fts,n1ql"}, auth=auth)
    return (
        r.status_code == 200
        or "cannot change node services after cluster is provisioned" in r.text
    )


def setup_memory_quota(
    cluster_http_url,
    username,
    password,
    memory_quota_mb,
    index_memory_quota_mb,
    fts_memory_quota_mb,
):
    logger.debug("setup_memory_quota()")
    auth = HTTPBasicAuth(username, password)
    url = f"{cluster_http_url}/pools/default"
    r = requests.post(
        url,
        data={
            "memoryQuota": memory_quota_mb,
            "indexMemoryQuota": index_memory_quota_mb,
            "ftsMemoryQuota": fts_memory_quota_mb,
        },
        auth=auth,
    )
    return r.status_code == 200


def setup_index_storage(cluster_http_url, username, password):
    logger.debug("setup_index_storage()")
    auth = HTTPBasicAuth(username, password)
    url = f"{cluster_http_url}/settings/indexes"
    auth = HTTPBasicAuth(username, password)
    r = requests.post(url, data={"storageMode": "forestdb"}, auth=auth)
    return r.status_code == 200


def setup_couchbase_username_password(couchbase_config: CouchbaseConfig):
    logger.debug("setup_couchbase_username_password()")
    url = f"{couchbase_config.cb_http_url}/settings/web"
    auth = HTTPBasicAuth(
        couchbase_config.cb_default_user, couchbase_config.cb_default_password
    )
    r = requests.post(
        url,
        data={
            "username": couchbase_config.cb_user,
            "password": couchbase_config.cb_password,
            "port": "SAME",
        },
        auth=auth,
    )
    return r.status_code == 200


def check_couchbase_username_password(cluster_http_url, username, password):
    logger.debug("check_couchbase_username_password()")
    url = f"{cluster_http_url}/settings/web"
    auth = HTTPBasicAuth(username, password)
    r = requests.get(url, auth=auth)
    return r.status_code == 200


def ensure_couchbase_username_password(couchbase_config: CouchbaseConfig):
    logger.debug("ensure_couchbase_username_password()")
    if setup_couchbase_username_password(couchbase_config=couchbase_config):
        return True
    return check_couchbase_username_password(
        cluster_http_url=couchbase_config.cb_http_url,
        username=couchbase_config.cb_user,
        password=couchbase_config.cb_password,
    )


def config_couchbase(couchbase_config: CouchbaseConfig):
    logger.debug("config_couchbase()")
    assert is_couchbase_ready(couchbase_config.cb_http_url)
    assert setup_couchbase_services(
        cluster_http_url=couchbase_config.cb_http_url,
        username=couchbase_config.cb_default_user,
        password=couchbase_config.cb_default_password,
    ) or setup_couchbase_services(
        cluster_http_url=couchbase_config.cb_http_url,
        username=couchbase_config.cb_user,
        password=couchbase_config.cb_password,
    )
    assert setup_memory_quota(
        cluster_http_url=couchbase_config.cb_http_url,
        username=couchbase_config.cb_default_user,
        password=couchbase_config.cb_default_password,
        memory_quota_mb=couchbase_config.cb_memory_quota_mb,
        index_memory_quota_mb=couchbase_config.cb_index_memory_quota_mb,
        fts_memory_quota_mb=couchbase_config.cb_fts_memory_quota_mb,
    ) or setup_memory_quota(
        cluster_http_url=couchbase_config.cb_http_url,
        username=couchbase_config.cb_user,
        password=couchbase_config.cb_password,
        memory_quota_mb=couchbase_config.cb_memory_quota_mb,
        index_memory_quota_mb=couchbase_config.cb_index_memory_quota_mb,
        fts_memory_quota_mb=couchbase_config.cb_fts_memory_quota_mb,
    )
    if not couchbase_config.cb_enterprise:
        assert setup_index_storage(
            cluster_http_url=couchbase_config.cb_http_url,
            username=couchbase_config.cb_default_user,
            password=couchbase_config.cb_default_password,
        ) or setup_index_storage(
            cluster_http_url=couchbase_config.cb_http_url,
            username=couchbase_config.cb_user,
            password=couchbase_config.cb_password,
        )
    assert ensure_couchbase_username_password(couchbase_config=couchbase_config)
    return True


def is_bucket_created(couchbase_config: CouchbaseConfig):
    logger.debug("is_bucket_created()")
    url = f"{couchbase_config.cb_http_url}/pools/default/buckets/{couchbase_config.cb_bucket}"
    auth = HTTPBasicAuth(couchbase_config.cb_user, couchbase_config.cb_password)
    r = requests.get(url, auth=auth)
    return r.status_code == 200


def create_bucket(couchbase_config: CouchbaseConfig):
    logger.debug("create_bucket()")
    url = f"{couchbase_config.cb_http_url}/pools/default/buckets"
    auth = HTTPBasicAuth(couchbase_config.cb_user, couchbase_config.cb_password)
    data = {
        "name": couchbase_config.cb_bucket,
        "ramQuotaMB": couchbase_config.cb_bucket_ram_quota_mb,
        "bucketType": couchbase_config.cb_bucket_type,
    }
    r = requests.post(url, data=data, auth=auth)
    return r.status_code == 202


def ensure_create_bucket(couchbase_config: CouchbaseConfig):
    logger.debug("ensure_create_bucket()")
    if is_bucket_created(couchbase_config=couchbase_config):
        return True
    return create_bucket(couchbase_config=couchbase_config)


def get_cluster(couchbase_config: CouchbaseConfig):
    logger.debug("get_cluster()")
    cluster = Cluster(couchbase_config.cb_cluster_url)
    authenticator = PasswordAuthenticator(
        couchbase_config.cb_user, couchbase_config.cb_password
    )
    cluster.authenticate(authenticator)
    return cluster


def get_bucket(couchbase_config: CouchbaseConfig):
    logger.debug("get_bucket()")
    cluster = get_cluster(couchbase_config=couchbase_config)
    bucket: Bucket = cluster.open_bucket(
        couchbase_config.cb_bucket, lockmode=LOCKMODE_WAIT
    )
    bucket.timeout = couchbase_config.cb_operation_timeout_secs
    bucket.n1ql_timeout = couchbase_config.cb_n1ql_timeout_secs
    return bucket


def ensure_create_primary_index(bucket: Bucket):
    logger.debug("ensure_create_primary_index()")
    manager = bucket.bucket_manager()
    return manager.n1ql_index_create_primary(ignore_exists=True)


def ensure_create_type_index(bucket: Bucket):
    logger.debug("ensure_create_type_index()")
    manager = bucket.bucket_manager()
    return manager.n1ql_index_create("idx_type", ignore_exists=True, fields=["type"])


def is_couchbase_user_created(couchbase_config: CouchbaseConfig):
    logger.debug("is_couchbase_user_created()")
    url = f"{couchbase_config.cb_http_url}/settings/rbac/users/local/{couchbase_config.cb_app_user}"
    auth = HTTPBasicAuth(couchbase_config.cb_user, couchbase_config.cb_app_password)
    r = requests.get(url, auth=auth)
    return r.status_code == 200


def create_couchbase_user(couchbase_config: CouchbaseConfig):
    logger.debug("create_couchbase_user()")
    url = f"{couchbase_config.cb_http_url}/settings/rbac/users/local/{couchbase_config.cb_app_user}"
    auth = HTTPBasicAuth(couchbase_config.cb_user, couchbase_config.cb_app_password)
    data = {
        "name": "",
        "roles": "ro_admin,bucket_full_access[*]",
        "password": couchbase_config.cb_app_password,
    }
    r = requests.put(url, data=data, auth=auth)
    return r.status_code == 200


def ensure_create_couchbase_user(couchbase_config: CouchbaseConfig):
    logger.debug("ensure_create_couchbase_user()")
    if is_couchbase_user_created(couchbase_config=couchbase_config):
        return True
    return create_couchbase_user(couchbase_config=couchbase_config)


def init_db():
    logger.debug("init_db()")
    config_couchbase(couchbase_config=couchbase_config)
    ensure_create_bucket(couchbase_config=couchbase_config)
    bucket = get_bucket(couchbase_config=couchbase_config)
    ensure_create_primary_index(bucket=bucket)
    ensure_create_type_index(bucket=bucket)
    ensure_create_couchbase_user(couchbase_config=couchbase_config)


if __name__ == "__main__":
    init_db()
