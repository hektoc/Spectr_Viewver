import sys
import matplotlib.pyplot as plt
from ZajSpectr.ZajSpectrReader import ZajSpectrReader, ZajSpectr


class MainWindow:
    
    def __init__(self, filename=''):
        reader = ZajSpectrReader
        try:
            zaj_spec = reader.return_zai_spectr(ZajSpectrReader, filename=filename)
            self.lineplot(zaj_spec)
        # не удалось определить содержимое файла со спектром
        except TypeError:
            exit()
        
    @staticmethod
    def lineplot(cur_spectr):
        _, ax = plt.subplots()
        
        if isinstance(cur_spectr, ZajSpectr):
            x_data = cur_spectr.channel
            y_data = cur_spectr.data
            details = cur_spectr.details
        else:
            details = ''
            if 'vl' in cur_spectr and 'val' in cur_spectr:
                x_data = cur_spectr['vl']
                y_data = cur_spectr['val']
            else:
                x_data, y_data = [], []
            
        ax.plot(x_data, y_data, lw=1, color='#539caf', alpha=1, label=details)

        ax.set_title(sys.argv[1].split('\\')[-1])
        ax.set_xlabel('Длина волны (или номер канала)')
        ax.set_ylabel('Значение (единицы отсчёта в линейке)')
        ax.legend(loc='upper right')
        plt.show()
      
        
filename = sys.argv[1]
a = MainWindow(filename)
