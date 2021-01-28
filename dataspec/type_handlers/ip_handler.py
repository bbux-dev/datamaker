import json
import random
import ipaddress
import dataspec
from dataspec import suppliers
from dataspec import SpecException


class IpV4Supplier:
    def __init__(self, octet_supplier_map):
        self.octet_supplier_map = octet_supplier_map

    def next(self, iteration):
        first = self.octet_supplier_map['first'].next(iteration)
        second = self.octet_supplier_map['second'].next(iteration)
        third = self.octet_supplier_map['third'].next(iteration)
        fourth = self.octet_supplier_map['fourth'].next(iteration)
        return f'{first}.{second}.{third}.{fourth}'


@dataspec.registry.types('ipv4')
def configure_ipv4(field_spec, _):
    return configure_ip(field_spec, _)


@dataspec.registry.types('ip')
def configure_ip(field_spec, _):
    config = field_spec.get('config', {})
    if 'base' in config and 'cidr' in config:
        raise SpecException('Must supply only one of base or cidr param: ' + json.dumps(field_spec))

    parts = _get_base_parts(config)
    # this is the same thing as a constant
    if len(parts) == 4:
        return suppliers.values('.'.join(parts))
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
                raise SpecException('Invalid Mask in cidr for config: ' + json.dumps(config))
            if int(mask) not in [8, 16, 24]:
                raise SpecException('Invalid Subnet Mask in cidr for config: ' + json.dumps(config)
                                    + ' only one of /8 /16 or /24 supported')
            ip_parts = cidr[0:cidr.index('/')].split('.')
            if len(ip_parts) < 4 or not all(part.isdigit() for part in ip_parts):
                raise SpecException('Invalid IP in cidr for config: ' + json.dumps(config))
            if mask == '8':
                parts = ip_parts[0:1]
            if mask == '16':
                parts = ip_parts[0:2]
            if mask == '24':
                parts = ip_parts[0:3]
        else:
            raise SpecException('Invalid Subnet Mask in cidr for config: ' + json.dumps(config)
                                + ' only one of /8 /16 or /24 supported')
    return parts


def _create_octet_supplier(parts, index, sample):
    if len(parts) >= index + 1 and parts[index].strip() != '':
        octet = parts[index].strip()
        if not octet.isdigit():
            raise SpecException(f'Octet: {octet} invalid for base' + '.'.join(parts))
        return suppliers.values(octet)
    else:
        octet_range = list(range(0, 255))
        spec = {'config': {'sample': sample}, 'data': octet_range}
        return suppliers.values(spec)


class IpV4PreciseSupplier:
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
    config = field_spec.get('config')
    if config is None:
        raise SpecException('No config for: ' + json.dumps(field_spec) + ', param cidr required')
    cidr = config.get('cidr')
    sample = config.get('sample', 'no').lower() in ['yes', 'true', 'on']
    if cidr is None:
        raise SpecException('Invalid config for: ' + json.dumps(field_spec) + ', param cidr required')
    return IpV4PreciseSupplier(cidr, sample)
