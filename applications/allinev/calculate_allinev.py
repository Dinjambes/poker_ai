import copy
import os
from collections import defaultdict
from typing import Dict

import joblib
import pandas as pd
import ast
from tqdm import tqdm
import numpy as np
import os
from applications.allinev.holdem_calc import holdem_calc
import re
import time
import subprocess
import json


### Comparison of 2 ways to calculate outcome of hands

# print(time.perf_counter())
# results = holdem_calc.calculate(None, False, 1000, None, ['6s', '8s', '7d', '8d', '5s', '6h'], False)
# print(time.perf_counter())
# print("====")
# print(time.perf_counter())
# result = subprocess.Popen(["/home/benjamin/pokerstove/build/bin/ps-eval", "8s6s", "7d8d", "5s6h"], stdout=subprocess.PIPE,
#                      stderr=subprocess.PIPE)
# stdout, stderr = result.communicate()
# output_array = stdout.decode('utf-8').splitlines()
# # results = os.system('/home/benjamin/pokerstove/build/bin/ps-eval 8s6s 7d8d 5s6h')
# print(time.perf_counter())

###

small_blind = 0.10
big_blind = 0.25
buyin = 2

path = 'history/'
files = []
for i in os.listdir(path):
    if os.path.isfile(os.path.join(path, i)) and ('Red' in i):
        files.append(i)

total_ev = 0.
jackpot_ev = 0.
jackpot_odds = 0.
flop_seen = 0
total_hands = 0
hands_history: Dict[Dict, object] = {}
utg_history: Dict[str,int] = {}

players = {}

for file in files:
    print(file)
    file_path = os.path.join(path, file)
    reader = open(file_path, "r")

    while True:
        line = reader.readline()
        # check if line is not empty
        if not line:
            break

        # if re.search(".*SUMMARY.*", line) is not None:
        if re.search(".*Poker Hand.*", line) is not None:
            #Player information I want:
            # number_of_hands
            # history(73s, UTG) Every history is from an All-In. If a player shows its cards I have the history from that too but does not happen a lot
            #   showed [cards] and collected
            hand_id = ''
            if re.search(".*Poker Hand.*", line):
                splitted_line = line.split(' ')
                hand_id = splitted_line[2][3:-1]

            totalpot = 0.
            blind_adjustment = 0.
            herocards = []
            villainscards = []
            utgcards = []
            position = ""
            bb_move = "F"
            sb_move = "F"
            btn_move = "F"
            utg_move = "F"

            action = ""
            current_hand_players = {}
            while True:
                line = reader.readline()
                if line == "\n":
                    break

                #Get list of players
                if re.search("Seat.*chips.*", line):
                    split_line = line.split(' ')
                    player = split_line[2]
                    current_hand_players[player] = ''
                    player_data = players.get(player, {'hands_count': 0, 'hands_won':[], 'history':[]})
                    player_data['hands_count'] += 1
                    players[player] = player_data

                #Search for something like player: from the list of players
                for key in current_hand_players.keys():
                    if re.search(f"{key}: folds.*", line):
                        action += 'F'
                    if re.search(f"{key}: calls.*", line) or re.search(f"{key}: raises.*", line):
                        if action == '':
                            current_hand_players[key] = 'UTG'
                        else:
                            current_hand_players[key] = action
                        action += 'C'
                #If found, look for the action. If the word 'folds' can be found then the player folded, if its 'calls' or 'raises' it was an allin

                if re.search("Hero.*big blind.*", line):
                    blind_adjustment = -big_blind
                    position = "bb"
                elif re.search("Hero.*small blind.*", line):
                    blind_adjustment = -small_blind
                    position = "sb"
                elif re.search("Hero.*button.*", line):
                    position = "btn"
                elif re.search("Hero.*", line):
                    position = "utg"
                elif re.search("big blind.*showed.*", line):
                    bb_move = "C"
                elif re.search("small blind.*showed.*", line):
                    sb_move = "C"
                elif re.search("button.*showed.*", line):
                    btn_move = "C"
                elif re.search(".*showed.*", line):
                    utg_move = "C"
                    v_cards = line.split('[')[1]
                    utgcards.insert(0, v_cards[0:2])
                    utgcards.insert(0, v_cards[3:5])

                # Got a walk
                if re.search(f"Seat.*Hero.*collected.*\(\\${small_blind*2}\)", line):
                    blind_adjustment = small_blind
                # Stole BB
                elif re.search(f"Seat.*Hero.*collected.*\(\\${big_blind*2}\)", line):
                    blind_adjustment = big_blind
                # Stole BB and SB
                elif re.search(f"Seat.*Hero.*collected.*\(\\${big_blind*2+small_blind}\)", line):
                    blind_adjustment = big_blind + small_blind
                elif re.search("Seat.*Hero.*collected.*\(\\$\)", line):
                    print("WTF HAPPENED!")

                if re.search(".*Total pot.*", line):
                    # Get total pot
                    totalpot = float(line.split('$')[1])
                elif re.search(".*Hero.*showed", line):
                    # Get cards
                    h_cards = line.split('[')[1]
                    herocards.insert(0, h_cards[0:2])
                    herocards.insert(0, h_cards[3:5])
                elif re.search(".*showed", line):
                    # Append villain cards
                    v_cards = line.split('[')[1]
                    villainscards.insert(0, v_cards[0:2])
                    villainscards.insert(0, v_cards[3:5])

                    #If villains showed cards and they have a history in the Dict, we add it to the big history dict with the cards
                    split_line = line.split(' ')
                    player = split_line[2]
                    if current_hand_players[player] != '':
                        action = current_hand_players[player]
                        player_data = players[player]

                        if re.search(".*won.*", line):
                            player_data['hands_won'].append(hand_id)

                        if len(current_hand_players) == 3:
                            action = 'F' + action
                        elif len(current_hand_players) == 2:
                            action = 'FF' + action

                        dict = {'action': action, 'cards': v_cards[0:2] + v_cards[3:5]}
                        player_data['history'].append(dict)
                        players[player] = player_data

            total_hands += 1
            if herocards or villainscards:
                flop_seen += 1

            if utgcards:
                utgcards.sort()
                utgcards_parsed = utgcards[0][0:1] + utgcards[1][0:1]
                if utgcards[0][1:] == utgcards[1][1:]:
                    utgcards_parsed += "s"
                else:
                    utgcards_parsed += "o"

                utg_history_node = utg_history.get(utgcards_parsed, 0)
                utg_history_node += 1
                utg_history[utgcards_parsed] = utg_history_node

            if herocards:
                cards = herocards + villainscards
                print(herocards)
                print(villainscards)
                results = holdem_calc.calculate(None, False, 100000, None, cards, False)
                print(results)

                ev = ((totalpot - buyin) * results[1]) - (buyin * sum(results[2:]))

                #Also calculate tie EV
                tie_ev = (((totalpot / (len(villainscards)/2 + 1)) - buyin) * results[0])
                # Thiis is an imperfect calculation of Tie when multiway. For exemple if I have A9 against A4 and K9, there is a calculated 12.39% chance of tie
                # But most of these tie will be separated between me and the player with A4 thus taking the money from the K9 player

                ev += tie_ev

                print("EV:" + str(ev))
                total_ev += ev
                print(f"TOTAL EV NOW:{str(total_ev)}")

                herocards.sort()
                herocards_parsed = herocards[0][0:1] + herocards[1][0:1]
                if herocards[0][1:] == herocards[1][1:]:
                    herocards_parsed += "s"
                else:
                    herocards_parsed += "o"

                history = ""
                if position == "utg":
                    history = "utg"
                elif position == "btn":
                    if utg_move == "F":
                        history = "F"
                    else:
                        history = "C"
                elif position == "sb":
                    if utg_move == "F":
                        history += "F"
                    else:
                        history += "C"
                    if btn_move == "F":
                        history += "F"
                    else:
                        history += "C"
                elif position == "bb":
                    if utg_move == "F":
                        history += "F"
                    else:
                        history += "C"
                    if btn_move == "F":
                        history += "F"
                    else:
                        history += "C"
                    if sb_move == "F":
                        history += "F"
                    else:
                        history += "C"

                average_ev = hands_history.get(str({"cards": herocards_parsed, "history": history}), [0, 0, 0])
                average_ev[0] += ev
                average_ev[1] += 1
                hands_history[str({"cards": herocards_parsed,"history": history})] = average_ev

                # Check if hero card are suited
                if herocards[0][1:] == herocards[1][1:]:
                    suit = herocards[0][1:]
                    first_value = herocards[0][0:1]
                    second_value = herocards[1][0:1]

                    if first_value == 'T':
                        first_value = '10'
                    elif first_value == 'J':
                        first_value = '11'
                    elif first_value == 'Q':
                        first_value = '12'
                    elif first_value == 'K':
                        first_value = '13'
                    elif first_value == 'A':
                        first_value = '14'

                    if second_value == 'T':
                        second_value = '10'
                    elif second_value == 'J':
                        second_value = '11'
                    elif second_value == 'Q':
                        second_value = '12'
                    elif second_value == 'K':
                        second_value = '13'
                    elif second_value == 'A':
                        second_value = '14'

                    if first_value == '14' and (
                            second_value == '2' or second_value == '3' or second_value == '4' or second_value == '5'):
                        first_value = '1'
                    if second_value == '14' and (
                            first_value == '2' or first_value == '3' or first_value == '4' or first_value == '5'):
                        second_value = '1'

                    first_value = int(first_value)
                    second_value = int(second_value)

                    # order them
                    f_value = first_value if first_value < second_value else second_value
                    s_value = first_value if first_value > second_value else second_value

                    distance = abs(f_value - s_value) - 1
                    if distance <= 3:
                        combination_needed = []
                        if distance == 3:
                            combination_needed.insert(0, [first_value + 1, first_value + 2, first_value + 3])
                        elif distance == 2:
                            combination_needed.insert(0, [first_value + 1, first_value + 2,
                                                          first_value + 4])
                            combination_needed.insert(0, [first_value + 1, first_value + 2,
                                                          first_value - 1])
                        elif distance == 1:
                            combination_needed.insert(0, [first_value + 1, first_value + 3,
                                                          first_value + 4])
                            combination_needed.insert(0, [first_value + 1, first_value + 3,
                                                          first_value - 1])
                            combination_needed.insert(0, [first_value + 1, first_value - 1,
                                                          first_value - 2])
                        elif distance == 0:
                            combination_needed.insert(0, [first_value + 2, first_value + 3,
                                                          first_value + 4])
                            combination_needed.insert(0, [first_value + 2, first_value + 3,
                                                          first_value - 1])
                            combination_needed.insert(0, [first_value + 2, first_value - 1,
                                                          first_value - 2])
                            combination_needed.insert(0, [first_value - 1, first_value - 2,
                                                          first_value - 3])
                        combination_needed_parsed = []
                        for x in combination_needed:
                            if x[0] > 14 or x[1] > 14 or x[2] > 14:
                                continue
                            elif x[0] < 1 or x[1] < 1 or x[2] < 1:
                                continue

                            one_card_blocked = False
                            for i in x:
                                if i == 1:
                                    i = 14
                                for y in villainscards:
                                    villain_suit = y[1:]
                                    if villain_suit != suit:
                                        continue
                                    villain_card = y[0:1]
                                    if villain_card == 'T':
                                        villain_card = '10'
                                    elif villain_card == 'J':
                                        villain_card = '11'
                                    elif villain_card == 'Q':
                                        villain_card = '12'
                                    elif villain_card == 'K':
                                        villain_card = '13'
                                    elif villain_card == 'A':
                                        villain_card = '14'

                                    villain_card = int(villain_card)

                                    if villain_card == i:
                                        one_card_blocked = True

                            if not one_card_blocked:
                                combination_needed_parsed.insert(0, x)

                        print("JACKPOT EV FOUND:" + str((180 * (len(combination_needed_parsed) * 0.0006))))
                        jackpot_ev += (180 * (len(combination_needed_parsed) * 0.0006))
                        jackpot_odds += (len(combination_needed_parsed) * 0.0006)

                # Check distance between 2 hero cards
                # T=10 J=11 Q=12 K=13 A=14 or 1


            else:
                print(f"NO FLOP, Blind stolen or lost: {str(blind_adjustment)}")
                total_ev += blind_adjustment
                print(f"TOTAL EV NOW:{str(total_ev)}")

    reader.close()

path = 'history_plus/'
files = []
for i in os.listdir(path):
    files.append(i)

hand_winner_history = {}

for file in files:
    file_path = os.path.join(path, file)

    with open(file_path, 'r') as f:
        distros_dict = json.load(f)

    for distro in distros_dict:
        if len(distro['winner'][0]) == 1:
            hand_winner_history[distro['handId']] = distro['winner'][0][0]

new_dict = {}
for key,value in players.items():
    hands_won = value['hands_won']
    for hand_won in hands_won:
        name = hand_winner_history.get(hand_won,'')
        if name != '':
            current_history_for_player = new_dict.get(name, {'hands_count':0,'history':[]})

            current_history_for_player['history'].extend(value['history'])
            current_history_for_player['hands_count'] += value['hands_count']

            new_dict[name] = current_history_for_player
            break



#Normalize UTG history
normalising_sum = 0
for (key,value) in utg_history.items():
    normalising_sum += value
for (key,value) in utg_history.items():
    value /= normalising_sum

print("TOTAL EV:" + str(total_ev))
print("TOTAL JACKPOT EV:" + str(jackpot_ev))
print(f"TOTAL HANDS: {total_hands}")
print(f"TOTAL FLOP: {flop_seen}")
print(f"JACKPOT ODDS PER HAND: {jackpot_odds / total_hands}")

reader.close()
