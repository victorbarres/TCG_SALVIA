# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 14:34:02 2016

@author: victor barres

Preliminary test for simulation analyses!
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def active_passive_static(file_path="./my_sim/", file_name="sim.csv", output_folder="plots/"):
    """
    """
    import os
    
    output_path = file_path + output_folder
    
    if not(os.path.exists(output_path)):
        os.mkdir(output_path)

    # Load .csv data into a pandas dataframe
    df= pd.read_csv(file_path + file_name)
    
    if 'produced' in df:
        print len(df.index)
        print len(df[df.produced == False].index)
        df = df[df.produced == True]     
    
    df['saliency_diff'] = df['x1'].map(lambda x: int(10*x)) - df['x2'].map(lambda x: int(10*x))
    df['act-pas'] = df.active - df.passive

    
    df_stats = df.groupby(['saliency_diff'])['active', 'passive', 'act-pas'].agg([np.mean, np.std])
    
    save_format = 'pdf'
    plt.figure()
    plt.errorbar(df_stats.index, df_stats['active']['mean'], yerr = df_stats['active']['std'], linestyle='None', marker='o', markerfacecolor='red', elinewidth=2, ecolor='red')
    plt.title('Active construction as a function of agent-patient saliency')
    plt.xlabel('(Agt_saliency - Pat_saliency)*10', fontsize=14)
    plt.ylabel('Mean # Active Cxn', fontsize=14)
    plt.ylim(-0.5, 1.5)
    save_to = "%sactive.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)
    
    plt.figure()
    plt.errorbar(df_stats.index, df_stats['passive']['mean'], yerr = df_stats['passive']['std'], linestyle='None', marker='o', markerfacecolor='blue', elinewidth=2, ecolor='blue')
    plt.title('Passive construction as a function of agent-patient saliency')
    plt.xlabel('(Agt_saliency - Pat_saliency)*10', fontsize=14)
    plt.ylabel('Mean # Passive Cxn', fontsize=14)
    plt.ylim(-0.5, 1.5)
    save_to = "%spassive.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)
    
    plt.figure()
    plt.errorbar(df_stats.index, df_stats['act-pas']['mean'], yerr = df_stats['act-pas']['std'], linestyle='None', marker='o', markerfacecolor='blue', elinewidth=2, ecolor='blue')
    plt.title('Active - passive cxn as a function of agent-patient saliency')
    plt.xlabel('(Agt_saliency - Pat_saliency)*10', fontsize=14)
    plt.ylabel('Mean active-passive cxn', fontsize=14)
    plt.ylim(-1.5, 1.5)
    save_to = "%sactive-passive.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)
    
def active_passive_dynamic(file_path="./my_sim/", file_name="sim.csv", output_folder="plots/"):
    """
    """
    import os
    output_path = file_path + output_folder
    
    if not(os.path.exists(output_path)):
        os.mkdir(output_path)
        
    df = pd.read_csv(file_path + file_name)
    if 'produced' in df:
        print len(df.index)
        print len(df[df.produced == False].index)
        df = df[df['produced'] == True]
        
    df['act-pas'] = df.active - df.passive
    df['saliency_diff'] = df['x1'].map(lambda x: int(x*10)) - df['x2'].map(lambda x: int(x*10))

    save_format = 'pdf'
    plt.figure()
    rates = df['x0'].unique()
    for r in rates:
        new_df = df[df['x0'] == r]
        df_stats = new_df.groupby(['saliency_diff'])['active', 'passive', 'act-pas'].agg([np.mean, np.std])
        plt.errorbar(df_stats.index, df_stats['act-pas']['mean'], yerr = df_stats['act-pas']['std'], marker='o', label= r)
    title = 'Active - passive cxn as a function of agent-patient saliency'  
    plt.title(title)
    plt.xlabel('(Agt_saliency - Pat_saliency)*10', fontsize=14)
    plt.ylabel('Mean active-passive cxn', fontsize=14)
    plt.ylim(-1.5, 1.5)
    plt.legend()
    plt.show()
    save_to = "%sactive-passive-err.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)
    
def time_pressure_dynamic(file_path="./my_sim/", file_name="sim.csv", output_folder="plots/"):
    """
    """
    import os
    output_path = file_path + output_folder
    
    if not(os.path.exists(output_path)):
        os.mkdir(output_path)
        
    df = pd.read_csv(file_path + file_name)
    
    # Renaming for simplicity
    df = df.rename(columns = {"Grammatical_WM_P.C2.confidence_threshold": "threshold", "Control.task.start_produce": "start_produce"})
    
    df = df[df['produced'] == True]
    
    df_stats= df.groupby(['start_produce'])['syntactic_complexity_mean', 'syntactic_complexity_std', 'utterance_length_mean', 'utterance_length_std', 'total_constructions'].agg([np.mean, np.std])
    save_format = 'pdf'
    plt.figure()
    plt.errorbar(df_stats.index, df_stats['syntactic_complexity_mean']['mean'], yerr=df_stats['syntactic_complexity_mean']['std'], linestyle='None', marker='o')
    plt.title('Effet of time pressure on syntactic complexity')
    plt.xlabel('Start produce time', fontsize=14)
    plt.ylabel('Mean syntactic complexity', fontsize=14)
    save_to = "%ssyntactic_complexity.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)    
    
    
    plt.figure()
    plt.errorbar(df_stats.index, df_stats['utterance_length_mean']['mean'], yerr=df_stats['utterance_length_mean']['std'], linestyle='None', marker='o')
    plt.title('Effet of time pressure on utterance length')
    plt.xlabel('Start produce time', fontsize=14)
    plt.ylabel('Mean utterance length', fontsize=14)
    save_to = "%sutterance_length.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)
    
    rates = rates = df['x0'].unique()
    rates.sort()
    df_stats= df.groupby(['x0','start_produce'])['syntactic_complexity_mean', 'syntactic_complexity_std', 'utterance_length_mean', 'utterance_length_std', 'total_constructions'].agg([np.mean, np.std])
    
    plt.figure()    
    for r in rates:
        new_df_stats = df_stats.ix[r]
        plt.errorbar(new_df_stats.index, new_df_stats['syntactic_complexity_mean']['mean'], yerr=new_df_stats['syntactic_complexity_mean']['std'], marker='o', label = r)
    plt.title('Effet of time pressure on syntactic complexity')
    plt.xlabel('Start produce time', fontsize=14)
    plt.ylabel('Mean syntactic complexity', fontsize=14)
    plt.legend()
    plt.show()
    save_to = "%ssyntactic_complexity_rate.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)    
    
    
    plt.figure()    
    for r in rates:
        new_df_stats = df_stats.ix[r]
        plt.errorbar(new_df_stats.index, new_df_stats['utterance_length_mean']['mean'], yerr=new_df_stats['utterance_length_mean']['std'], marker='o', label = r)
    plt.title('Effet of time pressure on utterance length')
    plt.xlabel('Start produce time', fontsize=14)
    plt.ylabel('Mean utterance length', fontsize=14)
    plt.legend()
    plt.show()
    save_to = "%sutterance_length_rate.%s" % (output_path, save_format)
    plt.savefig(save_to, facecolor='w', edgecolor='w', format=save_format)    
        
        
        
        
    
    

if __name__ == "__main__":
    file_name = 'blue_woman_kick_man'
    file_path = "./analyses/%s/" % file_name
#    active_passive_static(file_path=file_path, file_name=file_name+'.csv')
#    active_passive_dynamic(file_path=file_path, file_name=file_name+'.csv')
    time_pressure_dynamic(file_path=file_path, file_name=file_name+'.csv')

