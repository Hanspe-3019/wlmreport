''' Class Workload und coroutine zum Parsen
'''
from collections import defaultdict
from .coroutine import coroutine
from .serviceclass import process_serviceclass

class Workload:
    ''' Ein Workload ist eine Zusammenfassung von Service Classes für
    Reporting-Zwecke
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.serviceclasses = {}
    def __repr__(self):
        return 'Workload {:s} - {:s}'.format(self.name, self.description)

@coroutine
def process_workloads(workloads):
    '''
     * Workload STC - Started Tasks
       10 service classes are defined in this workload.
         * Service Class CICPRD0 - STC-goals fuer Prod0
    '''
    workload = None
    proc = None
    while True:
        zeile = (yield)
        if zeile.startswith('* Workload '):
            proc = None
            name, description = zeile[11:].split(' - ', maxsplit=1)
            workload = Workload(name, description)
            workloads[name] = workload
        elif zeile.startswith('* Service Class '):
            proc = process_serviceclass(
                workload.serviceclasses,
                zeile,
                workload.name,
            )
        else:
            if proc:
                proc.send(zeile)
def workloads_for_pandas(sdef):
    '''Erzeuge dictionary of lists für DataFrame Constructor
    '''
    workloads = sdef.workloads.values()
    sc_to_ssm = defaultdict(list)
    for ssm in sdef.ssmtypes.values():
        sc_to_ssm[ssm.serviceclass].append(ssm.name)
        for rule in ssm.workqualifiers:
            sc_to_ssm[rule.serviceclass].append(ssm.name)
    sc_to_ssm = {key: ' '.join(set(value)) for key, value in sc_to_ssm.items()}
    def used_sc(wload):
        '''
        '''
        return sum(sc.name in sc_to_ssm for sc in wload.serviceclasses.values())
    def used_ssm(wload):
        '''
        '''
        return ' '.join(set(
            sc_to_ssm.get(sc.name, '') for sc in wload.serviceclasses.values()
        ))
    return {
        'WORKLOAD': [wload.name for wload in workloads],
        'DEF_CLASSES': [len(wload.serviceclasses) for wload in workloads],
        'USED_CLASSES': [used_sc(wload) for wload in workloads],
        'SSMs': [used_ssm(wload) for wload in workloads],
        }
