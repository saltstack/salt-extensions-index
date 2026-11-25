The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 2.0.0 (2026-11-24)


### Breaking changes

- Renamed state functions `create_target_group` → `target_group_present` and `delete_target_group` → `target_group_absent`; fixed `targets_registered` and `targets_deregistered` to issue a single bulk API call instead of one call per target.


### Changed

- Changed `boto3_elbv2.target_group_exists` to accept explicit `name` or `arn` keyword arguments instead of a single positional argument that required ARN string-sniffing.


### Added

- Add security-group rule description support to `boto3_secgroup.authorize`, rule readback, and `boto3_secgroup.present`. Description-only changes use the new `boto3_secgroup.update_rule_description` function without revoking rules. Omitted or null state descriptions remain unmanaged; empty strings clear descriptions. `boto3_secgroup.revoke` accepts description metadata without using it to identify the rule. Normalize numeric protocol comparisons so integer `-1` matches AWS's string `"-1"` and does not trigger unnecessary rule replacement. Updating existing descriptions requires `ec2:UpdateSecurityGroupRuleDescriptionsIngress` or `ec2:UpdateSecurityGroupRuleDescriptionsEgress` permission.
- Added `boto3_elbv2.describe_target_group` to look up a target group by `name` or `arn` and return its full AWS dict.
- Added `boto3_rds.master_user_secret_ready` to wait with a bounded timeout until an RDS-managed master secret is active.
- Added `boto3_secretsmanager.managed_rotation_present` and `boto3_secretsmanager.configure_managed_rotation` to update schedules for service-managed secrets without specifying a Lambda rotation function or starting an immediate rotation.
- Added `manage_master_user_password` and `master_user_secret_kms_key_id` support to RDS execution calls, plus a `boto3_rds.master_user_password_managed` state for explicitly enabling RDS-managed master credentials on an existing instance.
- Added a `boto3_secretsmanager.rotation_present` state for configuring Lambda-based automatic rotation schedules without immediately rotating the secret by default.


### Fixed

- Fix `boto3_secgroup.present` for `all` (`-1`) protocol rules. Rules defined without `from_port`/`to_port` no longer raise `KeyError` during comparison, and ports are stripped before authorize/revoke calls since AWS rejects `FromPort`/`ToPort` when the protocol is `-1` ("When protocol is ALL, you cannot specify from-port"). Applies to both ingress and egress rules.
- Fixed local ZIP package hash comparison in `boto3_lambda.function_present` on Python 3.
- Stringify datetime values in ``boto3_ssm`` command returns (``send_command``, ``get_command_invocation``, ``list_command_invocations``). Raw boto3 datetimes (e.g. ``ExpiresAfter``) leaked into state returns and broke JSON consumers such as the Salt netapi, which returned HTTP 500 for ``jobs.lookup_jid`` on any orchestration embedding the result.

## 1.2.0 (2026-09-29)


### Added

- Added `boto3_ec2.create_launch_template`, `boto3_ec2.delete_launch_template`, and `boto3_ec2.describe_launch_templates` execution functions along with `boto3_ec2.launch_template_present` and `boto3_ec2.launch_template_absent` state functions.
- Added `boto3_ec2.get_dns_name` to return the private or public DNS name of an EC2 instance looked up by Name tag or instance ID.
- Added `boto3_ec2.instance_metadata_options` state to apply Instance Metadata Service (IMDS) options to any matching instances targeted by ID, Name tag, arbitrary tags, or raw boto3 filters.
- Added `boto3_ssm.run_shell_script_document` to fetch a script via Salt's file server, optionally render it as a Jinja template, and dispatch it via SSM Run Command targeting instances by tags or instance IDs.

## 1.1.0 (2026-09-15)


### Changed

- Added support for associating secondary CIDR blocks with VPCs through the `boto3_vpc` execution module and state, including backward-compatible list input for `cidr_block`.
- Expanded `boto3_rds` read-replica management with configurable instance, networking, storage, upgrade, parameter-group, option-group, accessibility, tagging, and AWS connection settings.
- Updated `boto3_vpc.route_table_absent` to disassociate non-main route-table associations before deleting a route table.


### Fixed

- Updated documentaion for consistency. [#18](https://github.com/salt-extensions/saltext-boto3/issues/18)


### Added

- Added the `boto3_secretsmanager` execution module and state for creating, reading, and updating AWS Secrets Manager secrets.
- Expanded `boto3_s3` with object get, put, delete, download, and presigned URL operations, including AWS connection options, extra arguments, validation, and error handling.

## 1.0.1 (2026-07-10)


### Fixed

- Fixed boto3_vpc.dhcp_options_present to associate an existing DHCP options set to the target VPC when the desired options already exist but are not currently attached.
- Fixed profile-string authentication to use named AWS profiles when no static credentials are set, and isolated profile-only client caching by profile name to prevent cross-profile reuse.

## 1.0.0 (2026-04-25)


### Removed

- Removed all legacy boto2 ``boto_*`` execution modules and states; use the ``boto3_*`` equivalents instead. [#boto2-legacy](https://github.com/salt-extensions/saltext-boto3/issues/boto2-legacy)


### Added

- Initial release of the ``saltext-boto3`` Salt Extension, carved out of Salt core and modernized to require boto3 1.28+/botocore 1.31+ on Python 3.10+. [#initial-extension](https://github.com/salt-extensions/saltext-boto3/issues/initial-extension)
