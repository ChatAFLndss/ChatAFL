from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot as plt
import pandas as pd

#Read the results
df = read_csv('results.csv')

#Calculate the mean of code coverage
#Store in a list first for efficiency
mean_list = []

for subject in [' exim']:
  for fuzzer in [' aflnet', ' aflnwe']:
    for cov_type in [' b_abs', ' b_per', ' l_abs', ' l_per']:
      #get subject & fuzzer & cov_type-specific dataframe
      df1 = df[(df['subject'] == subject) & 
                       (df['fuzzer'] == fuzzer) & 
                       (df['cov_type'] == cov_type)]

      for time in range(1, 60, 1):
        cov_total = 0
        runs = 0
        for run in range(1, 5, 1):
          #get run-specific data frame
          df2 = df1[df1['run'] == run]

          #get the starting time for this run
          start = df2.iloc[0, 0]

          #get all rows given a cutoff time
          df3 = df2[df2['time'] <= start + time*60]
          
          #update total coverage and #runs
          cov_total += df3.tail(1).iloc[0, 5]
          runs += 1
        
        #add a new row
        mean_list.append((subject, fuzzer, cov_type, time, cov_total / runs))

#Convert the list to a dataframe
mean_df = pd.DataFrame(mean_list, columns = ['subject', 'fuzzer', 'cov_type', 'time', 'cov'])


#Plot the data
#mean_df.set_index('time', inplace=True)
#mean_df.groupby(['fuzzer', 'cov_type'])['cov'].plot(legend=True)

#fig = plt.figure(1, figsize = (20, 10))
#chart_b_abs = fig.add_subplot(221)
#chart_b_per = fig.add_subplot(222)
#chart_l_abs = fig.add_subplot(223)
#chart_l_per = fig.add_subplot(224)

#for key, grp in mean_df.groupby(['fuzzer', 'cov_type']):
#    if key[1] == ' b_abs':
#      chart_b_abs.plot(grp['time'], grp['cov'])
#    if key[1] == ' b_per':
#      chart_b_per.plot(grp['time'], grp['cov'])
#    if key[1] == ' l_abs':
#      chart_l_abs.plot(grp['time'], grp['cov'])
#    if key[1] == ' l_per':
#      chart_l_per.plot(grp['time'], grp['cov'])

fig, axes = plt.subplots(2, 2, figsize = (20, 10))
fig.suptitle("Code coverage analysis")

for key, grp in mean_df.groupby(['fuzzer', 'cov_type']):
    if key[1] == ' b_abs':
      axes[0, 0].plot(grp['time'], grp['cov'])
      axes[0, 0].set_title('Edge coverage over time (absolute count)')
    if key[1] == ' b_per':
      axes[1, 0].plot(grp['time'], grp['cov'])
      axes[1, 0].set_title('Edge coverage over time in percentage')
      axes[1, 0].set_ylim([0,100])
    if key[1] == ' l_abs':
      axes[0, 1].plot(grp['time'], grp['cov'])
      axes[0, 1].set_title('Line coverage over time (absolute count)')
    if key[1] == ' l_per':
      axes[1, 1].plot(grp['time'], grp['cov'])
      axes[1, 1].set_title('Line coverage over time in percentage')
      axes[1, 1].set_ylim([0,100])

plt.legend(('AFLNet', 'AFLNwe'), loc='upper left')
plt.show()
