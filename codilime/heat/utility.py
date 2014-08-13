# coding=utf-8
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from __future__ import print_function
import sys

from heatclient import client as heat_client
from keystoneclient.v2_0 import client as keystone_client
from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client


_API_VERSIONS = {
    'orchestration': '1',
    'compute': '3',
    'network': '2'
}


class APIClients:
    def __init__(self,
                 keystone_endpoint_url,
                 username,
                 password,
                 tenant_name):
        self.keystone_endpoint_url = keystone_endpoint_url
        self.username = username
        self.password = password
        self.tenant_name = tenant_name
        self.keystone_client = None
        self.heat_client = None
        self.nova_client = None
        self.neutron_client = None

    def keystone(self):
        if self.keystone_client is None:
            self.keystone_client = keystone_client.Client(
                auth_url=self.keystone_endpoint_url,
                username=self.username,
                password=self.password,
                tenant_name=self.tenant_name)
        return self.keystone_client

    def heat(self):
        if self.heat_client is None:
            keystone = self.keystone()
            endpoint_url = keystone.service_catalog.url_for(
                service_type='orchestration',
                endpoint_type='publicURL')
            self.heat_client = heat_client.Client(
                _API_VERSIONS['orchestration'],
                endpoint_url,
                token=keystone.auth_token)
        return self.heat_client

    def nova(self):
        if self.nova_client is None:
            keystone = self.keystone()
            self.nova_client = nova_client.Client(
                _API_VERSIONS['compute'],
                self.username,
                None,
                self.tenant_name,
                auth_url=self.keystone_endpoint_url,
                auth_token=keystone.auth_token)
        return self.nova_client

    def neutron(self):
        if self.neutron_client is None:
            keystone = self.keystone()
            endpoint_url = keystone.service_catalog.url_for(
                service_type='network',
                endpoint_type='publicURL')
            self.neutron_client = neutron_client.Client(
                username=self.username,
                tenant_name=self.tenant_name,
                endpoint_url=endpoint_url,
                token=keystone.auth_token)
        return self.neutron_client


def get_stack_by_name(heat_client, stack_name):
    # The generator returned by client.stacks.list(...) has *at most*
    #   one element. Therefore there is no problem in casting it to
    #   a list.
    stacks = list(
        heat_client.stacks.list(
            filters={'name': stack_name})
    )
    if len(stacks) == 0:
        print('\'' + stack_name + '\': no such stack',
              file=sys.stderr)
        sys.exit(1)
    stack = stacks[0]
    return stack.to_dict()

def _normalise_server_info(server_info):
    return {
        'server': server_info
    }


def _get_nova_server_info(
        api_clients,
        server_id):
    return _normalise_server_info(
        api_clients.nova().servers.get(server_id).to_dict()
    )



def _get_neutron_net_info(
        api_clients,
        net_id):
    return api_clients.neutron().show_network(net_id)


def _get_neutron_subnet_info(
        api_clients,
        subnet_id):
    return api_clients.neutron().show_subnet(subnet_id)


def _get_neutron_router_info(
        api_clients,
        router_id):
    return api_clients.neutron().show_router(router_id)


def _get_neutron_port_info(
        api_clients,
        port_id):
    return api_clients.neutron().show_port(port_id)


def _get_neutron_floating_ip_info(
        api_clients,
        floating_ip_id):
    return api_clients.neutron().show_floatingip(floating_ip_id)


_RESOURCE_ATTRIBUTES_GETTERS = {
    'OS::Nova::Server': _get_nova_server_info,
    'OS::Neutron::Net': _get_neutron_net_info,
    'OS::Neutron::Subnet': _get_neutron_subnet_info,
    'OS::Neutron::Router': _get_neutron_router_info,
    'OS::Neutron::Port': _get_neutron_port_info,
    'OS::Neutron::FloatingIP': _get_neutron_floating_ip_info
}


_HEAT_RESOURCES = {
    'OS::Neutron::RouterGateway',
    'OS::Neutron::RouterInterface'
}


def get_single_resource_info(
        api_clients,
        resource,
        ignore_heat_resources,
        include_unsupported_resources):
    out_resource = {
        'resource_id': resource.physical_resource_id,
        'resource_type': resource.resource_type,
        'resource_name': resource.resource_name
    }
    #print ("{0}, {1}, {2}".format(resource.physical_resource_id ,resource.resource_type , resource.resource_name))
    if resource.resource_type in _RESOURCE_ATTRIBUTES_GETTERS:
        out_resource['resource_attributes'] = \
            _RESOURCE_ATTRIBUTES_GETTERS[resource.resource_type](
                api_clients,
                resource.physical_resource_id
            )
    elif ((not ignore_heat_resources
           and resource.resource_type in _HEAT_RESOURCES)
          or (include_unsupported_resources
              and resource.resource_type not in _HEAT_RESOURCES)):
        out_resource['resource_attributes'] = resource.to_dict()
    else:
        return None
    return out_resource


def get_all_stack_resource_info(
        api_clients,
        stack_id,
        ignore_heat_resources,
        include_unsupported_resources):
    resources = []
    for resource in api_clients.heat().resources.list(stack_id=stack_id):
        resource_info = get_single_resource_info(
            api_clients,
            resource,
            ignore_heat_resources,
            include_unsupported_resources
        )
        if resource_info is not None:
            resources.append(resource_info)
    return resources
