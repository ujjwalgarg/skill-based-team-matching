# Skill-based Matchmaking

Skill-based matchmaking (SBMM) is a system used in online multiplayer and Battle Royale-style video games to assign teams of similar skill levels to the same match to compete against each other. The goal of SBMM is to evenly balance the teams in each match, which helps increase overall player engagement and satisfaction from playing the game.

## Solution

### Variable Definition 
L = {l_1, l_2, l_3} -> lobbies

i, j \in {1, 2, 3, ...., 300} -> total number of players

K_i -> kill score of ith player

Let X be the decision variable

X_i_j_l = 1, if i and j are in the same team and part of same lobby
X_i_j_l = 0, otherwise




