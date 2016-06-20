# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:26:46 2016

@author: victor
"""

from joblib import Parallel, delayed

from test_TCG_production import test


def multi_proc(num_tests=1, n_jobs=-1, verbose=1):
    """
    For use of Parallel, the functions needs to be defined outside of __main__
    
    Args:
        num_tests (INT)
        n_jobs (INT) : -1 to set to the number of cores.
        verbose (INT) : higher ints increase verbosity
    """
    
    # Mapping data 
    Parallel(n_jobs=n_jobs, verbose=verbose)(delayed(test)() for i in range(num_tests))


if __name__=='__main__':
    import sys
    num_tests = int(sys.argv[1])
    n_jobs = int(sys.argv[2])
    verbose = int(sys.argv[3])
    print "num_tests=%i; n_jobs=%i; verbose=%i" %(num_tests, n_jobs, verbose)
    multi_proc(num_tests, n_jobs, verbose)
    
