from dataclasses import dataclass
from typing import Dict, Optional

from configurator.schemas import DictSchema, JsonSchema


@dataclass
class HiveSettingsSchema(DictSchema):
    hive_version: str
    is_hs2: bool
    is_metadata_cache_enabled: bool
    overrides: str


@dataclass
class EngineConfigSchema(DictSchema):
    hive_settings: HiveSettingsSchema
    type: str


@dataclass
class EC2SettingsSchema(DictSchema):
    aws_preferred_availability_zone: str
    aws_region: str
    bastion_node_port: Optional[str]
    bastion_node_public_dns: Optional[str]
    bastion_node_user: Optional[str]
    compute_external_id: str
    compute_role_arn: str
    compute_validated: bool
    instance_tenancy: Optional[str]
    master_elastic_ip: Optional[str]
    role_instance_profile: Optional[str]
    subnet_id: str
    use_account_compute_creds: bool
    vpc_id: str


@dataclass
class ClusterConfigSchema(JsonSchema):
    datadog_settings: Dict[str, str]
    disallow_cluster_termination: bool
    ec2_settings: EC2SettingsSchema
    enable_ganglia_monitoring: bool
    engine_config: EngineConfigSchema
