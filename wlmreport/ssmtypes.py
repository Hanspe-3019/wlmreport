''' Subsystem Types und Coroutine für Parsen
'''
from .coroutine import coroutine
from .genslices import gen_slices
class Subsystem:        # pylint: disable=too-few-public-methods
    ''' WLM Classifications erfolgen je WLM-Subsystem, also TSO, JES, CICS…
    Jedes Subsystem hat dann eine Liste von sog. Work Qualifiers.
    '''
    def __init__(self, start_zeile):
        name_desc = start_zeile.split(' Type ', maxsplit=1)[1]
        self.name, self.description = name_desc.split(' - ', maxsplit=1)
        self.serviceclass = None    # Default Service Class
        self.reportclass = None     # Default Report Class
        self.workqualifiers = []
    def __repr__(self):
        return 'Subsystem {:} {:}'.format(
            self.name,
            self.description
            )
class Workqualifier:     # pylint: disable=too-few-public-methods
    ''' Ein Workqualifier kann hierarchisch unter seinem Vorgänger stehen
    oder ist ein Bruder seiner Vorgängers auf der selben Hierarchiestufe.

    Qualifier Type ist z.B. UI für Userid oder TN für Transaktionsname
    Qualifier Name ist der Qualifier und kann auch generisch angegeben werden.
    '''
    def __init__(self, parent=None):
        self.parent = parent
        self.childs = []

        self.stufe = -1
        self.qtype = None
        self.qname = None
        self.startpos = 0
        self.serviceclass = None
        self.reportclass = None

        self.description = None
        self.storcrit = None
        self.managedby = None

@coroutine
def process_ssms(dict_ssm):
    '''

     * Subsystem Type CICS - CICS Workload
       Classification:
        …
       Descriptions:
        …
       Attributes:
        …
       =======================
    '''
    proc = None
    subsystem = None
    while True:
        zeile = (yield)
        if zeile.startswith('* Subsystem Type '):
            subsystem = Subsystem(zeile)
            dict_ssm[subsystem.name] = subsystem
        elif zeile.startswith('Classification:'):
            proc = process_classification(subsystem)
        elif zeile.startswith('Descriptions:'):
            proc = process_description(subsystem)
        elif zeile.startswith('Attributes:'):
            proc = process_attributes(subsystem)
        else:
            if proc:
                proc.send(zeile)

@coroutine
def process_classification(ssm):
    '''
       Classification:

         Default service class is CIHNP#DF
         There is no default report class.

           Qualifier  Qualifier      Starting       Service  Report
         # type       name           position       Class    Class
         - ---------- -------------- ---------      -------- --------
         1 SI         CICPRD0                       CIHNP#BA BODDEN
         2 . TNG      . IVAS_AU                     CIHNP#LO TPIVASAU
         2 . TN       . kNV1                        CIHNP#BA TPIVASK
         1 SI         CICOLT*                       CIHNT#DF CICIVVEO

    '''
    cols = []
    while True:
        zeile = (yield)
        if zeile.startswith('Default service class is '):
            wq_default = Workqualifier()
            ssm.workqualifiers.append(wq_default)
            ssm.serviceclass = zeile.split(' is ', maxsplit=1)[1]
            wq_default.stufe = 0
            wq_default.qtype = '**'
            wq_default.qname = 'default'
            wq_default.startpos = 0
            wq_default.serviceclass = ssm.serviceclass
        elif zeile.startswith('Default report class is '):
            ssm.reportclass = zeile.split(' is ', maxsplit=1)[1]
            wq_default.reportclass = ssm.reportclass
        elif zeile[0] == '-':
            cols = gen_slices(zeile)
        elif zeile[0] in '12345':
            wqual = Workqualifier()
            wqual.stufe = int(zeile[cols[0]])
            # ersetze die '. ' vor dem Typ und dem Namen
            wqual.qtype = zeile[cols[1]].replace('.', '').strip()
            wqual.qname = zeile[cols[2]].replace('.', '').strip()
            wqual.startpos = zeile[cols[3]].strip()
            if wqual.startpos:
                wqual.startpos = int(wqual.startpos)
            else:
                wqual.startpos = 0
            wqual.serviceclass = zeile[cols[4]].strip()
            wqual.reportclass = zeile[cols[5]].strip()
            ssm.workqualifiers.append(wqual)
        else:
            pass
@coroutine
def process_description(ssm):
    ''' Desription hinzufügen
           Qualifier  Qualifier      Description
         # type       name
         - ---------- -------------- --------------------------------
         1 SI         CICPRD0        CICS Prod Hannover
         2 . TNG      . IVAS_AU
    '''
    qpos = 0
    cols = []
    while True:
        zeile = (yield)
        if zeile[0] in '1234':
            wqual = ssm.workqualifiers[qpos]
            wqual.description = zeile[cols[3]].strip()
            qpos = qpos + 1
        elif zeile[0] == '-':
            cols = gen_slices(zeile)
        else:
            pass
@coroutine
def process_attributes(ssm):
    '''
       Attributes:

           Qualifier  Qualifier      Storage   Reporting  Manage Region
         # type       name           Critical  Attribute  Using Goals Of
         - ---------- -------------- --------- ---------- --------------
         1 SI         CICPRD0        NO        NONE       N/A
         2 . TNG      . IVAS_AU      NO        NONE       N/A
         2 . TN       . kNV1         NO        NONE       N/A
         1 SI         CICOLT*        NO        NONE       N/A
    '''
    qpos = 0
    cols = []
    while True:
        zeile = (yield)
        if zeile[0] in '1234':
            wqual = ssm.workqualifiers[qpos]
            wqual.storcrit = zeile[cols[3]][0]    # N/Y
            wqual.managedby = zeile[cols[5]]
            qpos = qpos + 1
        elif zeile[0] == '-':
            cols = gen_slices(zeile)
        else:
            pass
