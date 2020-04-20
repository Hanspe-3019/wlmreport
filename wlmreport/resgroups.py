''' Resource Group und coroutine zum Parsen
'''
from .coroutine import coroutine
class Resgroup:
    ''' Resource Group
    '''
    def __init__(self, start_zeile):
        name_description = start_zeile.split(' Group ', maxsplit=1)[1]
        self.name, self.description = name_description.split(
            ' - ',
            maxsplit=1,
        )
        self.type = None
        self.capacity = None
        self.min = None
        self.max = None
    def __repr__(self):
        return 'RG {:8s} : {:s} {:16s} - {:s}'.format(
            self.name,
            self.type,
            '[{}<{}]'.format(self.min, self.max),
            self.description,
            )

@coroutine
def process_resgroups(resgroups, overrides_only=False):
    '''
    resgroups ist ein Dictionary für die gefunden Resgroupobjekte
    Der Flage overrides_only steuert, ob nur overrides
    geliefert werden sollen.

     * Resource Group KILLIT - Logical Swapout for Non-Swap
       Base attributes:
         Capacity is in Service Units with Sysplex Scope.
         Minimum capacity is not specified.
         Maximum capacity is 1.
         Memory limit is not specified.
    '''
    resgroup = None
    while True:
        zeile = (yield)
        if zeile.startswith('* Resource Group '):
            resgroup = Resgroup(zeile)
            resgroups[resgroup.name] = resgroup
        elif zeile.startswith('Capacity'):
            resgroup.capacity = zeile[:-1]
            if zeile.find('Number of CPs') > 0:
                resgroup.type = 'CPs'
            elif zeile.find('LPAR share') > 0:
                resgroup.type = 'SHR'
            elif zeile.find('Service Units') > 0:
                resgroup.type = 'SUs'
            else:
                resgroup.type = '?'
        elif zeile.startswith('Minimum'):
            resgroup.min = zeile[:-1].split('capacity is ', maxsplit=1)[1]
            if resgroup.min.startswith('not '):
                resgroup.min = ''
        elif zeile.startswith('Maximum'):
            resgroup.max = zeile[:-1].split('capacity is ', maxsplit=1)[1]
            if resgroup.max.startswith('not '):
                resgroup.max = ''
        elif zeile.startswith('Base attributes:'):
            if overrides_only:
                resgroups.pop(resgroup.name)
        else:
            pass
