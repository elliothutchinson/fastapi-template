from typing import Any

from pydantic import BaseModel


class CouchbaseConfig(BaseModel):
    cb_enterprise: bool = False
    cb_cluster_url: str = "couchbase://db:8091"
    cb_http_url: str = "http://db:8091"
    cb_default_user: str = "Administrator"
    cb_default_password: str = "password"
    cb_user: str = "admin"
    cb_password: str = "password"
    cb_app_user: str = "appuser"
    cb_app_password: str = "password"
    cb_bucket: str = "api"
    cb_bucket_type: str = "couchbase"
    cb_bucket_ram_quota_mb: int = 100
    cb_memory_quota_mb: int = 256
    cb_index_memory_quota_mb: int = 256
    cb_fts_memory_quota_mb: int = 256
    cb_full_text_port: int = 8094
    cb_durability_timeout_secs: float = 60.0
    cb_operation_timeout_secs: float = 30.0
    cb_n1ql_timeout_secs: float = 5.0


class DbContext(BaseModel):
    bucket: Any
    config: CouchbaseConfig
