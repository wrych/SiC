import os
import sys

import matplotlib.pyplot
import numpy

def read_data(path, folder, filename):
    print(folder)
    with open(os.path.join(path,folder,filename),'r') as f:
        data = []
        for l in f:
            l = l.replace('[', '')
            l = l.replace(']', '')
            data.append([float(v) for v in l.split()])
        return(numpy.asarray(data))


def get_xy_data(data, indices):
    x = []
    y = []
    for d in data:
        x.extend(d[:, indices['x']])
        y.extend(d[:, indices['y']])
    x = numpy.asarray(x)
    y = numpy.asarray(y)
    return x,y

full_path = sys.argv[1]
path, folder = os.path.split(full_path.rstrip('/'))
folder = folder.replace('cr_1', '{0}')
folder = folder.replace('cr_2', '{0}')
print path, folder
data = [read_data(path, folder.format(cr), 'Epics-transmissionvsEpics-currents.txt') for cr in ['cr_1','cr_2']]
data2 = [read_data(path, folder.format(cr), 'Epics-transmissionvsEpics-diode_current.txt') for cr in ['cr_1','cr_2']]

fig = matplotlib.pyplot.figure()
ax = fig.add_subplot(1,1,1)

x1, y1 = get_xy_data(data, {'x': 4,'y': 3})
x2, y2 = get_xy_data(data2, {'x': 1,'y': 0})

A = numpy.vstack([x1, numpy.ones(len(x1))]).T

ratios = y2/y1
print y1
print y2
print ratios

ax.plot(x1,ratios,'b.', label='')
ax.set_title('Linearity ({0})\n{1}'.format(folder,path))
ax.set_ylabel('Ratio (diode/xbpm) []')
ax.set_xlabel('Epics/transmission []')
ax.set_xscale('log')

fig.savefig(os.path.join(path, folder.format('cr_1'), 'Epics-transmissionvsEpics-currents.png'))
#fig.show()
#raw_input()