import pandas as pd
from elements import Player, Lobby, SkillBasedMatchMaking
from itertools import permutations, combinations
from dataclasses import asdict

df = pd.read_csv('player_data.csv')
df['index'] = list(range(len(df)))

players = [Player(index=p['index'], kill_score=p['KD']) for p in df.to_dict('records')]
lobbies = [Lobby(index=0,name='A', score=4.25),
           Lobby(index=1,name='B', score=5.0),
           Lobby(index=2,name='C', score=5.75)]


index_to_player = {rec['index']: rec for rec in df.to_dict('records')}
index_to_lobby = {loby.index : asdict(loby) for loby in lobbies}

skillBasedMatching = SkillBasedMatchMaking(players=players, lobbies=lobbies, party_index=[(0, 21), (1, 33)])
skillBasedMatching.process()

l_f =[]
s_v = []
for k,v in skillBasedMatching.X.items():
    if v.solution_value() > 0.1:
        l_f.append(k)
        s_v.append(v.solution_value())


final_op = []
for _ in l_f:
    p1, p2, l = index_to_player[_[0]], index_to_player[_[1]], index_to_lobby[_[2]]
    final_op.append({'player_1': p1['Player'],
                     'player_1_kill_score': p1['KD'],
                     'player_2': p2['Player'],
                     'player_2_kill_score': p2['KD'],
                     'total_score': (p1['KD'] + p2['KD']),
                     'lobby': l['name'],
                     'lobby_score': l['score']})


df_final = pd.DataFrame(final_op)
df_final.to_csv("team_results.csv", index=False)
