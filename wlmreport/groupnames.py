''' Class Groupname und Parser
'''
from .coroutine import coroutine

class Groupname:         # pylint: disable=too-few-public-methods
    '''Beschreibt eine Classification Group. Je nach Typ und
    Verwendung in den Klassifizierungen eines Subsystem sind
    das Gruppen von
    Jobnamen, Userids, Transactionscodes, Jobklassen usw.
    '''
    def __init__(self, start_zeile):
        '''Logik der Interpretation der Startzeile ist hier drin.
        '''
        name_description = start_zeile.split(' Group ', maxsplit=1)[1]
        self.name, self.description = name_description.split(' -', maxsplit=1)
        self.qualifier = []
        self.qualidesc = []
        if start_zeile.startswith('* Subsystem Instance Group '):
            self.type = 'SIG'
        elif start_zeile.startswith('* Transaction Name Group '):
            self.type = 'TNG'
        elif start_zeile.startswith('* Userid Group '):
            self.type = 'UIG'
        elif start_zeile.startswith('* Transaction Class Group '):
            self.type = 'TCG'
        else:
            self.type = start_zeile
    def __repr__(self):
        return 'gn {:s} {:s}'.format(self.type, self.name)

@coroutine
def process_classificationgroups(classificationgroups):
    '''
     Coroutine lässt sich Zeilen reingeben, erzeugt Objekte von
     Classification Groups und stellt diese in das übergebene Dictionary.

    Beispieldaten:

     * Subsystem Instance Group DB2E - Subsys DB2E und DB2F
         Qualifier  Starting
         name       position  Description
         ---------  --------  --------------------------------
         DB2E                 Test DB2 HN
         DB2F                 Test DB2 HN - 2. Member
       ================================================================
    '''
    clg = None
    while True:
        zeile = (yield)
        while True:
            zeile = (yield)
            if zeile.startswith('* '):
                clg = Groupname(zeile)
                classificationgroups[clg.name] = clg
            elif zeile.startswith('Qualifier'):
                pass
            elif zeile.startswith('name '):
                pass
            elif zeile.startswith('===='):
                pass
            elif zeile.startswith('******'):
                pass
            elif zeile.startswith('------'):
                pass
            elif clg:
                qual, pos, desc = zeile[0:8], zeile[11:19], zeile[21:]
                pos = pos.strip()
                pos = int(pos) if pos else 0
                clg.qualifier.append('%'*pos + qual)
                clg.qualidesc.append(desc.strip())
def groupnames_for_pandas(servdef):
    ''' Dict für generierung eine DataFrames
    '''
    gns = servdef.clfgroups.values()
    gns_used = {
        (rule.qtype, rule.qname)
        for ssm in servdef.ssmtypes.values()
        for rule in ssm.workqualifiers if rule.qtype.endswith('G')
    }
    pd_dict1 = {
        'TYPE': [gn.type for gn in gns],
        'GROUP': [gn.name for gn in gns],
        'DESC': [gn.description for gn in gns],
        'USED': [(gn.type, gn.name) in gns_used for gn in gns],
    }
    pd_dict2 = {
        'TYPE': [gn.type for gn in gns for qual in gn.qualifier],
        'GROUP': [gn.name for gn in gns for qual in gn.qualifier],
        'QUAL': [qual for gn in gns for qual in gn.qualifier],
        'DESC': [desc for gn in gns for desc in gn.qualidesc],
    }
    return (pd_dict1, pd_dict2)
