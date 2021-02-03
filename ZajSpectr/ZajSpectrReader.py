import csv
from abc import ABC, ABCMeta, abstractmethod
from typing import Union


class ZajSpectr():
    def __init__(self, filename:str = '', data: list = None, channel: list = None, exposition: int = 0, time: int = 0):
        self._filename = filename
        self._data = data
        self._channel = channel
        self._exposition = exposition
        self._time = time
    
    @property
    def channel(self):
        return self._channel
    
    @property
    def data(self):
        return self._data
    
    @property
    def details(self):
        detail = ''
        
        """if self._filename:
            detail += self._filename.split('\\')[-1] + '\n'"""
        
        if self._time:
            detail += 'Time: ' + str(self._time) + '\n'

        if self._exposition:
            detail += 'Экспозиция: ' + str(self._exposition) + '\n'
        return detail.strip()

    
class ZajSpectrReaderAbstract(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def return_zai_spectr(self, filename: str) -> ZajSpectr:
        """:input принимает на вход строку с именем файла
        :return Возвращает экземпляр класса ZajSpectr"""


class ZajSpectrReader(ZajSpectrReaderAbstract):

    def __init__(self):
        self.cur_data_delimiter = ''
        self.cur_header_delimiter = ''

    @staticmethod
    def _return_number_or_false(num: str) -> Union[int, float, bool]:
        if num.isdigit():
            return int(num)
        try:
            return float(num)
        except ValueError:
            return False

    @staticmethod
    def _find_delimiter(line: str) -> Union[str, bool]:
        if ':' in line and len(line.strip(':')) > 1:
            return ':'
        elif '\t' in line and len(line.strip('\t')) > 1:
            return '\t'
        elif ';' in line and len(line.strip(';')) > 1:
            return ';'
        else:
            return False

    def read_headed_spectr(self, file) -> dict:
        """Читаем из файла строки с заголовками и данными вида
        [header][self.cur_header_delimiter]
        [int][self.cur_data_delimiter][int]
        [int][self.cur_data_delimiter][int]
        или
        [header][self.cur_header_delimiter][int]
        [header][self.cur_header_delimiter][int]
        :return возвращаем словарь с результатами
        """
        result = {}
        cur_header = ''
        file.seek(0, 0)
        self.cur_data_delimiter, self.cur_header_delimiter = '', self.cur_data_delimiter
        for line in csv.reader(file, delimiter=self.cur_header_delimiter):
            # Если успешно разделили строку, значит перед нами заголовок
            if len(line) > 1:
                if line[1] != '':
                    result[line[0]] = line[1]
                else:
                    cur_header = line[0]
                    result[cur_header] = {}
            # Если не разделили - значит перед нами данные
            else:
                # Если разделитель для данных еще не найден
                if self.cur_data_delimiter == '':
                    self.cur_data_delimiter = self._find_delimiter(line[0])
                    # print( 'разделитель ', self.cur_data_delimiter)
                if not not self.cur_data_delimiter and cur_header:
                    cur_data = line[0].split(self.cur_data_delimiter)
                    result[cur_header][int(cur_data[0])] = int(cur_data[1])
        return result
        
    def read_csv_spectr(self, file) -> dict:
        """Читаем из файла строки с данными вида [int][self.cur_data_delimiter][int] и
        :return возвращаем словарь с результатами"""
        result = {}
        for line in csv.reader(file, delimiter=self.cur_data_delimiter):
            result[int(line[0])] = float(line[1])
        return result
    
    def return_zai_spectr(self, filename: str) -> ZajSpectr:
        # print(filename)
        with open(filename, 'r') as file:
            result = {}
            # читаем одну линию из файла
            first_line = file.readline().strip()
            self.cur_data_delimiter = self._find_delimiter(first_line)
            splitted_line = first_line.split(self.cur_data_delimiter)
            # если нашли разделитель и строка разбилась минимум на 2 части
            if len(splitted_line) > 1:
                # если первое часть - число, то имеем дело с обычным спектром, без заголовка
                
                if splitted_line[0].isdigit():
                # if self._return_number_or_false(splitted_line[0]):
                    result['data'] = self.read_csv_spectr(self, file)
                # В противном случае у нас есть заголовки
                else:
                    result = self.read_headed_spectr(self, file)
            # если разделитель так и не нашли, кидаем эксепшн
            else:
                raise TypeError('Не могу определить содержимое спектра')
            
            # Если есть данные темновых пикселей, удаляем из данных усреднённую постоянную составляющую
            if 'BlackPixels' in result and 'SpectrumPixels' in result:
                black_mean = int(sum(result['BlackPixels'].values()) / len(result['BlackPixels']))
                result['data'] = {x: y - black_mean for x, y in result['SpectrumPixels'].items()}
            result['filename'] = filename
            if 'Exposition' not in result:
                result['Exposition'] = 0
            if 'Time' not in result:
                result['Time'] = 0
            result['channel'] = list(result['data'].keys())
            result['values'] = list(result['data'].values())
            
            return ZajSpectr(filename=filename,
                             data=result['values'],
                             channel=result['channel'],
                             exposition=result['Exposition'],
                             time=result['Time'])
                            
                   
'''spectrs = []
reader = ZajSpectrReader()
spectrs.append(reader.return_zai_spectr(r'..\example\20171018_135311_A703OLZX_6.spec'))
spectrs.append(reader.return_zai_spectr(r'C:\py\Projects\Spectr_Viewver\Data\FSR04_calib_110820\6\20200811_11_01_51_837#15_16.asc'))

print(spectrs[1].details)'''