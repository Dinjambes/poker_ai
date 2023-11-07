| code-thing      | status        |
| --------------- | ------------- |
| master          | [![Build Status](https://travis-ci.org/fedden/poker_ai.svg?branch=master)](https://travis-ci.org/fedden/poker_ai)  |
| develop         | [![Build Status](https://travis-ci.org/fedden/poker_ai.svg?branch=develop)](https://travis-ci.org/fedden/poker_ai) |
| maintainability | [![Maintainability](https://api.codeclimate.com/v1/badges/c5a556dae097b809b4d9/maintainability)](https://codeclimate.com/github/fedden/poker_ai/maintainability) |
| coverage        | [![Test Coverage](https://api.codeclimate.com/v1/badges/c5a556dae097b809b4d9/test_coverage)](https://codeclimate.com/github/fedden/poker_ai/test_coverage) |
| license         | [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) |

[Read the documentation]()

# 🤖 All-In or Fold Poker AI fork

This original repository contains an open source implementation of a poker AI using the ideas of Counterfactual Regret.

This fork is implementing the All-In or Fold (AoF) variant of poker. Much like the Short Deck variant used in the original
project, AoF is a very simplified version of poker. This was done in 2020 and I am just right now cleaning it up and
committing to a fork.

This fork requires a local installation of pokerstove to calculate EV

## _Changes Made_

- Implemented AoF variant of poker
- Created a script to get csv files for each potential situation
- Added calculation of jackpot EV
- Calculate EV based on real world hand data

## Prerequisites

This repository assumes Python 3.7 or newer is used.

## Installing

Either install from pypi:
```bash
pip install poker_ai 
```

Or if you want to dev on our code, install the Python package from source by cloning this repo and `pip -e` installing it:
```bash
git clone https://github.com/fedden/poker_ai.git # Though really we should use ssh here!
cd /path/to/poker_ai
pip install .
```

## Command Line Interface (CLI)

We have a CLI that will be installed when you pip install the package. To get help on any option, just add the `--help` flag when invoking the CLI.

How to get a list of commands that can be run:
```bash
poker_ai --help
``` 

You will need to produce some lookup tables that cluster the various information sets. Here is more information on that:
```bash
poker_ai cluster --help
```

How to get information on training an agent:
```bash
poker_ai train start --help
```

How to get information on resuming training:
```bash
poker_ai train resume --help
```

Once you have an agent, and want to play against it, you can do the following:
```bash
poker_ai play --help
```

## Running tests

We are working hard on testing our components, but contributions here are always welcome. You can run the tests by cloning the code, changing directory to this repositories root directory (i.e `poker_ai/`) and call the python test library `pytest`:
```bash
cd /path/to/poker_ai
pip install pytest
pytest
```

## Building documentation

Documentation is hosted, but you can build it yourself if you wish:
```bash
# Build the documentation.
cd /path/to/poker_ai/docs
make html
cd ./_build/html 
# Run a webserver and navigate to localhost and the port (usually 8000) in your browser.
python -m http.server 
```

## Repository Structure

Below is a rough structure of the codebase. 

```
├── applications   # Larger applications like the state visualiser sever.
├── paper          # Main source of info and documentation :)
├── poker_ai       # Main Python library.
│   ├── ai         # Stub functions for ai algorithms.
│   ├── games      # Implementations of poker games as node based objects that
│   │              # can be traversed in a depth-first recursive manner.
│   ├── poker      # WIP general code for managing a hand of poker.
│   ├── terminal   # Code to play against the AI from your console.
│   └── utils      # Utility code like seed setting.
├── research       # A directory for research/development scripts 
│                  # to help formulate understanding and ideas.
└── test           # Python tests.
    ├── functional # Functional tests that test multiple components 
    │              # together.
    └── unit       # Individual tests for functions and objects.
```

## Code Examples

Here are some assorted examples of things that are being built in this repo.

### State based poker traversal

To perform MCCFR, the core algorithm of poker_ai, we need a class that encodes all of the poker rules, that we can apply an action to which then creates a new game state.

```python
pot = Pot()
players = [
    ShortDeckPokerPlayer(player_i=player_i, initial_chips=10000, pot=pot)
    for player_i in range(n_players)
]
state = ShortDeckPokerState(players=players)
for action in state.legal_actions:
    new_state: ShortDeckPokerState = state.apply_action(action)
```

### Playing against AI in your terminal

We also have some code to play a round of poker against the AI agents, inside your terminal.

The characters are a little broken when captured in `asciinema`, but you'll get the idea by watching this video below. Results should be better in your actual terminal!

<p align="center">
  <a href="https://asciinema.org/a/331234" target="_blank">
    <img src="https://asciinema.org/a/331234.svg" width="500" />
  </a>
</p>
To invoke the code, either call the `run_terminal_app` method directly from the `poker_ai.terminal.runner` module, or call from python like so:

```bash
cd /path/to/poker_ai/dir
python -m poker_ai.terminal.runner       \
  --agent offline                        \ 
  --pickle_dir ./research/blueprint_algo \
  --strategy_path ./research/blueprint_algo/offline_strategy_285800.gz 
```

### Web visualisation code

We are also working on code to visualise a given instance of the `ShortDeckPokerState`, which looks like this:
<p align="center">
  <img src="https://github.com/fedden/poker_ai-poker-AI/blob/develop/assets/visualisation.png">
</p>

It is so we can visualise the AI as it plays, and also debug particular situations visually. The idea as it stands, is a live web-visualisation server like TensorBoard, so you'll just push your current poker game state, and this will be reflected in the visualisations, so you can see what the agents are doing. 

[_The frontend code is based on this codepen._](https://codepen.io/Rovak/pen/ExYeQar)

Here is an example of how you could plot the poker game state:
```python
from plot import PokerPlot
from poker_ai.games.short_deck.player import ShortDeckPokerPlayer
from poker_ai.games.short_deck.state import ShortDeckPokerState
from poker_ai.poker.pot import Pot


def get_state() -> ShortDeckPokerState:
    """Gets a state to visualise"""
    n_players = 6
    pot = Pot()
    players = [
        ShortDeckPokerPlayer(player_i=player_i, initial_chips=10000, pot=pot)
        for player_i in range(n_players)
    ]
    return ShortDeckPokerState(
        players=players, 
        pickle_dir="../../research/blueprint_algo/"
    )


pp: PokerPlot = PokerPlot()
# If you visit http://localhost:5000/ now you will see an empty table.

# ... later on in the code, as proxy for some code that obtains a new state ...
# Obtain a new state.
state: ShortDeckPokerState = get_state()
# Update the state to be plotted, this is sent via websockets to the frontend.
pp.update_state(state)
# http://localhost:5000/ will now display a table with 6 players.
```

### Playing a game of poker

There are two parts to this repository, the code to manage a game of poker, and the code to train an AI algorithm to play the game of poker. A low level thing to first to is to implement a poker engine class that can manage a game of poker.

The reason the poker engine is implemented is because it is useful to have a well-integrated poker environment available during the development of the AI algorithm, incase there are tweaks that must be made to accomadate things like the history of state or the replay of a scenario during Monte Carlo Counterfactual Regret Minimisation. 

The following code is how one might program a round of poker that is deterministic using the engine. This engine is now the first pass that will be used support self play.

```python
from poker_ai import utils
from poker_ai.ai.dummy import RandomPlayer
from poker_ai.poker.table import PokerTable
from poker_ai.poker.engine import PokerEngine
from poker_ai.poker.pot import Pot

# Seed so things are deterministic.
utils.random.seed(42)

# Some settings for the amount of chips.
initial_chips_amount = 10000
small_blind_amount = 50
big_blind_amount = 100

# Create the pot.
pot = Pot()
# Instanciate six players that will make random moves, make sure 
# they can reference the pot so they can add chips to it.
players = [
    RandomPlayer(
        name=f'player {player_i}',
        initial_chips=initial_chips_amount,
        pot=pot)
    for player_i in range(6)
]
# Create the table with the players on it.
table = PokerTable(players=players, pot=pot)
# Create the engine that will manage the poker game lifecycle.
engine = PokerEngine(
    table=table,
    small_blind=small_blind_amount,
    big_blind=big_blind_amount)
# Play a round of Texas Hold'em Poker!
engine.play_one_round()
```

## Contributing

This is an open effort and help, criticisms and ideas are all welcome. 

First of all, please check out the [CONTRIBUTING](/CONTRIBUTING.md) guide.

Feel free to start a discussion on the github issues or to reach out to me at leonfedden at gmail dot com. 

## License

The code is provided under the copy-left GPL licence. If you need it under a more permissive license then please contact me at leonfedden at gmail dot com.
