from read_file import ReadFile
from ybus import Ybus
from power_flow_gov import PowerFlowControl
import os

file = os.path.join('IEEE 24 Barras FREQ.pwf')

dbar, dlin, dger = ReadFile().read_file(file)

ybus = Ybus(dbar=dbar, dlin=dlin).calc_ybus()

# Aumento/redução de carga desejada em todas as barras do sistema
deltaLoad = -10.

pf_sol = PowerFlowControl(dbar, dlin, dger, ybus, deltaLoad).newton_control()
