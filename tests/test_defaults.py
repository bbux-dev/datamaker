import dataspec


@dataspec.registry.defaults('dino')
def _get_default_dinosaur():
    return 'velociraptor'


def test_default_registry():
    assert dataspec.types.get_default('dino') == 'velociraptor'


def test_default_registry_set():
    dataspec.types.set_default('dino', 'triceratops')

    assert dataspec.types.get_default('dino') == 'triceratops'


def test_default_registry_get_all():
    defaults = dataspec.types.all_defaults()
    assert type(defaults) == dict
    assert len(defaults) > 0
