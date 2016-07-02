# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 14:34:02 2016

@author: victor

Preliminary test for simulation analyses!
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def active_passive(file_path="./sim.csv", output_path='./tmp/'):
    """
    """
    import os
    
    if not(os.path.exists(output_path)):
        os.mkdir(output_path)

    # Load .csv data into a pandas dataframe
    my_dataframe = pd.read_csv(file_path)
    #print list(my_dataframe.columns.values)
    
    my_dataframe['saliency_diff'] = my_dataframe.x1 - my_dataframe.x2
    my_dataframe['act-pas'] = my_dataframe.active - my_dataframe.passive
    
    #my_dataframe.plot(kind='scatter', x='x1', y='active', color='red', label='active')
    #my_dataframe.plot(kind='scatter', x='x2', y='passive', color='blue', label='passive')
    #my_dataframe.plot(kind='scatter', x='saliency_diff', y='active', color='red', label='active')
    #my_dataframe.plot(kind='scatter', x='saliency_diff', y='passive', color='blue', label='passive')
    #
    #my_dataframe.plot(kind='scatter', x='saliency_diff', y='act-pas')
    
    sub_set = my_dataframe[['saliency_diff', 'active', 'passive']]
    summary_data = {}
    for vals in sub_set.values:
            val = int(10*vals[0])
            if not summary_data.has_key(val):
                summary_data[val] = {'act':[vals[1]], 'pas':[vals[2]]}
            else:
                summary_data[val]['act'].append(vals[1])
                summary_data[val]['pas'].append(vals[2])
    saliency_diff = []
    act_mean = []
    act_std = []
    pas_mean = []
    pas_std = []
    for k,v in summary_data.iteritems():
        saliency_diff.append(k)
        act_mean.append(np.mean(v['act']))
        act_std.append(np.std(v['act'])/2)
        pas_mean.append(np.mean(v['pas']))
        pas_std.append(np.std(v['pas'])/2)
    
    save_format = 'png'
    plt.figure()
    plt.errorbar(saliency_diff, act_mean, yerr = act_std, linestyle='None', marker='o', markerfacecolor='red', elinewidth=2, ecolor='red')
    plt.title('Active construction as a function of agent-patient saliency')
    plt.xlabel('(Agt_saliency - Pat_saliency)*10', fontsize=14)
    plt.ylabel('Mean # Active Cxn', fontsize=14)
    plt.ylim(-0.5, 1.5)
    save_to = "%sactive.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)
    
    plt.figure()
    plt.errorbar(saliency_diff, pas_mean, yerr = pas_std, linestyle='None', marker='o', markerfacecolor='blue', elinewidth=2, ecolor='blue')
    plt.title('Passive construction as a function of agent-patient saliency')
    plt.xlabel('(Agt_saliency - Pat_saliency)*10', fontsize=14)
    plt.ylabel('Mean # Passive Cxn', fontsize=14)
    plt.ylim(-0.5, 1.5)
    save_to = "%spassive.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)


if __name__ == "__main__":
    active_passive(file_path="./sim.csv", output_path='./tmp/plots/dyn_patient_first/')

