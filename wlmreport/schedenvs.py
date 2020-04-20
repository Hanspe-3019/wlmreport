''' Class Scheduling Environment und corroutine fürs Parsen
'''
from .coroutine import coroutine
from .genslices import gen_slices

class SchedulingEnvironment:     # pylint: disable=too-few-public-methods
    ''' Scheduling Environment mit Resources
    '''
    def __init__(self, name):
        self.name = name
        self.description = None
        self.resources = []

    def __repr__(self):
        return "SCHED {:8s} - {:}".format(
            self.name,
            self.description,
            )

@coroutine
def process_schedenvs(dict_se):
    '''
   01234567890123456789012345678901234567890123456789

   Die Environments werden durch =-Zeilen voneinander getrennt.
   Ende der Liste ist eine *-Zeile

   Scheduling Environment Name. . AS
   Description. . . . . . . . . . AS     laeuft hier (wg. Lizenz)

    Resource Name     State  Resource Description
    -------------     -----  --------------------
    AS                ON
     ==================================================================
     …
     ********
    '''
    senvs = None
    cols = []
    while True:
        zeile = (yield)
        if zeile.startswith('Scheduling Environment Name'):
            senvs = SchedulingEnvironment(zeile[31:].strip())
            dict_se[senvs.name] = senvs
        elif zeile.startswith('Description'):
            senvs.description = zeile[31:]
        elif zeile.startswith('Resource Name'):
            pass
        elif zeile.startswith('--'):
            cols = gen_slices(zeile)
            eins, zwei, drei = cols
        elif zeile[0] in '=*':
            pass
        else:
            if cols:
                senvs.resources.append(
                    Resource(zeile[eins], zeile[zwei], zeile[drei])
                )
class Resource:              # pylint: disable=too-few-public-methods
    '''Resource Object: Name, state, Description
    '''
    def __init__(self, name, state, description):
        self.name = name.strip()
        self.state = state.strip()
        self.description = description.strip()
    def __repr__(self):
        return 'RES {:} : {:} - {:}'.format(
            self.name,
            self.state,
            self.description,
            )
def sched_for_pandas(scheds):
    ''' dict of lists für DataFrame Konstruktor
    '''
    def res_to_str(res):
        return ' '.join(
        ('+' if resource.state == 'ON' else '-') + resource.name
            for resource in res)

    return {
        'SCHEDENV': [sched.name for sched in scheds],
        'DESC': [sched.description for sched in scheds],
        'RESOURCES': [res_to_str(sched.resources) for sched in scheds],
    }
