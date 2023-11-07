import copy
import os
from collections import defaultdict
from typing import Dict

import joblib
import pandas as pd
import ast
from tqdm import tqdm
import numpy as np


def to_hand_str(cluster: int) -> str:
    return f"hand_cluster_{cluster}"

def calculate_strategy(this_info_sets_regret: Dict[str, float]) -> Dict[str, float]:
    """Calculate the strategy based on the current information sets regret."""
    # TODO: Could we instanciate a state object from an info set?
    actions = this_info_sets_regret.keys()
    regret_sum = sum([max(regret, 0) for regret in this_info_sets_regret.values()])
    if regret_sum > 0:
        strategy: Dict[str, float] = {
            action: max(this_info_sets_regret[action], 0) / regret_sum
            for action in actions
        }
    else:
        default_probability = 1 / len(actions)
        strategy: Dict[str, float] = {action: default_probability for action in actions}
    return strategy

def write_to_dict(key_p, dict_p, value_p):
    cluster = ast.literal_eval(key_p)["cards_cluster"]
    bucket = dict_p.get(cluster)
    if bucket is None:
        dict_p[ast.literal_eval(key_p)["cards_cluster"]] = copy.deepcopy(value_p)
    else:
        dict_p[ast.literal_eval(key_p)["cards_cluster"]]["fold"] += copy.deepcopy(value_p["fold"])
        dict_p[ast.literal_eval(key_p)["cards_cluster"]]["allin"] += copy.deepcopy(value_p["allin"])
        
def write_to_dict_v2(key_p, dict_p, value_p):
    cluster = ast.literal_eval(key_p)["cards_cluster"]
    bucket = dict_p.get(cluster)
    if bucket is None:
        dict_p[ast.literal_eval(key_p)["cards_cluster"]] =  {
            "allin":copy.deepcopy(value_p)
        }
    else:
        dict_p[ast.literal_eval(key_p)["cards_cluster"]]["allin"] += copy.deepcopy(value_p)

#realblind_2020_06_23_01_57_29_311329 = big jackpot?
#realblindsmalljackpot_2020_06_23_13_50_32_940205 = small jackpot?

strategy_path = "../../poker_ai/ai/bronze_705_newev_2020_07_13_02_30_02_454747/agent.joblib"
dag_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
data = joblib.load(strategy_path)
sorted_ragret = sorted (data["regret"].items())
sorted_strat = sorted (data["strategy"].items())
sorted_ev = sorted (data["ev"].items())


# for (key,value) in data["regret"].items():
#     if value["allin"] > 0. and value["allin"] < 400. and value["fold"] > 0. and value["fold"] < -400.:
#         print(str(key) + str(value))

# for item in sorted_ragret:
#     print(item)

ignore_history : Dict[str,Dict] = {}
utg_strat : Dict[str,Dict] = {}
fold_strat : Dict[str,Dict] = {}
call_strat : Dict[str,Dict] = {}
foldfold_strat : Dict[str,Dict] = {}
foldcall_strat : Dict[str,Dict] = {}
callfold_strat : Dict[str,Dict] = {}
callcall_strat : Dict[str,Dict] = {}
callfoldfold_strat : Dict[str,Dict] = {}
callcallfold_strat : Dict[str,Dict] = {}
callcallcall_strat : Dict[str,Dict] = {}
callfoldcall_strat : Dict[str,Dict] = {}
foldfoldcall_strat : Dict[str,Dict] = {}
foldcallcall_strat : Dict[str,Dict] = {}
foldcallfold_strat : Dict[str,Dict] = {}

utg_regret : Dict[str,Dict] = {}
fold_regret : Dict[str,Dict] = {}
call_regret : Dict[str,Dict] = {}
foldfold_regret : Dict[str,Dict] = {}
foldcall_regret : Dict[str,Dict] = {}
callfold_regret : Dict[str,Dict] = {}
callcall_regret : Dict[str,Dict] = {}
callfoldfold_regret : Dict[str,Dict] = {}
callcallfold_regret : Dict[str,Dict] = {}
callcallcall_regret : Dict[str,Dict] = {}
callfoldcall_regret : Dict[str,Dict] = {}
foldfoldcall_regret : Dict[str,Dict] = {}
foldcallcall_regret : Dict[str,Dict] = {}
foldcallfold_regret : Dict[str,Dict] = {}

utg_ev : Dict[str,Dict] = {}
fold_ev : Dict[str,Dict] = {}
call_ev : Dict[str,Dict] = {}
foldfold_ev : Dict[str,Dict] = {}
foldcall_ev : Dict[str,Dict] = {}
callfold_ev : Dict[str,Dict] = {}
callcall_ev : Dict[str,Dict] = {}
callfoldfold_ev : Dict[str,Dict] = {}
callcallfold_ev : Dict[str,Dict] = {}
callcallcall_ev : Dict[str,Dict] = {}
callfoldcall_ev : Dict[str,Dict] = {}
foldfoldcall_ev : Dict[str,Dict] = {}
foldcallcall_ev : Dict[str,Dict] = {}
foldcallfold_ev : Dict[str,Dict] = {}
# Iterate over all the items in dictionary and filter items which has even keys
for (key, value) in data["strategy"].items():
    write_to_dict(key, ignore_history, value)

    if ast.literal_eval(key)["history"] == []:
        write_to_dict(key,utg_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold"]}]:
        write_to_dict(key,fold_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call"]}]:
        write_to_dict(key,call_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","fold"]}]:
        write_to_dict(key,foldfold_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call"]}]:
        write_to_dict(key,foldcall_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold"]}]:
        write_to_dict(key,callfold_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call"]}]:
        write_to_dict(key,callcall_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold","fold"]}]:
        write_to_dict(key,callfoldfold_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call","fold"]}]:
        write_to_dict(key,callcallfold_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call","call"]}]:
        write_to_dict(key,callcallcall_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold","call"]}]:
        write_to_dict(key,callfoldcall_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","fold","call"]}]:
        write_to_dict(key,foldfoldcall_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call","call"]}]:
        write_to_dict(key,foldcallcall_strat,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call","fold"]}]:
        write_to_dict(key,foldcallfold_strat,value)
         
for (key, value) in data["regret"].items():
    value = calculate_strategy(value)

    if ast.literal_eval(key)["history"] == []:
        write_to_dict(key,utg_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold"]}]:
        write_to_dict(key,fold_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call"]}]:
        write_to_dict(key,call_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","fold"]}]:
        write_to_dict(key,foldfold_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call"]}]:
        write_to_dict(key,foldcall_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold"]}]:
        write_to_dict(key,callfold_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call"]}]:
        write_to_dict(key,callcall_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold","fold"]}]:
        write_to_dict(key,callfoldfold_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call","fold"]}]:
        write_to_dict(key,callcallfold_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call","call"]}]:
        write_to_dict(key,callcallcall_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold","call"]}]:
        write_to_dict(key,callfoldcall_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","fold","call"]}]:
        write_to_dict(key,foldfoldcall_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call","call"]}]:
        write_to_dict(key,foldcallcall_regret,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call","fold"]}]:
        write_to_dict(key,foldcallfold_regret,value)
        
for (key, value) in data["ev"].items():
    value = (value[0] / value[2])

    if ast.literal_eval(key)["history"] == []:
        write_to_dict_v2(key,utg_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold"]}]:
        write_to_dict_v2(key,fold_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call"]}]:
        write_to_dict_v2(key,call_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","fold"]}]:
        write_to_dict_v2(key,foldfold_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call"]}]:
        write_to_dict_v2(key,foldcall_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold"]}]:
        write_to_dict_v2(key,callfold_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call"]}]:
        write_to_dict_v2(key,callcall_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold","fold"]}]:
        write_to_dict_v2(key,callfoldfold_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call","fold"]}]:
        write_to_dict_v2(key,callcallfold_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","call","call"]}]:
        write_to_dict_v2(key,callcallcall_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["call","fold","call"]}]:
        write_to_dict_v2(key,callfoldcall_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","fold","call"]}]:
        write_to_dict_v2(key,foldfoldcall_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call","call"]}]:
        write_to_dict_v2(key,foldcallcall_ev,value)
    if ast.literal_eval(key)["history"] == [{"pre_flop":["fold","call","fold"]}]:
        write_to_dict_v2(key,foldcallfold_ev,value)


# ev : Dict[str,Dict] = {}
# ev_count : Dict[str,Dict] = {}
# for i in sorted_ev:
#     print(i)

# for (key, value) in ignore_history.items():
#     ignore_history[key]["fold"] /= 14
#     ignore_history[key]["allin"] /= 14

doing_column = True
average_grid = np.zeros([13,13])
utg_strat_grid = np.zeros([13,13])
fold_strat_grid = np.zeros([13,13])
call_strat_grid = np.zeros([13,13])
foldfold_strat_grid = np.zeros([13,13])
foldcall_strat_grid = np.zeros([13,13])
callfold_strat_grid = np.zeros([13,13])
callcall_strat_grid = np.zeros([13,13])
callfoldfold_strat_grid = np.zeros([13,13])
callcallfold_strat_grid = np.zeros([13,13])
callcallcall_strat_grid = np.zeros([13,13])
callfoldcall_strat_grid = np.zeros([13,13])
foldfoldcall_strat_grid = np.zeros([13,13])
foldcallcall_strat_grid = np.zeros([13,13])
foldcallfold_strat_grid = np.zeros([13,13])

utg_regret_grid = np.zeros([13,13])
fold_regret_grid = np.zeros([13,13])
call_regret_grid = np.zeros([13,13])
foldfold_regret_grid = np.zeros([13,13])
foldcall_regret_grid = np.zeros([13,13])
callfold_regret_grid = np.zeros([13,13])
callcall_regret_grid = np.zeros([13,13])
callfoldfold_regret_grid = np.zeros([13,13])
callcallfold_regret_grid = np.zeros([13,13])
callcallcall_regret_grid = np.zeros([13,13])
callfoldcall_regret_grid = np.zeros([13,13])
foldfoldcall_regret_grid = np.zeros([13,13])
foldcallcall_regret_grid = np.zeros([13,13])
foldcallfold_regret_grid = np.zeros([13,13])

utg_ev_grid = np.zeros([13,13])
fold_ev_grid = np.zeros([13,13])
call_ev_grid = np.zeros([13,13])
foldfold_ev_grid = np.zeros([13,13])
foldcall_ev_grid = np.zeros([13,13])
callfold_ev_grid = np.zeros([13,13])
callcall_ev_grid = np.zeros([13,13])
callfoldfold_ev_grid = np.zeros([13,13])
callcallfold_ev_grid = np.zeros([13,13])
callcallcall_ev_grid = np.zeros([13,13])
callfoldcall_ev_grid = np.zeros([13,13])
foldfoldcall_ev_grid = np.zeros([13,13])
foldcallcall_ev_grid = np.zeros([13,13])
foldcallfold_ev_grid = np.zeros([13,13])

column_index = 11
row_index = 12
i = 0
while(i < 169):
    if doing_column:
        column = copy.deepcopy(column_index+1)
        for y in range(column_index, -1 ,-1):
            average_grid.itemset((y, column), ignore_history[i]["allin"])
            utg_strat_grid.itemset((y, column), utg_strat[i]["allin"])
            fold_strat_grid.itemset((y, column), fold_strat[i]["allin"])
            call_strat_grid.itemset((y, column), call_strat[i]["allin"])
            foldfold_strat_grid.itemset((y, column), foldfold_strat[i]["allin"])
            foldcall_strat_grid.itemset((y, column), foldcall_strat[i]["allin"])
            callfold_strat_grid.itemset((y, column), callfold_strat[i]["allin"])
            callcall_strat_grid.itemset((y, column), callcall_strat[i]["allin"])
            callfoldfold_strat_grid.itemset((y, column), callfoldfold_strat[i]["allin"])
            callcallfold_strat_grid.itemset((y, column), callcallfold_strat[i]["allin"])
            callcallcall_strat_grid.itemset((y, column), callcallcall_strat[i]["allin"])
            callfoldcall_strat_grid.itemset((y, column), callfoldcall_strat[i]["allin"])
            foldfoldcall_strat_grid.itemset((y, column), foldfoldcall_strat[i]["allin"])
            foldcallcall_strat_grid.itemset((y, column), foldcallcall_strat[i]["allin"])
            foldcallfold_strat_grid.itemset((y, column), foldcallfold_strat[i]["allin"])

            utg_regret_grid.itemset((y, column), utg_regret[i]["allin"])
            fold_regret_grid.itemset((y, column), fold_regret[i]["allin"])
            call_regret_grid.itemset((y, column), call_regret[i]["allin"])
            foldfold_regret_grid.itemset((y, column), foldfold_regret[i]["allin"])
            foldcall_regret_grid.itemset((y, column), foldcall_regret[i]["allin"])
            callfold_regret_grid.itemset((y, column), callfold_regret[i]["allin"])
            callcall_regret_grid.itemset((y, column), callcall_regret[i]["allin"])
            callfoldfold_regret_grid.itemset((y, column), callfoldfold_regret[i]["allin"])
            callcallfold_regret_grid.itemset((y, column), callcallfold_regret[i]["allin"])
            callcallcall_regret_grid.itemset((y, column), callcallcall_regret[i]["allin"])
            callfoldcall_regret_grid.itemset((y, column), callfoldcall_regret[i]["allin"])
            foldfoldcall_regret_grid.itemset((y, column), foldfoldcall_regret[i]["allin"])
            foldcallcall_regret_grid.itemset((y, column), foldcallcall_regret[i]["allin"])
            foldcallfold_regret_grid.itemset((y, column), foldcallfold_regret[i]["allin"])

            utg_ev_grid.itemset((y, column), utg_ev[i]["allin"])
            fold_ev_grid.itemset((y, column), fold_ev[i]["allin"])
            call_ev_grid.itemset((y, column), call_ev[i]["allin"])
            foldfold_ev_grid.itemset((y, column), foldfold_ev[i]["allin"])
            foldcall_ev_grid.itemset((y, column), foldcall_ev[i]["allin"])
            callfold_ev_grid.itemset((y, column), callfold_ev[i]["allin"])
            callcall_ev_grid.itemset((y, column), callcall_ev[i]["allin"])
            callfoldfold_ev_grid.itemset((y, column), callfoldfold_ev[i]["allin"])
            callcallfold_ev_grid.itemset((y, column), callcallfold_ev[i]["allin"])
            callcallcall_ev_grid.itemset((y, column), callcallcall_ev[i]["allin"])
            callfoldcall_ev_grid.itemset((y, column), callfoldcall_ev[i]["allin"])
            foldfoldcall_ev_grid.itemset((y, column), foldfoldcall_ev[i]["allin"])
            foldcallcall_ev_grid.itemset((y, column), foldcallcall_ev[i]["allin"])
            foldcallfold_ev_grid.itemset((y, column), foldcallfold_ev[i]["allin"])
            
            i += 1
        column_index -= 1
        doing_column = False
        continue
    else:
        row = copy.deepcopy(row_index)
        for y in range(row_index, -1, -1):
            average_grid.itemset((row, y), ignore_history[i]["allin"])
            utg_strat_grid.itemset((row, y), utg_strat[i]["allin"])
            fold_strat_grid.itemset((row, y), fold_strat[i]["allin"])
            call_strat_grid.itemset((row, y), call_strat[i]["allin"])
            foldfold_strat_grid.itemset((row, y), foldfold_strat[i]["allin"])
            foldcall_strat_grid.itemset((row, y), foldcall_strat[i]["allin"])
            callfold_strat_grid.itemset((row, y), callfold_strat[i]["allin"])
            callcall_strat_grid.itemset((row, y), callcall_strat[i]["allin"])
            callfoldfold_strat_grid.itemset((row, y), callfoldfold_strat[i]["allin"])
            callcallfold_strat_grid.itemset((row, y), callcallfold_strat[i]["allin"])
            callcallcall_strat_grid.itemset((row, y), callcallcall_strat[i]["allin"])
            callfoldcall_strat_grid.itemset((row, y), callfoldcall_strat[i]["allin"])
            foldfoldcall_strat_grid.itemset((row, y), foldfoldcall_strat[i]["allin"])
            foldcallcall_strat_grid.itemset((row, y), foldcallcall_strat[i]["allin"])
            foldcallfold_strat_grid.itemset((row, y), foldcallfold_strat[i]["allin"])

            utg_regret_grid.itemset((row, y), utg_regret[i]["allin"])
            fold_regret_grid.itemset((row, y), fold_regret[i]["allin"])
            call_regret_grid.itemset((row, y), call_regret[i]["allin"])
            foldfold_regret_grid.itemset((row, y), foldfold_regret[i]["allin"])
            foldcall_regret_grid.itemset((row, y), foldcall_regret[i]["allin"])
            callfold_regret_grid.itemset((row, y), callfold_regret[i]["allin"])
            callcall_regret_grid.itemset((row, y), callcall_regret[i]["allin"])
            callfoldfold_regret_grid.itemset((row, y), callfoldfold_regret[i]["allin"])
            callcallfold_regret_grid.itemset((row, y), callcallfold_regret[i]["allin"])
            callcallcall_regret_grid.itemset((row, y), callcallcall_regret[i]["allin"])
            callfoldcall_regret_grid.itemset((row, y), callfoldcall_regret[i]["allin"])
            foldfoldcall_regret_grid.itemset((row, y), foldfoldcall_regret[i]["allin"])
            foldcallcall_regret_grid.itemset((row, y), foldcallcall_regret[i]["allin"])
            foldcallfold_regret_grid.itemset((row, y), foldcallfold_regret[i]["allin"])

            utg_ev_grid.itemset((row, y), utg_ev[i]["allin"])
            fold_ev_grid.itemset((row, y), fold_ev[i]["allin"])
            call_ev_grid.itemset((row, y), call_ev[i]["allin"])
            foldfold_ev_grid.itemset((row, y), foldfold_ev[i]["allin"])
            foldcall_ev_grid.itemset((row, y), foldcall_ev[i]["allin"])
            callfold_ev_grid.itemset((row, y), callfold_ev[i]["allin"])
            callcall_ev_grid.itemset((row, y), callcall_ev[i]["allin"])
            callfoldfold_ev_grid.itemset((row, y), callfoldfold_ev[i]["allin"])
            callcallfold_ev_grid.itemset((row, y), callcallfold_ev[i]["allin"])
            callcallcall_ev_grid.itemset((row, y), callcallcall_ev[i]["allin"])
            callfoldcall_ev_grid.itemset((row, y), callfoldcall_ev[i]["allin"])
            foldfoldcall_ev_grid.itemset((row, y), foldfoldcall_ev[i]["allin"])
            foldcallcall_ev_grid.itemset((row, y), foldcallcall_ev[i]["allin"])
            foldcallfold_ev_grid.itemset((row, y), foldcallfold_ev[i]["allin"])
            i += 1
        row_index -= 1
        doing_column = True
        continue

diff = np.subtract(utg_strat_grid ,average_grid)
np.savetxt("csv/utg_strat_grid.csv", utg_strat_grid, delimiter=",")
np.savetxt("csv/fold_strat_grid.csv", fold_strat_grid, delimiter=",")
np.savetxt("csv/call_strat_grid.csv", call_strat_grid, delimiter=",")
np.savetxt("csv/foldfold_strat_grid.csv", foldfold_strat_grid, delimiter=",")
np.savetxt("csv/foldcall_strat_grid.csv", foldcall_strat_grid, delimiter=",")
np.savetxt("csv/callfold_strat_grid.csv", callfold_strat_grid, delimiter=",")
np.savetxt("csv/callcall_strat_grid.csv", callcall_strat_grid, delimiter=",")
np.savetxt("csv/callfoldfold_strat_grid.csv", callfoldfold_strat_grid, delimiter=",")
np.savetxt("csv/callcallfold_strat_grid.csv", callcallfold_strat_grid, delimiter=",")
np.savetxt("csv/callcallcall_strat_grid.csv", callcallcall_strat_grid, delimiter=",")
np.savetxt("csv/callfoldcall_strat_grid.csv", callfoldcall_strat_grid, delimiter=",")
np.savetxt("csv/foldfoldcall_strat_grid.csv", foldfoldcall_strat_grid, delimiter=",")
np.savetxt("csv/foldcallcall_strat_grid.csv", foldcallcall_strat_grid, delimiter=",")
np.savetxt("csv/foldcallfold_strat_grid.csv", foldcallfold_strat_grid, delimiter=",")

np.savetxt("csv/utg_regret_grid.csv", utg_regret_grid, delimiter=",")
np.savetxt("csv/fold_regret_grid.csv", fold_regret_grid, delimiter=",")
np.savetxt("csv/call_regret_grid.csv", call_regret_grid, delimiter=",")
np.savetxt("csv/foldfold_regret_grid.csv", foldfold_regret_grid, delimiter=",")
np.savetxt("csv/foldcall_regret_grid.csv", foldcall_regret_grid, delimiter=",")
np.savetxt("csv/callfold_regret_grid.csv", callfold_regret_grid, delimiter=",")
np.savetxt("csv/callcall_regret_grid.csv", callcall_regret_grid, delimiter=",")
np.savetxt("csv/callfoldfold_regret_grid.csv", callfoldfold_regret_grid, delimiter=",")
np.savetxt("csv/callcallfold_regret_grid.csv", callcallfold_regret_grid, delimiter=",")
np.savetxt("csv/callcallcall_regret_grid.csv", callcallcall_regret_grid, delimiter=",")
np.savetxt("csv/callfoldcall_regret_grid.csv", callfoldcall_regret_grid, delimiter=",")
np.savetxt("csv/foldfoldcall_regret_grid.csv", foldfoldcall_regret_grid, delimiter=",")
np.savetxt("csv/foldcallcall_regret_grid.csv", foldcallcall_regret_grid, delimiter=",")
np.savetxt("csv/foldcallfold_regret_grid.csv", foldcallfold_regret_grid, delimiter=",")

np.savetxt("csv/utg_ev_grid.csv", utg_ev_grid, delimiter=",")
np.savetxt("csv/fold_ev_grid.csv", fold_ev_grid, delimiter=",")
np.savetxt("csv/call_ev_grid.csv", call_ev_grid, delimiter=",")
np.savetxt("csv/foldfold_ev_grid.csv", foldfold_ev_grid, delimiter=",")
np.savetxt("csv/foldcall_ev_grid.csv", foldcall_ev_grid, delimiter=",")
np.savetxt("csv/callfold_ev_grid.csv", callfold_ev_grid, delimiter=",")
np.savetxt("csv/callcall_ev_grid.csv", callcall_ev_grid, delimiter=",")
np.savetxt("csv/callfoldfold_ev_grid.csv", callfoldfold_ev_grid, delimiter=",")
np.savetxt("csv/callcallfold_ev_grid.csv", callcallfold_ev_grid, delimiter=",")
np.savetxt("csv/callcallcall_ev_grid.csv", callcallcall_ev_grid, delimiter=",")
np.savetxt("csv/callfoldcall_ev_grid.csv", callfoldcall_ev_grid, delimiter=",")
np.savetxt("csv/foldfoldcall_ev_grid.csv", foldfoldcall_ev_grid, delimiter=",")
np.savetxt("csv/foldcallcall_ev_grid.csv", foldcallcall_ev_grid, delimiter=",")
np.savetxt("csv/foldcallfold_ev_grid.csv", foldcallfold_ev_grid, delimiter=",")


for info_set, action_to_probabilities in tqdm(sorted(data["strategy"].items())):
    norm = sum(list(action_to_probabilities.values()))
    for action in ["call", "fold", "raise", "allin"]:
        probability = action_to_probabilities.get(action, 0)
        cluster_str, history_str = info_set.split(",", 1)
        cluster = int(cluster_str[14:-1])
        history = [h for h in eval(history_str[8:]) if h != "skip"]
        history.append(action)
        path = [to_hand_str(cluster), *history]
        level = len(path)
        dag_data[cluster][level]["size"].append(int(1000 * probability / norm))
        dag_data[cluster][level]["path"].append(os.path.join(*path))

cluster = 1
data = defaultdict(list)
data["size"].append(1000)
data["path"].append(to_hand_str(cluster))
for level, size_and_path in sorted(dag_data[cluster].items()):
    size = size_and_path["size"]
    path = size_and_path["path"]
    path, size = (list(t) for t in zip(*sorted(zip(path, size))))
    data["size"] += size
    data["path"] += path
df = pd.DataFrame(data=data)
df.to_csv("dataset.csv", index=False)
