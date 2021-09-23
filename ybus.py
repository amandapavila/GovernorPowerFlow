from numpy import ndarray
import numpy as np
import pandas as pd


class Ybus:
    """
    Classe para cálculo da matriz Ybus
    """

    def __init__(self, dbar, dlin):

        self.dbar = dbar
        self.dlin = dlin

        # Potência base do sistema (em MVA)
        self.sbase = 100

        # Número de barras do sistema
        self.nbus = int(self.dbar.max()['num'])

        # Inicializa matriz Ybus
        self.ybus: ndarray = np.zeros(shape=[self.nbus, self.nbus], dtype='complex_')

    def calc_ybus(self, file_out=False):
        """
        Método para cálculo dos parâmetros da matriz Ybus
        :param file_out: caminho do arquivo de saída -> .csv contendo a matriz Ybus
        :return: Matriz Ybus
        """

        # Data conversion
        self.dlin['de'] = self.dlin.de.astype(dtype='int', copy=False)
        self.dlin['para'] = self.dlin.para.astype(dtype='int', copy=False)
        self.dbar['num'] = self.dbar.num.astype(dtype='int', copy=False)

        # Linhas de transmissão e transformadores
        for idx, value in self.dlin.iterrows():

            # Elementos fora da diagonal (elemento série)
            if value['tap'].strip() == '':
                self.ybus[value['de'] - 1, value['para'] - 1] -= (1 / complex(real=value['resist'],
                                                                              imag=value['reat'])) * self.sbase
                self.ybus[value['para'] - 1, value['de'] - 1] -= (1 / complex(real=value['resist'],
                                                                              imag=value['reat'])) * self.sbase
            else:
                self.ybus[value['de'] - 1, value['para'] - 1] -= (1 / complex(real=value['resist'],
                                                                              imag=value['reat'])) * self.sbase \
                                                                 / float(value['tap'])
                self.ybus[value['para'] - 1, value['de'] - 1] -= (1 / complex(real=value['resist'],
                                                                              imag=value['reat'])) * self.sbase \
                                                                 / float(value['tap'])

            # Elementos na diagonal (elemento série)
            if value['tap'].strip() == '':
                self.ybus[value['de'] - 1, value['de'] - 1] += (1 / complex(real=value['resist'], imag=value['reat'])) \
                                                               * self.sbase
            else:
                self.ybus[value['de'] - 1, value['de'] - 1] += (1 / complex(real=value['resist'], imag=value['reat'])) \
                                                               * self.sbase / float(value['tap']) ** 2

            self.ybus[value['para'] - 1, value['para'] - 1] += (1 / complex(real=value['resist'], imag=value['reat'])) \
                                                               * self.sbase

            # Elementos na diagonal (elemento shunt)
            if value['suscep'].strip() == '':
                pass
            else:
                self.ybus[value['de'] - 1, value['de'] - 1] += complex(real=0., imag=float(value['suscep'])
                                                                                     / (2 * self.sbase))

                self.ybus[value['para'] - 1, value['para'] - 1] += complex(real=0., imag=float(value['suscep'])
                                                                                         / (2 * self.sbase))
        # Bancos de capacitores e reatores
        for idx, value in self.dbar.iterrows():
            # Elementos na diagonal (elemento shunt)
            if value['capac_reat'].strip() == '':
                pass
            else:
                self.ybus[value['num'] - 1, value['num'] - 1] += complex(real=0., imag=float(value['capac_reat'])
                                                                                       / self.sbase)

        if file_out:
            pd.DataFrame(self.ybus).to_csv(f'{file_out}ybus.csv', header=None, index=None, sep=',')

        return self.ybus
