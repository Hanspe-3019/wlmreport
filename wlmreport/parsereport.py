'''Parser eines ISPF-Print einer Service Definition
'''
import collections


from .coroutine import coroutine
from .resgroups import process_resgroups
from .groupnames import process_classificationgroups
from .workloads import process_workloads
from .policies import process_policies
from .ssmtypes import process_ssms
from .reportclasses import process_repclasses
from .applenvs import process_applenvs
from .schedenvs import process_schedenvs

def gen_rec(path):
    ''' Einfacher Generator für die Eingabezeilen
    in der ersten Spalte stehen Vorschubsteuerzeichen, die wir ignorieren
    '''
    with open(path, 'rb') as in_file:
        for rec in in_file:
            strip_rec = rec[1:].decode('cp850').lstrip()
            if strip_rec:
                if strip_rec.startswith('+---'):
                    pass
                else:
                    yield strip_rec.rstrip()
@coroutine
def process_default(wlm):
    ''' Default Coroutine, extrahiert Namen der Service defintion
    und wirft ValueError gegebenenfalls.
    '''
    while True:
        zeile = (yield)
        if not wlm.service_definition:
            if zeile.startswith('* Service Definition '):
                wlm.service_definition = zeile.split('n ', maxsplit=1)[1]
            else:
                raise ValueError(
                    'Keine Service Definition\n' + zeile
                )

        #print(zeile)

def parse_reportfile(sdef, path):
    ''' Wir wird geparse't. Aufruf aus method
    '''
    recs = gen_rec(path)
    anz_je_abschnitt = collections.defaultdict(int)

    abschnitte = {
        '*Start*': process_default(sdef),
        '!Service Policies!': process_policies(sdef.policies),
        '!Classification Groups!': process_classificationgroups(sdef.clfgroups),
        '!Subsystem Types!': process_ssms(sdef.ssmtypes),
        '!Report Classes!': process_repclasses(sdef.repclasses),
        '!Application Environments!': process_applenvs(sdef.applenvs),
        '!Scheduling Environments!': process_schedenvs(sdef.schedenvs),
        '!Workloads!': process_workloads(sdef.workloads),
        '!Resource Groups!': process_resgroups(sdef.resgroups),
    }

    aktueller_abschnitt = '*Start*'
    proc = process_default(sdef)
    for rec in recs:
        if rec[0] == '!':
            aktueller_abschnitt = rec
            try:
                proc = abschnitte[aktueller_abschnitt]
            except KeyError:
                proc = None
        anz_je_abschnitt[aktueller_abschnitt] += 1
        if proc:
            proc.send(rec)
# Ende #
