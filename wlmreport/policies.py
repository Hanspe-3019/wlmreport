''' Policy Class und coroutine für parse
'''
from .coroutine import coroutine
from .serviceclass import process_serviceclass
from .resgroups import process_resgroups

class Policy:
    '''Die Policy überschreibt einige Service Classes und Resource Groups
    In der Eingabedatei sind alle SCs (unter deren Workload) und RGs
    enthalten, auch die, die nicht überschrieben werden.
    Wir halten in dem Policy Objekt nur die Overrides.
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.overrides_sc = {}
        self.overrides_rg = {}
    def __repr__(self):
        return 'Policy {:s} - {:s}'.format(self.name, self.description)

@coroutine
def process_policies(policies):
    '''
     * Service Policy NACHTS - Policy der ivv fuer Batch Abends
       * Workload BATCH - Production Batch
         19 service classes are defined in this workload.
           * Service Class BATNO#RG - Batch normal ohne Resource Group
    '''
    policy = None
    proc = None
    while True:
        zeile = (yield)
        if zeile.startswith('* Service Policy '):
            name_description = zeile.split('Policy ', maxsplit=1)[1]
            name, description = name_description.split(' - ', maxsplit=1)
            policy = Policy(name, description)
            policies[name] = policy
        elif zeile.startswith('* Resource Group '):
            proc = process_resgroups(
                policy.overrides_rg,
                overrides_only=True,
            )
            proc.send(zeile)
        elif zeile.startswith('* Service Class '):
            proc = process_serviceclass(
                policy.overrides_sc,
                zeile,
                overrides_only=True,
            )
        else:
            if proc:
                proc.send(zeile)
