'''Ich benutze Pandas, um Excel sheets zu erzeugen,
hier werden die gefundenen Daten in passende DataFrames geschoben
'''
import pandas as pd

from .applenvs import applenvs_for_pandas
from .schedenvs import sched_for_pandas
from .reportclasses import repclasses_for_pandas
from .serviceclass import serviceclasses_for_pandas
from .workloads import workloads_for_pandas
from .groupnames import groupnames_for_pandas

def export_to_excel(wlm, path):
    '''Anreichern der Daten aus der Service Definition und exportieren
    in einzelne Sheets eines Excel-Files.
    '''
    # Übersicht der Workloads
    df_wl = pd.DataFrame(workloads_for_pandas(wlm))

    # Serviceclasses anreichern mit
    #       USED:        in eine Classification benutzt
    #       SC_OVERRIDE: in Policy überschrieben
    #       RG_OVERRIDE: Resource Group der SC in Policy überschrieben
    df_sc = pd.DataFrame(serviceclasses_for_pandas(wlm))

    # Resource Groups mit Overrides
    df_rg = rg_to_df(wlm.resgroups.values())
    dfs_rg = [
        rg_to_df(p.overrides_rg.values(), policy=p.name)
        for p in wlm.policies.values()
    ]
    dfs_rg.append(df_rg)
    df_rg_all_policies = (
        pd.concat(dfs_rg)
        .set_index('RESGROUP POLICY'.split())
        .unstack()
    )

    # Classification Groupnames
    # Zwei Tabelle: die erste nur mit den Gruppen, die zweite mit
    # Gruppen und ihren Kriterien.
    gn_1, gn_2 = groupnames_for_pandas(wlm)
    df_gn_1, df_gn_2 = pd.DataFrame(gn_1), pd.DataFrame(gn_2)

    df_applenvs = pd.DataFrame(
        applenvs_for_pandas(wlm.applenvs.values())
    )
    df_scheds = pd.DataFrame(
        sched_for_pandas(wlm.schedenvs.values())
    )
    df_repclasses = pd.DataFrame(
        repclasses_for_pandas(
            wlm.repclasses.values(),
            wlm.ssmtypes.values(),
        )
    )

    with pd.ExcelWriter(path) as writer:
        df_wl.to_excel(writer, sheet_name='Workloads')
        df_sc.to_excel(writer, sheet_name='Serviceclasses')

        df_rg_all_policies.to_excel(writer, sheet_name='Resource Groups')

        df_gn_1.to_excel(writer, sheet_name='Group Names')
        df_gn_2.to_excel(writer, sheet_name='Group Quals')

        df_applenvs.to_excel(writer, sheet_name='Appl Envs')
        df_scheds.to_excel(writer, sheet_name='Sched Envs')
        df_repclasses.to_excel(writer, sheet_name='Report Classes')

        for ssm in wlm.ssmtypes.values():
            df_ssm = ssm_to_df(ssm)
            df_ssm.to_excel(writer, sheet_name=ssm.name)


def rg_to_df(rgs, policy='BASE'):
    ''' Resource Groups als DataFrame
    '''
    rg_dict = {
        'POLICY': ((policy + ' ')* len(rgs)).split(),
        'RESGROUP': [rg.name for rg in rgs],
        'CAPACITY': ['{} [{}<{}]'.format(rg.type, rg.min, rg.max) for rg in rgs],
    }
    return pd.DataFrame(rg_dict)
def ssm_to_df(ssm):
    '''Je Subsystem ein Dataframe mit den Classifications
    '''
    clf_dict = {
        'STUFE': [wq.stufe for wq in ssm.workqualifiers],
        'TYPE':  [wq.qtype for wq in ssm.workqualifiers],
        'QNAME': ['%'*wq.startpos + wq.qname for wq in ssm.workqualifiers],
        'SERVCLS':    [wq.serviceclass for wq in ssm.workqualifiers],
        'REPTCLS':    [wq.reportclass for wq in ssm.workqualifiers],
        'DESCRIPTION':    [wq.description for wq in ssm.workqualifiers],
        'STORCRIT':    [wq.storcrit for wq in ssm.workqualifiers],
        'MANAGEDBY':    [wq.managedby for wq in ssm.workqualifiers],
    }
    return pd.DataFrame(clf_dict)
