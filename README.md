# Skill-based Matchmaking

Skill-based matchmaking (SBMM) is a system used in online multiplayer and Battle Royale-style video games to assign teams of similar skill levels to the same match to compete against each other. The goal of SBMM is to evenly balance the teams in each match, which helps increase overall player engagement and satisfaction from playing the game.

## Solution

### Variable Definition 
L = ${l_1, l_2, l_3}$ -> lobbies

$i, j \in {1, 2, 3, ...., 300}$ -> total number of players

$K_i$ -> kill score of ith player

### Decision Variable

$X_{ijl} = 1$, if i and j are in the same team and part of same lobby

$X_{ijl} = 0$, otherwise

### Constraints

$\sum_{j} \sum_{l} X_{ijl} = 1, \forall i$

P -> parties

$\sum X_{ijl} = 1, (i, j) \in P$

$s_i$ <- score for ith lobby

$\sum_{i} \sum_{j} X_{ijl} >= 48, \forall l$

$\sum_{i} \sum_{j} X_{ijl} <= 52, \forall l$

### Objective Function

$\sum_{i} \sum_{j} \sum_{l} \| s_l - ((k_i + k_j)/2) \| *X_{ijl}$
