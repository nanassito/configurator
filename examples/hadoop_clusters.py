import os
from functools import partial

from configurator import Config, ConfigSet, Template
from examples.hadoop_types import ClusterConfigSchema
from examples.hadoop_templates import (
    base_hadoop_cluster_config_template,
    hive_cluster_config,
)
from writers import file_writer, json_formatter


CONFIG_ROOT = os.path.join(os.path.dirname(__file__), "generated_configs")


def get_config_json_writer(cluster_name: str) -> None:
    return partial(
        file_writer,
        formatter=json_formatter,
        path=os.path.join(CONFIG_ROOT, cluster_name, "config.json"),
    )


ConfigSet(
    configs=[
        Config(
            schema=ClusterConfigSchema,
            writer=get_config_json_writer("NewHiveCluster"),
            templates=[
                base_hadoop_cluster_config_template,
                hive_cluster_config,
                Template(
                    ec2_settings=Template(
                        compute_external_id="SOMEUNIQID",
                        compute_role_arn="arn:aws:iam::0987654321:role/my-fancy-role",
                        subnet_id="subnet-01234567,subnet-89abcdef,subnet-fedcba98,subnet-7654321",
                        vpc_id="vpc-01234567",
                    )
                ),
            ],
            config_modifiers=None,
            config_validators=None,
        )
    ],
    configset_modifiers=None,
    configset_validators=None,
).materialize()


ConfigSet(
    configs=[
        Config(
            schema=ClusterConfigSchema,
            writer=get_config_json_writer("SparkCluster"),
            templates=[
                base_hadoop_cluster_config_template,
                Template(
                    ec2_settings=Template(
                        compute_external_id="ANOTHERUNIQID",
                        compute_role_arn="arn:aws:iam::1234567890:role/my-fancy-role",
                        subnet_id="subnet-76543210",
                        vpc_id="vpc-89abcdef",
                    ),
                    engine_config=None,
                ),
            ],
        )
    ]
).materialize()
