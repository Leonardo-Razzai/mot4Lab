from TempAnalyzer import *

base_name = 'cool_dds'
x_label = 'Cool DDS'
unit = ''

iterator = [10, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11]
T_list = []
err_T_list = []

t1 = 2.0  # ms
t2 = 20.0  # ms
    
for val in iterator:
    im1 = Image(f'{base_name}={val}{unit}_tof={t1:.1f}ms.fits.gz')
    im1.select_roi(0, 400, 0, 500)
    im1.fit_gaussian('x', plot=True)

    im2 = Image(f'{base_name}={val}{unit}_tof={t2:.1f}ms.fits.gz')
    im2.select_roi(0, 400, 0, 500)
    im2.fit_gaussian('x', plot=False)
    
    T, dT = get_temperature(im1, im2, t1, t2)
    
    T_list.append(T)    
    err_T_list.append(dT)
    
    print(f'{x_label}: {val}, Temp: ({T:.2f} +- {dT:.2f}) uK')
    
# plotting
import matplotlib.pyplot as plt
plt.errorbar(iterator, T_list, err_T_list, fmt='o', alpha=0.9, color='blue', ecolor='royalblue', capsize=5, label='Data')
plt.xlabel(f'{x_label} ({unit})', fontdict=base_font)
plt.ylabel('Temp (uK)', fontdict=base_font)
plt.title(f'Temperature vs {x_label}', fontdict=title_font)
plt.grid()
plt.savefig(f'Temp_vs_{base_name}.png')


