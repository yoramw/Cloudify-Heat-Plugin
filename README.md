OpenStack Heat pilot project
============================


Task description
----------------

> Given a running Heat stack deployment (inputs are identity credentials
> and stack name), go over all the infrastructure resources and generate
> a yaml with a list of all the resources and the attributes of each
> resource in an output file.


Environment
----------

The resulting tool will be designed for the following set--up:
* *DevStack*, branch *stable/icehouse*,
* *Ubuntu 12.04 "precise"*.

The template used for testing is available in this repository
(docs/templates).


Installation
------------

First OpenStack is needed. The following command clones *DevStack*
and switches to the proper branch:

    git clone -b stable/icehouse https://github.com/openstack-dev/devstack.git

The tool has been tested using the following `localrc` file:

    ADMIN_PASSWORD=your-password
    DATABASE_PASSWORD=$ADMIN_PASSWORD
    RABBIT_PASSWORD=$ADMIN_PASSWORD
    SERVICE_PASSWORD=$ADMIN_PASSWORD
    SERVICE_TOKEN=your-token
    disable_service n-net
    enable_service q-svc
    enable_service q-agt
    enable_service q-dhcp
    enable_service q-l3
    enable_service q-meta
    enable_service neutron
    IMAGE_URLS+=",http://fedorapeople.org/groups/heat/prebuilt-jeos-images/F17-x86_64-cfntools.qcow2"
    IMAGE_URLS+=",http://shardy.fedorapeople.org/F18-x86_64-cfntools.qcow2"

Due to a bug described
[here](https://bitbucket.org/pypa/setuptools/issue/73/typeerror-dist-must-be-a-distribution)
the recommended installation method is by using *virtualenv* and *pip*:

    cd <root-directory-with-the-tool>
    virtualenv <your-directory>
    source <your-directory>/bin/activate
    pip install .


Using the tool
--------------

Unless explicitly specified in program options, the credentials are
implicitly read from the system environment, as in all *OpenStack* CLIs.
Therefore it is  recommended to "source" *DevStack*'s *openrc* or write
a short script setting up the environment.

Assuming the tool is installed, running `heat_resource_fetcher -h` will
print usage information:
/bin/heat_resource_fetcher -h
usage: heat_resource_fetcher [-h] [--os-auth-url URL] [--os-username username]
                             [--os-password password]
                             [--os-tenant-name tenant name] -s stack name
                             [-o [file]] [-m [file]] [-i]

A tool for fetching resource information for the given stack.

optional arguments:
  -h, --help            show this help message and exit
  --os-auth-url URL     Keystone API endpoint URL
  --os-username username
                        username
  --os-password password
                        password
  --os-tenant-name tenant name
                        tenant name
  -s stack name, --stack-name stack name
                        stack name
  -o [file], --output-file [file]
                        output file; unless specified otherwise the output is
                        written to standard output (`-' is interpreted as
                        standard output)
  -m [file], --mappings-file [file]
                        mappings file; unless specified otherwise the output
                        is heat_mappings.json in the script dir
  -i, --ignore-heat-resources
                        resources seen only by Heat (eg. RouterGateway) will
                        be filtered out


If all necessary environment variables are properly set running
`heat_resource_fetcher -s <stack-name>` will fetch stack information
from *OpenStack* and print it to the standard output. Using the `-o`
flag the output can be written to a file. By default, a jason mapping file named 'heat_mappings.json' is expected.
It can be overridden with a `-m` flag and a path to alternative mapping file.

Example:
/bin/heat_resource_fetcher -s hello_stack --mappings-file ./heat_mappings.json --output-file ./blueprint.yaml

