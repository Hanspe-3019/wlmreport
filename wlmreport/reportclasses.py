''' class Reportclass und Parser
'''
from collections import defaultdict
from .coroutine import coroutine

class Reportclass:          # pylint: disable=too-few-public-methods
    '''Ist nur ein Name mit einer Beschreibung
    '''
    def __init__(self, zeile):
        name_desc = zeile.split(' Class ', maxsplit=1)[1]
        self.name, self.description = name_desc.split(' -', maxsplit=1)
    def __repr__(self):
        return "Report Class {:8s} - {:}".format(
            self.name,
            self.description,
            )

@coroutine
def process_repclasses(dict_rc):
    '''
     * Report Class ASCH - APPC/MVS Users
    '''
    while True:
        zeile = (yield)
        if zeile.startswith('* Report Class '):
            repclass = Reportclass(zeile)
            dict_rc[repclass.name] = repclass
        else:
            pass
def repclasses_for_pandas(repclasses, ssmtypes):
    '''Zusätzliche Spalten für XREF zu Classifications
    '''
    pd_dict = {
        'REPORTCLASS': [rp.name for rp in repclasses],
        'DESC': [rp.description for rp in repclasses],
    }
    #   Ermittle alle Bezüge auf Report Classes in den Classifications der SSM
    rp_to_ssm = defaultdict(list)
    for ssm in ssmtypes:
        rp_to_ssm[ssm.reportclass].append(ssm.name)
        for rule in ssm.workqualifiers:
            rp_to_ssm[rule.reportclass].append(ssm.name)

    rp_to_ssm = {key: ' '.join(set(value)) for key, value in rp_to_ssm.items()}

    pd_dict['USED_IN'] = [rp_to_ssm.get(rp.name, '') for rp in repclasses]

    return pd_dict
