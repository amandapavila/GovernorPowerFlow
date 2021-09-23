import pandas as pd
import sys


class ReadFile:
    """
    Classe para leitura do arquivo de dados elétricos
    """

    def __init__(self):
        # Bloco titu:
        self.titu = dict()
        self.titu['titu'] = list()

        # Bloco dbar:
        self.dbar = dict()
        self.dbar['num'] = list()
        self.dbar['oper'] = list()
        self.dbar['estado'] = list()
        self.dbar['tipo'] = list()
        self.dbar['base_tensao'] = list()
        self.dbar['nome'] = list()
        self.dbar['lim_tensao'] = list()
        self.dbar['tensao'] = list()
        self.dbar['angulo'] = list()
        self.dbar['p'] = list()
        self.dbar['q'] = list()
        self.dbar['q_min'] = list()
        self.dbar['q_max'] = list()
        self.dbar['bar_control'] = list()
        self.dbar['p_load'] = list()
        self.dbar['q_load'] = list()
        self.dbar['capac_reat'] = list()
        self.dbar['area'] = list()
        self.dbar['tensao_load'] = list()
        self.dbar['modo'] = list()
        self.dbar['agreg1'] = list()
        self.dbar['agreg2'] = list()
        self.dbar['agreg3'] = list()
        self.dbar['agreg4'] = list()
        self.dbar['agreg5'] = list()
        self.dbar['agreg6'] = list()
        self.dbar['agreg7'] = list()
        self.dbar['agreg8'] = list()
        self.dbar['agreg9'] = list()
        self.dbar['agreg10'] = list()

        # Bloco dlin:
        self.dlin = dict()
        self.dlin['de'] = list()
        self.dlin['abert_de'] = list()
        self.dlin['oper'] = list()
        self.dlin['abert_para'] = list()
        self.dlin['para'] = list()
        self.dlin['circ'] = list()
        self.dlin['estado'] = list()
        self.dlin['prop'] = list()
        self.dlin['resist'] = list()
        self.dlin['reat'] = list()
        self.dlin['suscep'] = list()
        self.dlin['tap'] = list()
        self.dlin['tap_min'] = list()
        self.dlin['tap_max'] = list()
        self.dlin['defasagem'] = list()
        self.dlin['barra_control'] = list()
        self.dlin['capac_norm'] = list()
        self.dlin['capac_emerg'] = list()
        self.dlin['num_taps'] = list()
        self.dlin['capac_equip'] = list()
        self.dlin['agreg1'] = list()
        self.dlin['agreg2'] = list()
        self.dlin['agreg3'] = list()
        self.dlin['agreg4'] = list()
        self.dlin['agreg5'] = list()
        self.dlin['agreg6'] = list()
        self.dlin['agreg7'] = list()
        self.dlin['agreg8'] = list()
        self.dlin['agreg9'] = list()
        self.dlin['agreg10'] = list()

        # Bloco dger:
        self.dger = dict()
        self.dger['num'] = list()
        self.dger['oper'] = list()
        self.dger['pg_min'] = list()
        self.dger['pg_max'] = list()
        self.dger['fp'] = list()
        self.dger['fpcr'] = list()
        self.dger['fpn'] = list()
        self.dger['fs_ia'] = list()
        self.dger['fs_if'] = list()
        self.dger['ang_load'] = list()
        self.dger['reat_maq'] = list()
        self.dger['s_nom'] = list()
        self.dger['est'] = list()

        # Line counter
        self.count = 0

        # Keywords
        self.end = 'FIM'
        self.end_block = ('9999', '99999')
        self.comment = '('

    def read_file(self, file: str):
        """
        Método para leitura do arquivo de dados elétricos
        :param file: caminho do arquivo de dados elétricos
        :return: DataFrame contendo os dados dos blocos dbar e dlin
        """

        f = open(f'{file}', 'r', encoding='latin-1')
        self.lines = f.readlines()
        f.close()

        while self.lines[self.count].strip() != self.end:

            if self.lines[self.count].strip() == 'TITU':
                self.count += 1
                self.titu['titu'].append(self.lines[self.count])

            elif self.lines[self.count].strip() == 'DBAR':
                self.count += 1
                while self.lines[self.count].strip() not in self.end_block:
                    if self.lines[self.count][0] == self.comment:
                        pass
                    else:
                        self.dbar['num'].append(self.lines[self.count][:5])
                        self.dbar['oper'].append(self.lines[self.count][5])
                        self.dbar['estado'].append(self.lines[self.count][6])
                        self.dbar['tipo'].append(self.lines[self.count][7])
                        self.dbar['base_tensao'].append(self.lines[self.count][8:10])
                        self.dbar['nome'].append(self.lines[self.count][10:22])
                        self.dbar['lim_tensao'].append(self.lines[self.count][22:24])
                        self.dbar['tensao'].append(self.lines[self.count][24:28])
                        self.dbar['angulo'].append(self.lines[self.count][28:32])
                        self.dbar['p'].append(self.lines[self.count][32:37])
                        self.dbar['q'].append(self.lines[self.count][37:42])
                        self.dbar['q_min'].append(self.lines[self.count][42:47])
                        self.dbar['q_max'].append(self.lines[self.count][47:52])
                        self.dbar['bar_control'].append(self.lines[self.count][52:58])
                        self.dbar['p_load'].append(self.lines[self.count][58:63])
                        self.dbar['q_load'].append(self.lines[self.count][63:68])
                        self.dbar['capac_reat'].append(self.lines[self.count][68:73])
                        self.dbar['area'].append(self.lines[self.count][73:76])
                        self.dbar['tensao_load'].append(self.lines[self.count][76:80])
                        self.dbar['modo'].append(self.lines[self.count][80])
                        self.dbar['agreg1'].append(self.lines[self.count][81:84])
                        self.dbar['agreg2'].append(self.lines[self.count][84:87])
                        self.dbar['agreg3'].append(self.lines[self.count][87:90])
                        self.dbar['agreg4'].append(self.lines[self.count][90:93])
                        self.dbar['agreg5'].append(self.lines[self.count][93:96])
                        self.dbar['agreg6'].append(self.lines[self.count][96:99])
                        self.dbar['agreg7'].append(self.lines[self.count][99:102])
                        self.dbar['agreg8'].append(self.lines[self.count][102:105])
                        self.dbar['agreg9'].append(self.lines[self.count][105:108])
                        self.dbar['agreg10'].append(self.lines[self.count][108:111])
                    self.count += 1

            elif self.lines[self.count].strip() == 'DLIN':
                self.count += 1
                while self.lines[self.count].strip() not in self.end_block:
                    if self.lines[self.count][0] == self.comment:
                        pass
                    else:
                        self.dlin['de'].append(self.lines[self.count][:5])
                        self.dlin['abert_de'].append(self.lines[self.count][5])
                        self.dlin['oper'].append(self.lines[self.count][7])
                        self.dlin['abert_para'].append(self.lines[self.count][9])
                        self.dlin['para'].append(self.lines[self.count][10:15])
                        self.dlin['circ'].append(self.lines[self.count][15:17])
                        self.dlin['estado'].append(self.lines[self.count][17])
                        self.dlin['prop'].append(self.lines[self.count][18])
                        self.dlin['resist'].append(self.lines[self.count][20:26])
                        self.dlin['reat'].append(self.lines[self.count][26:32])
                        self.dlin['suscep'].append(self.lines[self.count][32:38])
                        self.dlin['tap'].append(self.lines[self.count][38:43])
                        self.dlin['tap_min'].append(self.lines[self.count][43:48])
                        self.dlin['tap_max'].append(self.lines[self.count][48:53])
                        self.dlin['defasagem'].append(self.lines[self.count][53:58])
                        self.dlin['barra_control'].append(self.lines[self.count][58:64])
                        self.dlin['capac_norm'].append(self.lines[self.count][64:68])
                        self.dlin['capac_emerg'].append(self.lines[self.count][68:72])
                        self.dlin['num_taps'].append(self.lines[self.count][72:74])
                        self.dlin['capac_equip'].append(self.lines[self.count][74:78])
                        self.dlin['agreg1'].append(self.lines[self.count][78:81])
                        self.dlin['agreg2'].append(self.lines[self.count][81:84])
                        self.dlin['agreg3'].append(self.lines[self.count][84:87])
                        self.dlin['agreg4'].append(self.lines[self.count][87:90])
                        self.dlin['agreg5'].append(self.lines[self.count][90:93])
                        self.dlin['agreg6'].append(self.lines[self.count][93:96])
                        self.dlin['agreg7'].append(self.lines[self.count][96:99])
                        self.dlin['agreg8'].append(self.lines[self.count][99:102])
                        self.dlin['agreg9'].append(self.lines[self.count][102:105])
                        self.dlin['agreg10'].append(self.lines[self.count][105:108])
                    self.count += 1

            elif self.lines[self.count].strip() == 'DGER':
                self.count += 1
                while self.lines[self.count].strip() not in self.end_block:
                    if self.lines[self.count][0] == self.comment:
                        pass
                    else:
                        self.dger['num'].append(self.lines[self.count][:5])
                        self.dger['oper'].append(self.lines[self.count][6])
                        self.dger['pg_min'].append(self.lines[self.count][8:14])
                        self.dger['pg_max'].append(self.lines[self.count][15:21])
                        self.dger['fp'].append(self.lines[self.count][22:27])
                        self.dger['fpcr'].append(self.lines[self.count][28:33])
                        self.dger['fpn'].append(self.lines[self.count][34:39])
                        self.dger['fs_ia'].append(self.lines[self.count][40:44])
                        self.dger['fs_if'].append(self.lines[self.count][45:49])
                        self.dger['ang_load'].append(self.lines[self.count][50:54])
                        self.dger['reat_maq'].append(self.lines[self.count][55:60])
                        self.dger['s_nom'].append(self.lines[self.count][61:66])
                        self.dger['est'].append(self.lines[self.count][66:72])
                    self.count += 1

            self.count += 1

        self.dbar_df = pd.DataFrame(data=self.dbar, dtype=float)
        self.dlin_df = pd.DataFrame(data=self.dlin, dtype=float)
        self.dger_df = pd.DataFrame(data=self.dger, dtype=float)

        if self.dbar_df.empty or self.dlin_df.empty:
            print("File reading not done!")
            sys.exit()
        else:
            print("File read successfully!")

        return self.dbar_df, self.dlin_df, self.dger_df
