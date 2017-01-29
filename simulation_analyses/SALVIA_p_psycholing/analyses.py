# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 14:34:02 2016

@author: Victor Barres

Coarse analysis of the effect of parameters on production

"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_sim_data(sim_dir="./"):
    """
    returns a dictionary of pandas dataframes for each sim data csv files in sim_dir.
    Adds a "combined" dataframes that concatenates all the loaded df.
    """
    FILE_EXT = '.csv'
    sim_names = [f_name for f_name in os.listdir(sim_dir) if f_name[-4:] == FILE_EXT]
    
    dataframes = {}
    for name in sim_names:
        input_name = name[:-4] # remove extension
        dataframes[input_name] = pd.read_csv(sim_dir + name)
        dataframes[input_name]['input_name'] = input_name # adds the input name as a column
    combined_df = pd.concat(dataframes.values()) # concatenates all the dataframes
    dataframes['combined'] = combined_df

    return dataframes
    
def plot_main_effects(df, column_names, save=False, save_folder='./', save_format='pdf'):
    """
    """
    for name in column_names:
        plt.figure(facecolor='white')
        plt.subplot(211)
        title = '%s (hist)' %name
        plt.title(title)
        df[name].hist()
        plt.autoscale(enable=True)
        
        plt.subplot(212)
        title = '%s (boxplot)' %name
        plt.title(title)
        df.boxplot(column=name,return_type='axes')
        if save:
            if not(os.path.exists(save_folder)):
                os.mkdir(save_folder)
            file_name = '%s/%s_main_effects.%s' %(save_folder, name, save_format)
            plt.savefig(file_name, bbox_inches='tight', format=save_format)
    if not(save):   
        plt.show()
    
def plot_relationship(df, independent_var, dependent_vars, save=False, save_folder='./', save_format='pdf'):
    """
    """
    df_stats= df.groupby([independent_var])[dependent_vars].agg([np.mean, np.std])
    for var in dependent_vars:        
        plt.figure(facecolor='white')
        plt.errorbar(df_stats.index, df_stats[var]['mean'], yerr=df_stats[var]['std'], lw=2, marker='o')
        title = 'Effect of %s on %s.' %(independent_var, var)
        plt.title(title)
        plt.xlabel(independent_var, fontsize=14)
        y_label = 'Mean %s' %var
        plt.ylabel(y_label, fontsize=14)
        plt.margins(0.05, 0.1)
        if save:
            if not(os.path.exists(save_folder)):
                os.mkdir(save_folder)
            file_name = '%s/%s(%s).%s' %(save_folder, var, independent_var, save_format)
            plt.savefig(file_name, bbox_inches='tight', format=save_format)
    
    if not(save):
        plt.show()  
    
    
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
    sim_folder = '2017-01-27_14-37-54_threshold'
    sim_dir = "./%s/" % sim_folder
    df_dict = load_sim_data(sim_dir)
    combined_df = df_dict['combined']

    # apply filter
    filtered_df = combined_df[combined_df['time_pressure'] > 1]

    output_names = ['syntactic_complexity', 'global_syntactic_complexity', 'utterance_lengths', 'structural_compactness', 'partial_readout' ,'num_requests', 'utterance_intervals', 'cxn_usage_count', 'num_utterances']
    save_folder = '%s/plots_time_pressure_sup_1/' %sim_dir
    save_format = 'pdf'
    plot_main_effects(filtered_df, output_names, save=True, save_folder=save_folder, save_format=save_format)
    plot_relationship(filtered_df, 'time_pressure', output_names, save=True, save_folder=save_folder,save_format=save_format)
    
    

