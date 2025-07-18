from TempAnalyzer import *
import matplotlib.pyplot as plt  

def Analysis_Num_and_T(dataset, t1, t2):
    
    base_name = dataset['base_name']
    x_label = dataset['x_label']
    unit = dataset['unit']
    iterator = dataset['iterator']

    T_list = []
    err_T_list = []

    N_atoms_list = []
    err_N_atoms_list = []
    
    for val in iterator:
        print('----------------------------------------------------------')
        im1 = Image(f'{base_name}={val}{unit}_tof={t1:.1f}ms.fits.gz')
        im1.select_roi(0, 400, 0, 600)
        im1.fit_gaussian('x', plot=False)
        
        im2 = Image(f'{base_name}={val}{unit}_tof={t2:.1f}ms.fits.gz')
        im2.select_roi(0, 400, 0, 600)
        im2.fit_gaussian('x', plot=False)
        
        N_atoms, err_N_atoms = im2.Get_Number_Of_Atoms(axis='x')
        
        N_atoms_list.append(N_atoms)
        err_N_atoms_list.append(err_N_atoms)
        
        T, dT = Get_temperature(im1, im2, t1, t2)
        
        T_list.append(T)    
        err_T_list.append(dT)
        
        print(f'{x_label}: {val}, Temp: ({T:.2f} +- {dT:.2f}) uK\n')
        
    return T_list, err_T_list, N_atoms_list, err_N_atoms_list

def Analysis_and_Plotting(dataset):
    
    base_name = dataset['base_name']
    x_label = dataset['x_label']
    unit = dataset['unit']
    iterator = dataset['iterator']
    
    T_list, err_T_list, N_atoms_list, err_N_atoms_list = Analysis_Num_and_T(dataset, t1=2.0, t2=20.0)
        
    # plotting
    plt.figure(figsize=(8, 5))
    plt.errorbar(iterator, T_list, err_T_list, fmt='o', alpha=0.9, color='blue', ecolor='royalblue', capsize=5, label='Data')
    plt.xlabel(f'{x_label} ({unit})', fontdict=base_font)
    plt.ylabel('Temp (uK)', fontdict=base_font)
    plt.title(f'Temperature vs {x_label}', fontdict=title_font)
    plt.grid(linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'Temp_vs_{base_name}.png')
    plt.clf()
    plt.close()
    
    N_atoms = np.array(N_atoms_list) * 1e-8  # convert to 10^8
    err_N_atoms = np.array(err_N_atoms_list) * 1e-8  # assuming 10% error
    plt.figure(figsize=(8, 5))
    plt.errorbar(iterator, N_atoms, err_N_atoms, fmt='o', alpha=0.9, color='blue', ecolor='royalblue', capsize=5, label='Data')
    plt.xlabel(f'{x_label} ({unit})', fontdict=base_font)
    plt.ylabel(r'Num Atoms ($10^8$)', fontdict=base_font)
    plt.title(f'Num of Atoms vs {x_label}', fontdict=title_font)
    plt.grid(linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'Num_atoms_vs_{base_name}.png')
    plt.clf()
    plt.close()
    
dataset_cool_dds = {
    'base_name' : 'cool_dds',
    'x_label' : 'Cool DDS Frequency',
    'unit' : '',
    'iterator' : [10, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11]
}

dataset_time_ramp_aom = {
    'base_name' : 'time_ramp_aom',
    'x_label' : 'Ramp Time',
    'unit' : 'ms',
    'iterator' : [0.4, 0.6, 1, 2, 3, 4, 5, 10, 15, 20]
}

dataset_rep_delta = {
    'base_name' : 'rep_delta',
    'x_label' : 'Rep. Red Detuning',
    'unit' : '',
    'iterator' : [5, 10, 15, 20, 25, 30]
}

dataset_aom_amp = {
    'base_name' : 'aom_amp',
    'x_label' : 'AOM Amplitude',
    'unit' : '',
    'iterator' : [50, 100, 200, 300, 400, 500, 600, 700]
}

dataset_list = [dataset_cool_dds, dataset_time_ramp_aom, dataset_rep_delta, dataset_aom_amp]

for dataset in dataset_list:
    Analysis_and_Plotting(dataset)
