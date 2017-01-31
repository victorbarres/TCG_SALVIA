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
    
def load_sim_data_ACM(sim_dir, areas):
    """
    """

    FILE_EXT = '.csv'
    sim_names = [f_name for f_name in os.listdir(sim_dir) if f_name[-4:] == FILE_EXT]
    
    dataframes = {}
    for name in sim_names:
        input_name = name[:-4] # remove extension
        dataframes[input_name] = pd.read_csv(sim_dir + name)
        dataframes[input_name]['input_name'] = input_name # adds the input name as a column
        area_order = input_name.split('_')
        for area in areas:
            dataframes[input_name][area] = area_order.index(area) + 1 # Adding a column per area giving order info
            
    combined_df = pd.concat(dataframes.values()) # concatenates all the dataframes
    dataframes['combined'] = combined_df

    return dataframes
    
def plot_main_effects(df, column_names, save=False, save_folder='./', save_format='pdf', tag=''):
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
            file_name = '%s/%s_main_effects%s.%s' %(save_folder, name, tag, save_format)
            plt.savefig(file_name, facecolor='w', edgecolor='w', bbox_inches='tight', format=save_format)
    if not(save):   
        plt.show()
    
def plot_relationship(df, independent_var, dependent_vars, save=False, save_folder='./', save_format='pdf', tag=''):
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
            file_name = '%s/%s(%s)%s.%s' %(save_folder, var, independent_var, tag, save_format)
            plt.savefig(file_name, facecolor='w', edgecolor='w', bbox_inches='tight', format=save_format)
    
    if not(save):
        plt.show()

def basic_analyses_threshold():
    """
    """
    sim_folder = '2017-01-28_18-26-43_kuchinsky'
    sim_dir = "./%s/" % sim_folder
    df_dict = load_sim_data(sim_dir)
    combined_df = df_dict['combined']

#    # apply filter
#    filtered_df = combined_df[combined_df['time_pressure'] > 1]

    output_names = ['syntactic_complexity', 'global_syntactic_complexity', 'utterance_lengths', 'structural_compactness', 'partial_readout' ,'num_requests', 'utterance_intervals', 'cxn_usage_count', 'num_utterances']

    save_folder = '%s/plots/' %sim_dir
    save_format = 'png'
    plot_main_effects(combined_df, output_names, save=True, save_folder=save_folder, save_format=save_format)
    plot_relationship(combined_df, 'time_pressure', output_names, save=True, save_folder=save_folder,save_format=save_format)

def basic_analyses_WM_capacity():
    """
    """
    sim_folder = '2017-01-28_18-26-43_kuchinsky'
    sim_dir = "./%s/" % sim_folder
    df_dict = load_sim_data(sim_dir)
    combined_df = df_dict['combined']

    # apply filter
    filtered_df = combined_df[combined_df['wm_capcity'] != np.NaN]

    output_names = ['syntactic_complexity', 'global_syntactic_complexity', 'utterance_lengths', 'structural_compactness', 'partial_readout' ,'num_requests', 'utterance_intervals', 'cxn_usage_count', 'num_utterances']

    save_folder = '%s/plots/' %sim_dir
    save_format = 'png'
    plot_main_effects(filtered_df, output_names, save=True, save_folder=save_folder, save_format=save_format)
    plot_relationship(filtered_df, 'time_pressure', output_names, save=True, save_folder=save_folder,save_format=save_format)

def ACM_analyses():
    """
    """
    sim_folder = '2017-01-28_18-26-43_kuchinsky'
    sim_dir = "./%s/" % sim_folder
    
    areas = ['event', 'action', 'agent', 'patient']
    df_dict = load_sim_data_ACM(sim_dir, areas)
    combined_df_raw = df_dict['combined']
    
    # Remove the cases in which action is before event.
    combined_df = combined_df_raw.query('event < action')
#    print combined_df.dtypes
    
    combined_df['act_pref'] =  combined_df.ACTIVE/(combined_df.PASSIVE +  combined_df.ACTIVE)*100
    combined_df['agent_cue'] = combined_df.agent < combined_df.patient
    combined_df['input_rate_ratio'] =combined_df.input_rate/combined_df.tau
    combined_df['obj>act'] = combined_df.event>2

#    easy_obj_df = combined_df[combined_df['obj>act']==True]
#    hard_obj_df = combined_df[combined_df['obj>act']==False]
#
#    scene_type = 'obj>act'
#    df_stats = easy_obj_df.groupby(['agent_cue', 'input_rate_ratio','time_pressure'])['act_pref'].agg([np.mean, np.std])
#    for cue in df_stats.index.levels[0]:
#        plt.figure(facecolor='white')
#        for ratio in [df_stats.index.levels[1][0],df_stats.index.levels[1][-1]]:
#            df = df_stats.xs((cue, ratio))
#            plt.errorbar(df.index, df['mean'], yerr=df['std'], lw=2, marker='o', label=ratio)
#        title = 'Scene type: %s, Agent cue: %r.' %(scene_type, cue)
#        plt.title(title)
#        plt.xlabel('time pressure', fontsize=14)
#        plt.ylabel('act(%)', fontsize=14)
#        plt.margins(0.05, 0.1)
#        plt.legend()
#    
#    scene_type = 'act>obj'
#    df_stats = hard_obj_df.groupby(['agent_cue', 'input_rate_ratio','time_pressure'])['act_pref'].agg([np.mean, np.std])
#    for cue in df_stats.index.levels[0]:
#        plt.figure(facecolor='white')
#        for ratio in [df_stats.index.levels[1][0],df_stats.index.levels[1][-1]]:
#            df = df_stats.xs((cue, ratio))
#            plt.errorbar(df.index, df['mean'], yerr=df['std'], lw=2, marker='o', label=ratio)
#        title = 'Scene type: %s, Agent cue: %r.' %(scene_type, cue)
#        plt.title(title)
#        plt.xlabel('time pressure', fontsize=14)
#        plt.ylabel('act(%)', fontsize=14)
#        plt.margins(0.05, 0.1)
#        plt.legend()
#    
#    plt.show()

    simple_df = combined_df[combined_df['tau']==505.0]
    
    df_stats = simple_df.groupby(['obj>act','agent_cue','time_pressure'])['act_pref'].agg([np.mean, np.std])
    for scene_type in df_stats.index.levels[0]:
        plt.figure(facecolor='white')
        for cue in df_stats.index.levels[1]:
            df = df_stats.xs((scene_type, cue))
            plt.errorbar(df.index, df['mean'], yerr=df['std'], lw=2, marker='o', label=cue)
        type_name = 'obj>act' if scene_type else 'act>obj'
        title = 'Scene type: %s' %(type_name)
        plt.title(title)
        plt.xlabel('time pressure', fontsize=14)
        plt.ylabel('active(%)', fontsize=14)
        plt.margins(0.05, 0.1)
        plt.legend()
    plt.show()
    
    
#    easy_obj_df = combined_df[combined_df['obj>act']==True]
#    hard_obj_df = combined_df[combined_df['obj>act']==False]
#    easy_obj_df_stats = easy_obj_df.groupby(['agent_cue', 'input_rate_ratio','time_pressure'])['ACT-PAS'].agg([np.mean, np.std])
#    hard_obj_df_stats = hard_obj_df.groupby(['agent_cue', 'input_rate_ratio','time_pressure'])['ACT-PAS'].agg([np.mean, np.std])
#    
#    for df in [easy_obj_df_stats,hard_obj_df_stats]:
#        i = 1
#        rows = len(df.index.levels[1])
#        plt.figure(facecolor='white')
#        for cue in df.index.levels[0]:
#            plt.subplot(rows, 1, i)
#            for ratio in df.index.levels[1]:
#                print ratio
#                df = df.xs((cue, ratio))
#                plt.errorbar(df.index, df['mean'], yerr=df['std'], lw=2, marker='o', label=ratio)
#            title = 'agent-patient = %i ' %(cue)
#            plt.title(title)
#            plt.xlabel('time_pressure', fontsize=14)
#            plt.ylabel('act-pas', fontsize=14)
#            plt.margins(0.05, 0.1)
#            plt.tight_layout()
#            plt.legend()
#        i+=1
#    
#        plt.show()
        
        
    
#    save_folder = '%s/plots/' %sim_dir
#    save_format = 'pdf'
    
    
#    plot_main_effects(combined_df, output_names, save=True, save_folder=save_folder, save_format=save_format, tag='')
#    plot_relationship(combined_df, 'time_pressure', output_names, save=True, save_folder=save_folder,save_format=save_format, tag='')

def ACM_simple_analyses():
    """
    """
    sim_folder = '2017-01-29_16-01-14_kuchinsky_3_no_focus_(165313308)'
    sim_dir = "./%s/" % sim_folder
    areas = ['action', 'agent', 'patient']
    df_dict = load_sim_data_ACM(sim_dir, areas)
    combined_df = df_dict['combined']

    combined_df['act_pref'] =  combined_df.ACTIVE/(combined_df.PASSIVE +  combined_df.ACTIVE)*100
    df_stats = combined_df.groupby(['input_name', 'time_pressure'])['act_pref', 'ACTIVE', 'PASSIVE'].agg([np.mean, np.std])
    
    save_folder = '%s/plots/' %sim_dir
    save_format = 'png'
    
    if not(os.path.exists(save_folder)):
        os.mkdir(save_folder)
    
    for name in df_stats.index.levels[0]:
        plt.figure(facecolor='white')
        df = df_stats.xs(name)
        style={'PASSIVE':{'ls':'--', 'marker':'s'}, 'ACTIVE':{'ls':':', 'marker':'o'}}
        for var in ['PASSIVE', 'ACTIVE']:
            plt.errorbar(df.index, df[var]['mean'], yerr=df[var]['std'], lw=2, ls=style[var]['ls'], marker=style[var]['marker'], label=var)
        plt.title(name)
        plt.xlabel('time pressure', fontsize=14)
        plt.ylabel('active(%)', fontsize=14)
        plt.ylim(-0.5,1.5)
        plt.margins(0.05, 0.1)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, prop={'size':8})
#        plt.tight_layout()
        file_name = '%s/%s.%s' %(save_folder, name, save_format)
        plt.savefig(file_name, facecolor='w', edgecolor='w', format=save_format)
    
#    plt.show()

def ACM_simple_analyses_SVO_only():
    """
    """
    sim_folder = '2017-01-29_22-00-20_kuchinksy_simple_SVO_only_(982979794)'
    sim_dir = "./%s/" % sim_folder
    areas = ['action', 'agent', 'patient']
    df_dict = load_sim_data_ACM(sim_dir, areas)
    combined_df = df_dict['combined']

    df_stats = combined_df.groupby(['input_name', 'time_pressure'])['ACTIVE','first_request',  ].agg([np.mean, np.std])

    
#    plt.show()
if __name__ == "__main__":
    ACM_simple_analyses_SVO_only()
    
    
    

