"""
Module for handling ip types
"""
import ipaddress
import json
import random

import dataspec

IP_KEY = 'ip'
IPV4_KEY = 'ipv4'


class IpV4Supplier(dataspec.ValueSupplierInterface):
    """
    Default implementation for generating ip values, uses separate suppliers for each octet of the ip
    """

    def __init__(self, octet_supplier_map):
        self.first = octet_supplier_map['first']
        self.second = octet_supplier_map['second']
        self.third = octet_supplier_map['third']
        self.fourth = octet_supplier_map['fourth']

    def next(self, iteration):
        first = self.first.next(iteration)
        second = self.second.next(iteration)
        third = self.third.next(iteration)
        fourth = self.fourth.next(iteration)
        return f'{first}.{second}.{third}.{fourth}'


@dataspec.registry.schemas(IP_KEY)
def get_ip_schema():
    return dataspec.schemas.load(IP_KEY)


@dataspec.registry.schemas(IPV4_KEY)
def get_ipv4_schema():
    # shares schema with ip
    return dataspec.schemas.load(IP_KEY)


@dataspec.registry.types(IPV4_KEY)
def configure_ipv4(field_spec, _):
    """ configures value supplier for ipv4 type """
    return configure_ip(field_spec, _)


@dataspec.registry.types(IP_KEY)
def configure_ip(field_spec, loader):
    """ configures value supplier for ip type """
    config = dataspec.utils.load_config(field_spec, loader)
    if 'base' in config and 'cidr' in config:
        raise dataspec.SpecException('Must supply only one of base or cidr param: ' + json.dumps(field_spec))

    parts = _get_base_parts(config)
    # this is the same thing as a constant
    if len(parts) == 4:
        return dataspec.suppliers.values('.'.join(parts))
    sample = config.get('sample', 'yes')
    octet_supplier_map = {
        'first': _create_octet_supplier(parts, 0, sample),
        'second': _create_octet_supplier(parts, 1, sample),
        'third': _create_octet_supplier(parts, 2, sample),
        'fourth': _create_octet_supplier(parts, 3, sample),
    }
    return IpV4Supplier(octet_supplier_map)


def _get_base_parts(config):
    """
    Builds the base ip array for the first N octets based on
    supplied base or on the /N subnet mask in the cidr
    """
    if 'base' in config:
        parts = config.get('base').split('.')
    else:
        parts = []

    if 'cidr' in config:
        cidr = config['cidr']
        if '/' in cidr:
            mask = cidr[cidr.index('/') + 1:]
            if not mask.isdigit():
                raise dataspec.SpecException('Invalid Mask in cidr for config: ' + json.dumps(config))
            if int(mask) not in [8, 16, 24]:
                raise dataspec.SpecException('Invalid Subnet Mask in cidr for config: ' + json.dumps(config)
                                    + ' only one of /8 /16 or /24 supported')
            ip_parts = cidr[0:cidr.index('/')].split('.')
            if len(ip_parts) < 4 or not all(part.isdigit() for part in ip_parts):
                raise dataspec.SpecException('Invalid IP in cidr for config: ' + json.dumps(config))
            if mask == '8':
                parts = ip_parts[0:1]
            if mask == '16':
                parts = ip_parts[0:2]
            if mask == '24':
                parts = ip_parts[0:3]
        else:
            raise dataspec.SpecException('Invalid Subnet Mask in cidr for config: ' + json.dumps(config)
                                + ' only one of /8 /16 or /24 supported')
    return parts


def _create_octet_supplier(parts, index, sample):
    """ creates a value supplier for the index'th octet """
    # this index is for a part that is static, create a single value supplier for that part
    if len(parts) >= index + 1 and parts[index].strip() != '':
        octet = parts[index].strip()
        if not octet.isdigit():
            raise dataspec.SpecException(f'Octet: {octet} invalid for base, Invalid Input: ' + '.'.join(parts))
        if not 0 <= int(octet) <= 255:
            raise dataspec.SpecException(f'Each octet: {octet} must be in range of 0 to 255, Invalid Input: ' + '.'.join(parts))
        return dataspec.suppliers.values(octet)
    # need octet range at this point
    octet_range = list(range(0, 255))
    spec = {'config': {'sample': sample}, 'data': octet_range}
    return dataspec.suppliers.values(spec)


class IpV4PreciseSupplier(dataspec.ValueSupplierInterface):
    """
    Class that supports precise ip address generation by specifying cidr values, much slower for large ip ranges
    """

    def __init__(self, cidr, sample):
        self.net = ipaddress.ip_network(cidr)
        self.sample = sample
        cnt = 0
        for _ in self.net:
            cnt += 1
        self.size = cnt

    def next(self, iteration):
        if self.sample:
            idx = random.randint(0, self.size - 1)
        else:
            idx = iteration % self.size
        return str(self.net[idx])


@dataspec.registry.types('ip.precise')
def configure_precise_ip(field_spec, _):
    """ configures value supplier for ip.precise type """
    config = field_spec.get('config')
    if config is None:
        raise dataspec.SpecException('No config for: ' + json.dumps(field_spec) + ', param cidr required')
    cidr = config.get('cidr')
    sample = config.get('sample', 'no').lower() in ['yes', 'true', 'on']
    if cidr is None:
        raise dataspec.SpecException('Invalid config for: ' + json.dumps(field_spec) + ', param cidr required')
    return IpV4PreciseSupplier(cidr, sample)
