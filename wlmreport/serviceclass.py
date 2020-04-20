''' class Serviceclass und parser dafür.
'''
from collections import defaultdict
import re
from .coroutine import coroutine

class Serviceclass:
    '''Eine Service Class
    - gehört zu einem Workload
    - optional eine Resource Group
    - hat mindestens eine Period (dict mit Key '1', '2' usw.)
    '''
    def __init__(self, name, description):

        self.name = name
        self.workloadname = None
        self.description = description
        self.resgroup = None
        self.cpucrit = None
        self.periods = {}
    def __repr__(self):
        first_importance = self.periods['1'].importance
        first_goal = self.periods['1'].goal
        return 'svc {:8s} I={} {:20s} {:8s} : {:s}'.format(
            self.name,
            first_importance,
            first_goal,
            self.resgroup if self.resgroup else '.'*8,
            self.description)
    def list_periods(self):
        ''' list mit den Periods (Nummer, Duration, Importance und Goal
        '''
        out = []
        for pnum, period in self.periods.items():
            out.append(
                '{:} {:8s} {} {}'.format(
                    pnum,
                    period.duration,
                    period.importance,
                    period.goal,
                )
            )
        return out

@coroutine
def process_serviceclass(
        sc_dict,
        start_zeile,
        workloadname=None,
        overrides_only=False
    ):
    '''
    Verdaue die Textzeilen, die eine Service Class beschreiben:

         * Service Class PRDBATLO - Production Batch Low
           Class assigned to resource group RG#IV00
           Base goal:
           CPU Critical   = NO        I/O Priority Group = NORMAL
           Honor Priority = DEFAULT

             #  Duration   Imp  Goal description
             -  ---------  -    ----------------------------------------
             1                  Discretionary
    '''

    name_description = start_zeile.split('Class ', maxsplit=1)[1]
    name, description = name_description.split(' - ', maxsplit=1)
    svc = Serviceclass(name, description)
    sc_dict[name] = svc
    svc.workloadname = workloadname
    # jetzt warte ich auf Folgezeilen
    while True:
        zeile = (yield)
        if zeile.startswith('Class assigned'):
            svc.resgroup = zeile.split('group ', maxsplit=1)[1]
        elif zeile.startswith('CPU Critical'):
            svc.cpucrit = zeile.split(' = ', maxsplit=1)[1]
            svc.cpucrit = svc.cpucrit.split(' ', maxsplit=1)[0]
        elif zeile.startswith('Honor'):
            pass
        elif zeile[0] in '1234':    # 1 bis 4 Perioden
            svc.periods[zeile[0]] = Period(zeile)
        elif zeile.startswith('Base goal'):
            if overrides_only:
                sc_dict.pop(name)
        else:
            pass
class Period:            # pylint: disable=too-few-public-methods
    '''Eine Period hat
        - eine Duration in SUs außer bei der letzten (oder einzigen Period)
        - eine Importance von 1 bis 6,
            6 steht für discretionary
        - ein Goal (Velocity oder Response Time)
    '''

    pattern = re.compile(r'\d\d:\d\d:\d\d.\d\d\d')
    def __init__(self, zeile):
        self.duration = zeile[3:12]
        try:
            self.importance = int(zeile[14])
        except ValueError:
            self.importance = 6 # Discretionary
        self.goal = zeile[19:].replace('Execution velocity of ', 'vel=')
        self.goal = self.goal.replace('complete within ', 'in ')
        self.goal = self.goal.replace('Average response time', 'Avg')
        match = Period.pattern.search(self.goal)
        if match:
            hour, minutes, ss_sss = self.goal[match.start():].split(':')
            secs, sss = ss_sss.split('.')
            goal_in_seconds = (
                (int(hour) * 60 + int(minutes)) * 60 + int(secs)
            ) + int(sss)/1000
            self.goal = self.goal[:match.start()] + '{:.3f}s'.format(
                goal_in_seconds)

    def __repr__(self):
        return 'Imp={} Dur={} {}'.format(
            self.importance,
            self.duration,
            self.goal,
            )


def serviceclasses_for_pandas(sdef):
    ''' Erstelle pandas geeignetes dict aus Liste von Serviceclass Objekten

    '''
    scs = sdef.serviceclasses.values()
    overrides_sc = set(
        svc
        for pol in sdef.policies.keys()
        for svc in sdef.policies[pol].overrides_sc
    )
    overrides_rg = set(
        rg
        for pol in sdef.policies.keys()
        for rg in sdef.policies[pol].overrides_rg
    )
    sc_to_ssm = defaultdict(list)
    for ssm in sdef.ssmtypes.values():
        sc_to_ssm[ssm.serviceclass].append(ssm.name)
        for rule in ssm.workqualifiers:
            sc_to_ssm[rule.serviceclass].append(ssm.name)
    sc_to_ssm = {key: ' '.join(set(value)) for key, value in sc_to_ssm.items()}
    sc_dict = {
        'WORKLOAD': [svc.workloadname for svc in scs],
        'SERVICECLASS': [svc.name for svc in scs],
        'PERIODS': [len(svc.periods) for svc in scs],
        '1IMP' : [svc.periods['1'].importance for svc in scs],
        '1GOAL': [svc.periods['1'].goal for svc in scs],
        'RESGROUP' : [svc.resgroup for svc in scs],
        'RG_OVERRIDE': [svc.resgroup in overrides_rg for svc in scs],
        'SC_OVERRIDE': [svc.name in overrides_sc for svc in scs],
        'USED_IN_SSM': [sc_to_ssm.get(svc.name, '') for svc in scs],
        'DESCRIPTION': [svc.description for svc in scs],
    }
    return sc_dict
