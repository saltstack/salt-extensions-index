The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

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
