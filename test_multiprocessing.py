# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:26:46 2016

@author: Victor Barres

Test running models on mutliprocessing.
"""

from joblib import Parallel, delayed

from test_TCG_production import run_model


def multi_proc(num_tests=1, n_jobs=-1, verbose=1):
    """
    For use of Parallel, the functions needs to be defined outside of __main__
    
    Args:
        num_tests (INT)
        n_jobs (INT) : -1 to set to the number of cores.
        verbose (INT) : higher ints increase verbosity
    """
    
    # Mapping data 
    res = Parallel(n_jobs=n_jobs, verbose=verbose)(delayed(run_model)() for i in range(num_tests))
    
    return res


if __name__=='__main__':
    import sys
    import pprint as pp
    if len(sys.argv) == 0:
        print "Missing arguments!"
        print "run: python test_multiprocessing.py num_tests(INT) num_jobs(INT) verbose(INT)"
    
    num_tests = int(sys.argv[1])
    n_jobs = int(sys.argv[2])
    verbose = int(sys.argv[3])
    print "num_tests=%i; n_jobs=%i; verbose=%i" %(num_tests, n_jobs, verbose)
    res = multi_proc(num_tests, n_jobs, verbose)
    
    pp.pprint(res)