''' Class ApplEnvironment und coroutine zum parsen
'''
from .coroutine import coroutine
class ApplEnvironment:
    '''Application Environment
    '''
    def __init__(self, zeile):
        self.name = zeile.split(' . . ', maxsplit=1)[1]
        self.description = None
        self.ssmtype = None
        self.procname = None
        self.startparms = None
        self.parms = {}
        self.startrule = None
    def __repr__(self):
        return "ApplEnv {:20s} - {:}".format(
            self.name,
            self.description,
            )

@coroutine
def process_applenvs(dict_ae):
    '''
   01234567890123456789012345678901234567890123456789
   Appl Environment Name . . DBP2WIDT
   Description . . . . . . . WLM Stored Proc.f. DBP2 ID-geber
   Subsystem type  . . . . . DB2
   Procedure name  . . . . . DBP2WIDT
   Start parameters  . . . . DB2SSN=&IWMSSNM,NUMTCB=8,APPLENV=DBP2WID
                             T
   Starting of server address spaces for a subsystem instance:
    Limited to a single address space per system
     ==================================================================
    '''
    aenv = None
    while True:
        zeile = (yield)
        if zeile.startswith('Appl Environment Name '):
            aenv = ApplEnvironment(zeile)
            dict_ae[aenv.name] = aenv
            startparms, startrule = (False, False)
        elif aenv:
            if zeile.startswith('Description '):
                aenv.description = zeile[26:]
            elif zeile.startswith('Subsystem type'):
                aenv.ssmtype = zeile[26:]
            elif zeile.startswith('Procedure name '):
                aenv.procname = zeile[26:]
            elif zeile.startswith('Start parameters'):
                aenv.startparms = zeile[26:]
                startparms = True
            elif zeile.startswith('Starting of server'):
                startparms, startrule = (False, True)
            else:
                if zeile[0] in '=*':     # Ende des Appl Environments
                    try:
                        aenv.parms = {
                            k: v for k, v in [
                                parm.split('=')
                                for parm in aenv.startparms.split(',')
                            ]
                        }
                    except ValueError:
                        pass
                    aenv = None
                elif startparms:        # Fortsetzung Start Parameters
                    aenv.startparms += zeile
                elif startrule:         # Startrule in eigener Zeile
                    aenv.startrule = zeile
                else:
                    pass
        else:
            pass

def applenvs_for_pandas(aenvs):
    '''dict of list für Konstruktor DataFrame
    '''
    spalten = {
        'APPLENV': [aenv.name for aenv in aenvs],
        'DESC': [aenv.description for aenv in aenvs],
        'SUBSYS' :[aenv.ssmtype for aenv in aenvs],
        'PROCNAME': [aenv.procname for aenv in aenvs],
        'STARTRULE': [aenv.startrule for aenv in aenvs],
    }
    # jetzt noch alle Parameter in den Start Parms:

    start_parms = set().union(*[set(aenv.parms.keys()) for aenv in aenvs])
    for p_spalte in start_parms:
        spalten['_' + p_spalte] = [
            aenv.parms.get(p_spalte, '') for aenv in aenvs
        ]

    return spalten
