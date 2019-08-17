from configurator.compiler import Template


base_hadoop_cluster_config_template = Template(
    datadog_settings={"datadog_api_token": "", "datadog_app_token": ""},
    disallow_cluster_termination=True,
    ec2_settings=Template(
        aws_preferred_availability_zone="Any",
        aws_region="us-east-1",
        bastion_node_port=None,
        bastion_node_public_dns=None,
        bastion_node_user=None,
        compute_validated=True,
        instance_tenancy=None,
        master_elastic_ip=None,
        role_instance_profile=None,
        use_account_compute_creds=False,
    ),
    enable_ganglia_monitoring=True,
)


hive_cluster_config = Template(
    engine_config=Template(
        hive_settings=Template(
            hive_version="2.1.1",
            is_hs2=True,
            is_metadata_cache_enabled=False,
            overrides="ref://hive-overrides.properties",
        ),
        type="hadoop2",
    )
)
