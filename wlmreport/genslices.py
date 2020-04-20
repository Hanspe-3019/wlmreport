''' gen_slices
'''
def gen_slices(zeile):
    '''Hilfsroutine, die aus einer Headerzeile eine Liste von Slices
    generiert.

    - ---------- -------------- ---------      -------- --------
    '''
    start = 0
    slices = []
    while True:
        next_start = zeile[start :].find(' -') + 1
        if next_start == 0:
            break
        stop = zeile[start :].find(' ')
        slices.append(slice(start, start + stop))
        start += next_start

    slices.append(slice(start, len(zeile)))
    return slices

def test_gen_slices():
    ''' Test für gen_slices
    '''
    ###### = '012345678901234567890123456789012345678901234567890123456789'
    header = '- ---------- -------------- ---------      -------- --------'
    testit = 'A_bBBBBBBBBb_cCCCCCCCCCCCCc_dDDDDDDDd______eEEEEEEe_fFFFFFFf'
    for col in gen_slices(header):
        print("{}\t!{}!".format(col, testit[col]))
