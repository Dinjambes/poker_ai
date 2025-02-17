import logging
import multiprocessing as mp
from typing import Dict, List

import numpy as np

from poker_ai.ai.agent import Agent
from poker_ai.games.short_deck.state import ShortDeckPokerState


log = logging.getLogger("sync.ai")
log.setLevel(logging.FATAL)

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


def update_strategy(
    agent: Agent,
    state: ShortDeckPokerState,
    i: int,
    t: int,
    locks: Dict[str, mp.synchronize.Lock],
):
    """

    :param state: the game state
    :param i: the player, i = 1 is always first to act and i = 2 is always second to act, but they take turns who
        updates the strategy (only one strategy)
    :return: nothing, updates action count in the strategy of actions chosen according to sigma, this simple choosing of
        actions is what allows the algorithm to build up preference for one action over another in a given spot
    """
    ph = state.player_i  # this is always the case no matter what i is

    player_not_in_hand = not state.players[i].is_active
    if state.is_terminal or player_not_in_hand or state.betting_round > 0:
        return

    # NOTE(fedden): According to Algorithm 1 in the supplementary material,
    #               we would add in the following bit of logic. However we
    #               already have the game logic embedded in the state class,
    #               and this accounts for the chance samplings. In other words,
    #               it makes sure that chance actions such as dealing cards
    #               happen at the appropriate times.
    # elif h is chance_node:
    #   sample action from strategy for h
    #   update_strategy(rs, h + a, i, t)

    elif ph == i:
        # calculate regret
        this_info_sets_regret = agent.regret.get(state.info_set, state.initial_regret)
        sigma = calculate_strategy(this_info_sets_regret)
        log.debug(f"Calculated Strategy for {state.info_set}: {sigma}")
        # choose an action based of sigma
        available_actions: List[str] = list(sigma.keys())
        action_probabilities: np.ndarray = list(sigma.values())
        action: str = np.random.choice(available_actions, p=action_probabilities)
        log.debug(f"ACTION SAMPLED: ph {state.player_i} ACTION: {action}")
        # Increment the action counter.
        locks["strategy"].acquire()
        this_states_strategy = agent.strategy.get(state.info_set, state.initial_strategy)
        this_states_strategy[action] += 1
        # Update the master strategy by assigning.
        agent.strategy[state.info_set] = this_states_strategy
        locks["strategy"].release()
        new_state: ShortDeckPokerState = state.apply_action(action)
        update_strategy(agent, new_state, i, t, locks)
    else:
        # Traverse each action.
        for action in state.legal_actions:
            log.debug(f"Going to Traverse {action} for opponent")
            new_state: ShortDeckPokerState = state.apply_action(action)
            update_strategy(agent, new_state, i, t, locks)


def cfr(
    agent: Agent,
    state: ShortDeckPokerState,
    i: int,
    t: int,
    locks: Dict[str, mp.synchronize.Lock],
) -> float:
    """
    regular cfr algo

    :param state: the game state
    :param i: player
    :param t: iteration
    :return: expected value for node for player i
    """
    log.debug("")
    log.debug("CFR")
    log.debug("########")
    log.debug(f"Iteration: {t}")
    log.debug(f"Player Set to Update Regret: {i}")
    log.debug(f"P(h): {state.player_i}")
    log.debug(f"P(h) Updating Regret? {state.player_i == i}")
    log.debug(f"Betting Round {state._betting_stage}")
    log.debug(f"Community Cards {state._table.community_cards}")
    for i, player in enumerate(state.players):
        log.debug(f"Player {i} hole cards: {player.cards}")
    try:
        log.debug(f"I(h): {state.info_set}")
    except KeyError:
        pass
    log.debug(f"Betting Action Correct?: {state.players}")

    ph = state.player_i

    player_not_in_hand = not state.players[i].is_active
    if state.is_terminal or player_not_in_hand:
        log.debug("State was terminal or player was not in hand so we exit")
        return state.payout[i]

    # NOTE(fedden): The logic in Algorithm 1 in the supplementary material
    #               instructs the following lines of logic, but state class
    #               will already skip to the next in-hand player.
    # elif p_i not in hand:
    #   cfr()
    # NOTE(fedden): According to Algorithm 1 in the supplementary material,
    #               we would add in the following bit of logic. However we
    #               already have the game logic embedded in the state class,
    #               and this accounts for the chance samplings. In other words,
    #               it makes sure that chance actions such as dealing cards
    #               happen at the appropriate times.
    # elif h is chance_node:
    #   sample action from strategy for h
    #   cfr()

    elif ph == i:
        # calculate strategy
        this_info_sets_regret = agent.regret.get(state.info_set, state.initial_regret)
        sigma = calculate_strategy(this_info_sets_regret)
        tolog = f"Bucket: {str(state.info_set)} Regret was: {str(this_info_sets_regret)} Calculated strategy was : {str(sigma)} "
        log.debug(f"Calculated Strategy for {state.info_set}: {sigma}")

        vo = 0.0
        voa: Dict[str, float] = {}
        for action in state.legal_actions:
            log.debug(
                f"ACTION TRAVERSED FOR REGRET: ph {state.player_i} ACTION: {action}"
            )
            new_state: ShortDeckPokerState = state.apply_action(action)
            voa[action] = cfr(agent, new_state, i, t, locks)
            log.debug(f"Got EV for {action}: {voa[action]}")
            vo += sigma[action] * voa[action]
            log.debug(
                f"Added to Node EV for ACTION: {action} INFOSET: {state.info_set}\n"
                f"STRATEGY: {sigma[action]}: {sigma[action] * voa[action]}"
            )
        log.debug(f"Updated EV at {state.info_set}: {vo}")
        locks["regret"].acquire()
        this_info_sets_regret = agent.regret.get(state.info_set, state.initial_regret)
        for action in state.legal_actions:
            this_info_sets_regret[action] += voa[action] - vo
        # Assign regret back to the shared memory.
        agent.regret[state.info_set] = this_info_sets_regret
        locks["regret"].release()

        locks["ev"].acquire()
        this_info_sets_ev = agent.ev.get(state.info_set,[0.,0.,0])
        this_info_sets_ev[0] += voa["allin"]
        this_info_sets_ev[1] += voa["fold"]
        this_info_sets_ev[2] += 1
        agent.ev[state.info_set] = this_info_sets_ev
        locks["ev"].release()

        #===
        #Update strategy sum (+=)
        locks["strategy"].acquire()
        this_states_strategy = agent.strategy.get(state.info_set, state.initial_strategy)
        tolog += f"Action EV was: {str(str(voa))} Total EV was: {str(vo)} Agent strategy was: {str(this_states_strategy)}"
        this_states_strategy["fold"] += sigma["fold"]
        this_states_strategy["allin"] += sigma["allin"]
        tolog += f" Strategy after was: {str(this_states_strategy)}"
        # Update the master strategy by assigning.
        agent.strategy[state.info_set] = this_states_strategy
        locks["strategy"].release()
        #===
        print(tolog)

        return vo
    else:
        this_info_sets_regret = agent.regret.get(state.info_set, state.initial_regret)
        sigma = calculate_strategy(this_info_sets_regret)
        log.debug(f"Calculated Strategy for {state.info_set}: {sigma}")
        available_actions: List[str] = list(sigma.keys())
        action_probabilities: List[float] = list(sigma.values())
        action: str = np.random.choice(available_actions, p=action_probabilities)
        log.debug(f"ACTION SAMPLED: ph {state.player_i} ACTION: {action}")
        new_state: ShortDeckPokerState = state.apply_action(action)
        return cfr(agent, new_state, i, t, locks)


def cfrp(
    agent: Agent,
    state: ShortDeckPokerState,
    i: int,
    t: int,
    c: int,
    locks: Dict[str, mp.synchronize.Lock],
):
    """
    pruning cfr algo, might need to adjust only pruning if not final betting round and if not terminal node

    :param state: the game state
    :param i: player
    :param t: iteration
    :return: expected value for node for player i
    """
    ph = state.player_i

    player_not_in_hand = not state.players[i].is_active
    if state.is_terminal or player_not_in_hand:
        return state.payout[i]
    # NOTE(fedden): The logic in Algorithm 1 in the supplementary material
    #               instructs the following lines of logic, but state class
    #               will already skip to the next in-hand player.
    # elif p_i not in hand:
    #   cfr()
    # NOTE(fedden): According to Algorithm 1 in the supplementary material,
    #               we would add in the following bit of logic. However we
    #               already have the game logic embedded in the state class,
    #               and this accounts for the chance samplings. In other words,
    #               it makes sure that chance actions such as dealing cards
    #               happen at the appropriate times.
    # elif h is chance_node:
    #   sample action from strategy for h
    #   cfr()
    elif ph == i:
        # calculate strategy
        this_info_sets_regret = agent.regret.get(state.info_set, state.initial_regret)
        sigma = calculate_strategy(this_info_sets_regret)
        # TODO: Does updating sigma here (as opposed to after regret) miss out
        #       on any updates? If so, is there any benefit to having it up
        #       here?
        vo = 0.0
        voa: Dict[str, float] = dict()
        # Explored dictionary to keep track of regret updates that can be
        # skipped.
        explored: Dict[str, bool] = {action: False for action in state.legal_actions}
        # Get the regret for this state.
        this_info_sets_regret = agent.regret.get(state.info_set, state.initial_regret)
        for action in state.legal_actions:
            if this_info_sets_regret[action] > c:
                new_state: ShortDeckPokerState = state.apply_action(action)
                voa[action] = cfrp(agent, new_state, i, t, c, locks)
                explored[action] = True
                vo += sigma[action] * voa[action]
        locks["regret"].acquire()
        # Get the regret for this state again, incase any other process updated
        # it whilst we were doing `cfrp`.
        this_info_sets_regret = agent.regret.get(state.info_set, state.initial_regret)
        for action in state.legal_actions:
            if explored[action]:
                this_info_sets_regret[action] += voa[action] - vo
        # Update the master copy of the regret.
        agent.regret[state.info_set] = this_info_sets_regret
        locks["regret"].release()
        return vo
    else:
        this_info_sets_regret = agent.regret.get(state.info_set, state.initial_regret)
        sigma = calculate_strategy(this_info_sets_regret)
        available_actions: List[str] = list(sigma.keys())
        action_probabilities: List[float] = list(sigma.values())
        action: str = np.random.choice(available_actions, p=action_probabilities)
        new_state: ShortDeckPokerState = state.apply_action(action)
        return cfrp(agent, new_state, i, t, c, locks)
