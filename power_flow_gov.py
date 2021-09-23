import numpy as np
import plotly.graph_objects as go


class PowerFlowControl:
    """
    Classe para cálculo do fluxo de potência com Regulação Primária de acordo com método de Newton-Raphson
    """

    def __init__(self, dbar, dlin, dger, ybus, delta):
        self.dbar = dbar
        self.dlin = dlin
        self.dger = dger
        self.ybus = ybus

        # Número de barras do sistema
        self.nbus = int(dbar.max()['num'])

        # Potência base do sistema (em MVA)
        self.sbase = 100

        # Iteration counter
        self.iter = 0
        self.iter_max = 10

        # Tolerance
        self.e = 1e-6

        # Número de geradores do sistema
        self.nger = self.dger.shape[0]

        # Número de áreas (ilhas elétricas)
        self.nare = 1

        # Dimensão da Jacobiana
        self.dim = 2 * self.nbus + 2 * self.nger + self.nare

        # Frequência base
        self.fbase = 60

        # Frequência especificada
        self.fesp = 1

        # Dicionário para armazenar a solução inicial
        self.sol = {
            'voltage': np.array(self.dbar['tensao'] * 1e-3),
            'theta': np.array(np.radians(self.dbar['angulo'])),
            'pg': np.zeros(self.nger),
            'qg': np.zeros(self.nger),
            'f': 1.
        }

        ng = 0
        for idx, value in self.dbar.iterrows():
            if value['tipo'].strip() == '':
                pass
            else:
                self.sol['pg'][ng] = float(value['p'])
                self.sol['qg'][ng] = float(value['q'])
                ng += 1

        self.sol['pg'] /= self.sbase
        self.sol['qg'] /= self.sbase

        self.delta = 1 + delta * 1e-2

    def freq_ger(self):
        """
        Método para cálculo das frequências máximas e mínimas de operação de cada gerador
        :return: Dicionário com as frequências máximas e mínimas a serem utilizadas no tratamento de limites de potência
         ativa
        """

        self.freq_g = {
            'max': np.zeros(self.nger),
            'min': np.zeros(self.nger)
        }

        for idx, value in self.dger.iterrows():
            self.freq_g['max'][idx] = self.fesp + float(value['est']) * 1e-2 * \
                                      (float(self.dbar['p'][int(value['num']) - 1]) - float(value['pg_min'])) \
                                      / self.sbase

            self.freq_g['min'][idx] = self.fesp + float(value['est']) * 1e-2 * \
                                      (float(self.dbar['p'][int(value['num']) - 1]) - float(value['pg_max'])) \
                                      / self.sbase

    def value_spec(self):
        """
        Método para armazenamento de parâmetros especificados
        :return: Dicionário com valores especificados para cada parâmetro
        """

        self.value_esp = {
            'tipo': np.zeros(self.nbus),
            'p_esp': np.zeros(self.nbus),
            'q_esp': np.zeros(self.nbus),
            'pg_esp': np.zeros(self.nger),
            'qg_esp': np.zeros(self.nger),
            'v_esp': np.zeros(self.nbus),
            'theta_esp': np.zeros(self.nbus)
        }

        ng = 0

        for idx, value in self.dbar.iterrows():

            # Tipo de barra
            if value['tipo'].strip() == '':
                # Valor default '' ou 0 - Barra PQ
                self.value_esp['tipo'][idx] = 0
            else:
                # Barra PV e VTheta
                self.value_esp['tipo'][idx] = int(value['tipo'])

                # Potência ativa gerada
                self.value_esp['pg_esp'][ng] = float(value['p'])

                # Potência reativa gerada
                self.value_esp['qg_esp'][ng] = float(value['q'])

                # Incrementa contador
                ng += 1

            # Potência ativa
            if value['p'].strip() == '':
                self.value_esp['p_esp'][idx] += 0.
            else:
                self.value_esp['p_esp'][idx] += float(value['p'])

            if value['p_load'].strip() == '':
                self.value_esp['p_esp'][idx] -= 0.
            else:
                self.value_esp['p_esp'][idx] -= float(value['p_load']) * self.delta

            # Potência reativa
            if value['q'].strip() == '':
                self.value_esp['q_esp'][idx] += 0.
            else:
                self.value_esp['q_esp'][idx] += float(value['q'])

            if value['q_load'].strip() == '':
                self.value_esp['q_esp'][idx] -= 0.
            else:
                self.value_esp['q_esp'][idx] -= float(value['q_load']) * self.delta

            if value['tipo'].strip() == '':
                pass
            else:
                self.value_esp['v_esp'][idx] = float(value['tensao']) * 1e-3

                if value['tipo'].strip() == '2':
                    self.value_esp['theta_esp'][idx] = np.radians(float(value['angulo']))
                else:
                    pass

        self.value_esp['p_esp'] /= self.sbase
        self.value_esp['q_esp'] /= self.sbase
        self.value_esp['pg_esp'] /= self.sbase
        self.value_esp['qg_esp'] /= self.sbase

    def calc_p(self, bar):
        """
        Método para cálculo da potência ativa na barra bar
        :param bar: Número da barra
        :return: Potência ativa na barra
        """

        p = 0.

        for idx in range(self.nbus):
            p += self.sol['voltage'][idx] * \
                 (self.ybus[bar][idx].real * np.cos(self.sol['theta'][bar] - self.sol['theta'][idx]) +
                  self.ybus[bar][idx].imag * np.sin(self.sol['theta'][bar] - self.sol['theta'][idx]))

        p *= self.sol['voltage'][bar]

        return p

    def calc_q(self, bar):
        """
        Método para cálculo da potência reativa na barra bar
        :param bar: Número da barra
        :return: Potência reativa na barra
        """

        q = 0.

        for idx in range(self.nbus):
            q += self.sol['voltage'][idx] * \
                 (self.ybus[bar][idx].real * np.sin(self.sol['theta'][bar] - self.sol['theta'][idx]) -
                  self.ybus[bar][idx].imag * np.cos(self.sol['theta'][bar] - self.sol['theta'][idx]))

        q *= self.sol['voltage'][bar]

        return q

    def jacobiana(self):
        """
        Método para cálculo da matriz Jacobiana Expandida
        :return: Matriz Jacobiana
        """

        # Submatrizes da matriz jacobiana
        self.h = np.zeros([self.nbus, self.nbus])
        self.n = np.zeros([self.nbus, self.nbus])
        self.m = np.zeros([self.nbus, self.nbus])
        self.l = np.zeros([self.nbus, self.nbus])

        for idx in range(self.nbus):
            for idy in range(self.nbus):
                if idx is idy:
                    # Elemento Hkk
                    self.h[idx, idy] += (-self.sol['voltage'][idx] ** 2) * self.ybus[idx][idy].imag - self.calc_q(idx)

                    # Elemento Nkk
                    self.n[idx, idy] += (self.calc_p(idx) + self.sol['voltage'][idx] ** 2 * self.ybus[idx][idy].real) \
                                        / self.sol['voltage'][idx]

                    # Elemento Mkk
                    self.m[idx, idy] += self.calc_p(idx) - (self.sol['voltage'][idx] ** 2) * self.ybus[idx][idy].real

                    # Elemento Lkk
                    self.l[idx, idy] += (self.calc_q(idx) - self.sol['voltage'][idx] ** 2 * self.ybus[idx][idy].imag) \
                                        / self.sol['voltage'][idx]
                else:
                    # Elemento Hkm
                    self.h[idx, idy] += self.sol['voltage'][idx] * self.sol['voltage'][idy] * (
                            self.ybus[idx][idy].real * np.sin(self.sol['theta'][idx] - self.sol['theta'][idy]) -
                            self.ybus[idx][idy].imag * np.cos(self.sol['theta'][idx] - self.sol['theta'][idy]))

                    # Elemento Nkm
                    self.n[idx, idy] += self.sol['voltage'][idx] * (
                            self.ybus[idx][idy].real * np.cos(self.sol['theta'][idx] - self.sol['theta'][idy]) +
                            self.ybus[idx][idy].imag * np.sin(self.sol['theta'][idx] - self.sol['theta'][idy]))

                    # Elemento Mkm
                    self.m[idx, idy] -= self.sol['voltage'][idx] * self.sol['voltage'][idy] * (
                            self.ybus[idx][idy].real * np.cos(self.sol['theta'][idx] - self.sol['theta'][idy]) +
                            self.ybus[idx][idy].imag * np.sin(self.sol['theta'][idx] - self.sol['theta'][idy]))

                    # Elemento Lkm
                    self.l[idx, idy] += self.sol['voltage'][idx] * (
                            self.ybus[idx][idy].real * np.sin(self.sol['theta'][idx] - self.sol['theta'][idy]) -
                            self.ybus[idx][idy].imag * np.cos(self.sol['theta'][idx] - self.sol['theta'][idy]))

        self.jacob = np.concatenate((self.h, self.m, np.zeros([2 * self.nger, self.nbus]), self.ft))
        self.jacob = np.concatenate((self.jacob, np.concatenate((self.n, self.l, np.zeros([self.nger, self.nbus]),
                                                                 self.eqg, np.zeros([self.nare, self.nbus])))), axis=1)
        self.jacob = np.concatenate((self.jacob, np.concatenate((self.apg, np.zeros([self.nbus, self.nger]), self.cpg,
                                                                 np.zeros([self.nger + self.nare, self.nger])))), axis=1
                                    )
        self.jacob = np.concatenate((self.jacob, np.concatenate((np.zeros([self.nbus, self.nger]), self.bqg,
                                                                 np.zeros([2 * self.nger + self.nare, self.nger])))),
                                    axis=1)
        self.jacob = np.concatenate((self.jacob, np.concatenate((np.zeros([2 * self.nbus, self.nare]), self.cf,
                                                                 np.zeros([self.nger + self.nare, self.nare])))),
                                    axis=1)

    def jacobiana_exp(self):
        """
        Método para cálculo das submatrizes da Jacobiana Expandida
        :return: Submatrizes
        """

        self.apg = np.zeros([self.nbus, self.nger])
        self.bqg = np.zeros([self.nbus, self.nger])
        self.cpg = np.zeros([self.nger, self.nger])
        self.cf = np.zeros([self.nger, self.nare])
        self.eqg = np.zeros([self.nger, self.nbus])
        self.ft = np.zeros([self.nare, self.nbus])

        ng = 0
        na = 0

        for idx in range(self.nbus):
            if self.dbar['tipo'][idx].strip() == '':
                pass
            else:
                self.apg[idx, ng] = -1.
                self.bqg[idx, ng] = -1.
                self.eqg[ng, idx] = 1.
                ng += 1

                if self.dbar['tipo'][idx].strip() == '2':
                    self.ft[na, idx] = 1.
                else:
                    pass

        for idy in range(self.nger):
            self.cpg[idy, idy] = 1.
            self.cf[idy, na] = 1. / (float(self.dger['est'][idy]) * 1e-2)

    def calc_res(self):
        """
        Método para cálculo dos resíduos
        :return: Resíduos (deltaP, deltaQ, deltaY, deltaW, deltaZ)
        """

        # Vetor de residuos
        self.deltaP = np.zeros(self.nbus)
        self.deltaQ = np.zeros(self.nbus)
        self.deltaY = np.zeros(self.nger)
        self.deltaW = np.zeros(self.nger)
        self.deltaZ = np.zeros(self.nare)

        ng = 0
        for idx, value in self.dbar.iterrows():

            if value['tipo'].strip() == '':
                self.deltaP[idx] += self.value_esp['p_esp'][idx]
                self.deltaP[idx] -= self.calc_p(idx)

                self.deltaQ[idx] += self.value_esp['q_esp'][idx]
                self.deltaQ[idx] -= self.calc_q(idx)
            else:
                # Cálculo do resíduo DeltaP
                self.deltaP[idx] += self.sol['pg'][ng]

                if value['p_load'].strip() == '':
                    self.deltaP[idx] -= 0.
                else:
                    self.deltaP[idx] -= float(value['p_load']) * self.delta / self.sbase

                self.deltaP[idx] -= self.calc_p(idx)

                # Cálculo do resíduo DeltaQ
                self.deltaQ[idx] += self.sol['qg'][ng]

                if value['q_load'].strip() == '':
                    self.deltaQ[idx] -= 0.
                else:
                    self.deltaQ[idx] -= float(value['q_load']) * self.delta / self.sbase

                self.deltaQ[idx] -= self.calc_q(idx)

                # Cálculo do resíduo DeltaY
                # Tratamento de limite de potência ativa
                if self.sol['f'] >= self.freq_g['max'][ng] or self.sol['f'] <= self.freq_g['min'][ng]:
                    self.deltaY[ng] = 0.
                else:
                    self.deltaY[ng] += self.value_esp['pg_esp'][ng]
                    self.deltaY[ng] -= self.sol['pg'][ng]
                    self.deltaY[ng] -= (1 / (float(self.dger['est'][ng]) * 1e-2)) * (self.sol['f'] - self.fesp)

                # Cálculo do resíduo DeltaW
                self.deltaW[ng] += self.value_esp['v_esp'][idx]
                self.deltaW[ng] -= self.sol['voltage'][idx]

                if value['tipo'].strip() == '2':
                    self.deltaZ += self.value_esp['theta_esp'][idx]
                    self.deltaZ -= self.sol['theta'][idx]

                ng += 1

        self.res = np.concatenate((self.deltaP, self.deltaQ, self.deltaY, self.deltaW, self.deltaZ))

    def update_state_variables(self):
        """
        Método para atualização das variáveis de estado
        :return: Variáveis de estado atualizadas
        """

        self.sol['theta'] += self.state_variables[0:self.nbus]

        self.sol['voltage'] += self.state_variables[self.nbus:(2 * self.nbus)]

        self.sol['pg'] += self.state_variables[(2 * self.nbus):(2 * self.nbus + self.nger)]

        # Tratamento de limite de potência ativa
        for idx, value in enumerate(self.sol['pg']):
            if self.sol['f'] >= self.freq_g['max'][idx]:
                self.sol['pg'][idx] = float(self.dger['pg_min'][idx]) / self.sbase
                self.cpg[idx][idx] = np.infty

            elif self.sol['f'] <= self.freq_g['min'][idx]:
                self.sol['pg'][idx] = float(self.dger['pg_max'][idx]) / self.sbase
                self.cpg[idx][idx] = np.infty

            else:
                self.cpg[idx][idx] = 1.

        self.sol['qg'] += self.state_variables[(2 * self.nbus + self.nger):(2 * self.nbus + 2 * self.nger)]

        self.sol['f'] += self.state_variables[-1]

    def flow(self):
        """
        Método para cálculo do fluxo de potência nas linhas de transmissão
        :return: Potência ativa e reativa em cada linha de transmissão
        """

        self.power_flow = {
            'de': self.dlin['de'],
            'para': self.dlin['para'],
            'flow_p': np.zeros(len(self.dlin['de'])),
            'flow_q': np.zeros(len(self.dlin['de']))
        }

        for idx, value in self.dlin.iterrows():
            self.power_flow['flow_p'][idx] += self.calc_p(value['de'] - 1) * self.sbase
            self.power_flow['flow_p'][idx] -= self.calc_p(value['para'] - 1) * self.sbase

            self.power_flow['flow_q'][idx] += self.calc_q(value['de'] - 1) * self.sbase
            self.power_flow['flow_q'][idx] -= self.calc_q(value['para'] - 1) * self.sbase

    def result(self, imprime=False):
        """
        Método para impressão em forma de tabela das tensões e ângulos nas barras e do fluxo de potência nas linhas
        :param imprime: Recebe False (para não imprimir) ou True (para imprimir) -> Default: False
        :return: Impressão de resultados na tela em forma de tabela
        """

        headerColor = 'grey'
        rowEvenColor = 'lightgrey'
        rowOddColor = 'white'

        if imprime:
            fig = go.Figure(data=[go.Table(header=dict(values=['<b>BARRA</b>', '<b>TENSÃO</b>', '<b>ÂNGULO</b>'],
                                                       line_color='darkslategray',
                                                       fill_color=headerColor, align='center',
                                                       font=dict(color='white', size=14)
                                                       ),
                                           cells=dict(values=[np.arange(start=1, step=1, stop=self.nbus + 1),
                                                              np.round(self.sol['voltage'], decimals=3),
                                                              np.round(np.rad2deg(self.sol['theta']), decimals=1)],
                                                      fill_color=[[rowEvenColor, rowOddColor]
                                                                  * self.nbus],
                                                      align='center',
                                                      font=dict(color='darkslategray', size=14),
                                                      height=40
                                                      ))
                                  ])
            fig.update_layout(title={'text': '<b>RESULTS</b>'},
                              font={'family': 'Times New Roman', 'size': 20, 'color': 'grey'})
            fig.show()

            self.flow()

            fig = go.Figure(data=[go.Table(header=dict(values=['<b>BARRA DE</b>', '<b>BARRA PARA</b>',
                                                               '<b>POTÊNCIA ATIVA</b>', '<b>POTÊNCIA REATIVA<b>'],
                                                       line_color='darkslategray',
                                                       fill_color=headerColor, align='center',
                                                       font=dict(color='white', size=14)
                                                       ),
                                           cells=dict(values=[self.power_flow['de'], self.power_flow['para'],
                                                              np.round(self.power_flow['flow_p'], decimals=2),
                                                              np.round(self.power_flow['flow_q'], decimals=2)],
                                                      fill_color=[[rowEvenColor, rowOddColor]
                                                                  * len(self.power_flow['de'])],
                                                      align='center',
                                                      font=dict(color='darkslategray', size=14),
                                                      height=40
                                                      ))
                                  ])
            fig.update_layout(title={'text': '<b>RESULTS - POWER FLOW</b>'},
                              font={'family': 'Times New Roman', 'size': 20, 'color': 'grey'})
            fig.show()

    def newton_control(self, imprime=True):
        """
        Método de Newton-Raphson
        :return: Fluxo de potência com Regulação Primária
        """

        # Método de frequências mínima e máxima dos geradores
        self.freq_ger()

        # Método de valores especificados
        self.value_spec()

        # Método de submatrizes da Jacobiana Expandida
        self.jacobiana_exp()

        # Cálculo de resíduos para primeira iteração
        self.calc_res()

        while np.max(np.abs(self.res)) > self.e:
            # Se não convergiu
            # Incrementa contador de iteracoes
            self.iter += 1

            # Atualiza matriz jacobiana
            self.jacobiana()

            # Resolve problema de programacao linear
            self.state_variables = np.linalg.solve(self.jacob, self.res)

            # Atualiza variaveis de estado
            self.update_state_variables()

            # Calcula residuos
            self.calc_res()

            if self.iter > self.iter_max:
                break

        if imprime:
            self.result(imprime=True)
            print('-------------------------------------------------------------------------------------------------\n')
            print(f"FREQUÊNCIA DO SISTEMA: {round(self.sol['f'] * self.fbase, 3)}Hz\n")
            print('-------------------------------------------------------------------------------------------------\n')
            print('BARRA     PG (MW)     QG (Mvar)')
            for idx, value in self.dger.iterrows():
                print(f"{value['num']:2.0f}         {(self.sol['pg'][idx] * self.sbase):3.2f}       "
                      f"{(self.sol['qg'][idx] * self.sbase):3.2f}")

        return self.sol
