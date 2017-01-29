# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 14:34:02 2016

@author: victor barres

Coarse analysis of the effect of parameters on production

"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def level_0(file_path="./", file_name="combined.csv", output_folder="plots/"):
    """
    Analysis of outputs
    """
    return


def level_1(file_path="./", file_name="combined.csv", output_folder="plots/"):
    """
    Analysis of main effects for each parameters
    """
    output_path = file_path + output_folder
    if not(os.path.exists(output_path)):
        os.mkdir(output_path)
    
    df = pd.read_csv(file_path + file_name)
    
    return df
    
    
def time_pressure_dynamic(file_path="./my_sim/", file_name="sim.csv", output_folder="plots/"):
    """
    """
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
    file_name = 'transitive_action_static'
    file_path = "./analyses/%s/" % file_name
#    active_passive_static(file_path=file_path, file_name=file_name+'.csv')
#    active_passive_dynamic(file_path=file_path, file_name=file_name+'.csv')
    time_pressure_dynamic(file_path=file_path, file_name=file_name+'.csv')

