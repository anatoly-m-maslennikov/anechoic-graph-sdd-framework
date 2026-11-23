"""Executable review model for project-wide lenses and Component whitelists."""

from itertools import combinations


class LensModel:
    def __init__(self):
        self.children = {}

    def declare(self, name, children=()):
        if name in self.children:
            raise ValueError(f"Lens already declared: {name}")
        missing = set(children) - self.children.keys()
        if missing:
            raise ValueError(f"Unknown lenses: {sorted(missing)}")
        self.children[name] = frozenset(children)

    def details(self, name):
        children = self.children[name]
        return frozenset().union(*(self.details(child) for child in children)) if children else frozenset({name})

    def narrower(self, child, parent):
        return (parent == 'SPEC' and child != 'SPEC' and child in self.children) or child in self.children[parent] or any(
            self.narrower(child, branch) for branch in self.children[parent]
        )

    def effective(self, declarations):
        """Return the nearest declaration; input is ordered from Component to root."""
        return next((frozenset(value) for value in declarations if value is not None), frozenset())

    def validate(self, enabled):
        enabled = set(enabled)
        unknown = enabled - self.children.keys()
        if unknown:
            raise ValueError(f"Unknown lenses: {sorted(unknown)}")
        sibling_groups = list(self.children.values())
        if 'SPEC' in self.children:
            sibling_groups.append(self.children.keys() - {'SPEC'})
        for siblings in sibling_groups:
            for left, right in combinations(siblings & enabled, 2):
                if self.narrower(left, right) or self.narrower(right, left):
                    continue
                overlap = self.details(left) & self.details(right)
                if overlap:
                    raise ValueError(f"Sibling lenses {left} and {right} overlap: {sorted(overlap)}")
        return frozenset(enabled)


def run_cases():
    model = LensModel()
    for name in ('IO', 'DOM', 'SWA', 'SWS', 'QA', 'DevOps'):
        model.declare(name)
    model.declare('SWD', ('SWA', 'SWS'))
    model.declare('SWE', ('SWD', 'QA', 'DevOps'))
    model.declare('DES', ('IO', 'DOM'))
    model.declare('SYS', ('SWE', 'DOM'))
    model.declare('SPEC', ('DES', 'SYS', 'SWE'))

    assert model.effective([None, None]) == frozenset()
    assert model.effective([None, ['SPEC', 'DES']]) == {'SPEC', 'DES'}
    assert model.effective([['SWE'], ['SPEC', 'DES']]) == {'SWE'}
    assert model.effective([[], ['SPEC']]) == frozenset()
    assert model.validate(['SPEC', 'DES', 'SWE']) == {'SPEC', 'DES', 'SWE'}
    assert model.validate(['SYS', 'SWE']) == {'SYS', 'SWE'}
    assert model.validate(['SWE', 'SWD', 'QA']) == {'SWE', 'SWD', 'QA'}
    assert 'DevOps' not in model.validate(['SWE', 'SWD', 'QA'])
    try:
        model.validate(['DES', 'SYS'])
    except ValueError as error:
        assert 'DOM' in str(error)
    else:
        raise AssertionError('DES and SYS must be rejected')
    try:
        model.declare('DES', ('IO',))
    except ValueError:
        pass
    else:
        raise AssertionError('A global lens name cannot be redeclared')
    model.declare('NEW')
    model.declare('OVERLAP', ('DOM',))
    assert model.narrower('NEW', 'SPEC')
    assert model.validate(['SPEC', 'NEW']) == {'SPEC', 'NEW'}
    assert model.effective([None, []]) == frozenset()
    try:
        model.validate(['DES', 'OVERLAP'])
    except ValueError as error:
        assert 'DOM' in str(error)
    else:
        raise AssertionError('New sibling overlapping DOM must be rejected')
    assert model.details('DES') == {'IO', 'DOM'}
    print('Lens review cases passed')


if __name__ == '__main__':
    run_cases()
