from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations, permutations
from typing import Union, List, Dict, Tuple

from ortools.linear_solver import pywraplp


@dataclass
class Player:
    """
    Defines the player present in the game.
    """
    index: int
    kill_score: Union[int, float]


@dataclass
class Lobby:
    """
    Defines all the lobbies present in the system.
    """
    index: int
    name: str
    score: Union[int, float]


@dataclass
class SkillBasedMatchMaking:
    """
    Defines a mathematical program for finding optimal skill based match making.
    """
    players: List[Player]
    lobbies: List[Lobby]

    party_index: List[Tuple[int, int]]  # List of all the people present in predefined teams..
    min_lobby_capacity: int = field(init=True, default=48)
    max_lobby_capacity: int = field(init=True, default=52)

    X: Dict[Tuple[int, int, int], pywraplp.Solver.BoolVar] = field(init=False, default_factory=dict)
    L: Dict[Tuple[int, int, int], pywraplp.Solver.NumVar] = field(init=False, default_factory=dict)
    M: Dict[Tuple[int, int, int], pywraplp.Solver.NumVar] = field(init=False, default_factory=dict)

    solver: pywraplp.Solver = field(init=False, default=None)
    status: int = field(init=False, default=None)
    run_time: int = field(init=False, default=120)

    def __post_init__(self):
        """

        :return:
        """
        self.solver = pywraplp.Solver.CreateSolver(solver_id="SCIP_MIXED_INTEGER_PROGRAMMING")
        # self.solver = pywraplp.Solver.CreateSolver(solver_id="CBC")

    def process(self):
        """
        1. Create variables.
        2. Add Constraint.
        3. Add objective function.
        4. Optimise
        :return:
        """
        self._create_X()
        self._symmetry_constraint()
        self._same_team_setup()
        self._only_one_lobby()
        self._lobby_capacity_constraint()
        self._l_m()
        self._objective()
        self.status = self.solver.Solve()

    def _create_X(self):
        """
        Defines a decision variable for telling which players will form a team and be part of the lobby.
        :return:
        """
        for p1, p2 in list(permutations(self.players, 2)):
            for lobby in self.lobbies:
                self.X[p1.index, p2.index, lobby.index] = self.solver.BoolVar(name=f"""X_{p1.index}
                _{p2.index}_{lobby.index}""")

    def _symmetry_constraint(self):
        """
        Defines the symmetry constraint implying X_i_j_l == X_j_i_l.
        :return:
        """
        for i, j in combinations(self._get_all_player_index(), 2):
            for lobby in self.lobbies:
                self.solver.Add(self.X[i, j, lobby.index] == self.X[j, i, lobby.index],
                                f"Symmetry for {i} and {j}")

    def _same_team_setup(self):
        """

        :return:
        """
        for idx_1, idx_2 in self.party_index:
            self.solver.Add(sum(self._get_variable_based_on_index(index_1=idx_1, index_2=idx_2)) == 1,
                            f"""Player_idx={idx_1} and Player_idx={idx_2} should be in the same team.""")

    def _get_variable_based_on_index(self, index_1: int, index_2: int = None) -> List[pywraplp.Solver.BoolVar]:
        """
        Defines the methodology of retrieving decision variables based on their indexes.
        :return:
        """
        if index_2 is None:
            return [v for k, v in self.X.items() if k[0] == index_1]
        return [v for k, v in self.X.items() if k[0] == index_1 and k[1] == index_2]

    def _get_all_player_index(self) -> List[int]:
        """
        Returns all the indices of the players.
        :return:
        """
        return [p.index for p in self.players]

    def _only_one_lobby(self):
        """

        :return:
        """
        for i in self._get_all_player_index():
            self.solver.Add(sum(self._get_variable_based_on_index(index_1=i)) == 1)

    def _lobby_capacity_constraint(self):
        """

        :return:
        """
        same_lobby_team = defaultdict(list)

        for k, v in self.X.items():
            same_lobby_team[k[2]].append(v)

        for k, v in same_lobby_team.items():
            self.solver.Add(sum(list(v)) >= 2 * self.min_lobby_capacity)
            self.solver.Add(sum(list(v)) <= 2 * self.max_lobby_capacity)

    def _player_obj_based_on_index(self, idx: int) -> Player:
        """

        :return:
        """
        return [p for p in self.players if p.index == idx][0]

    def _lobby_obj_based_on_index(self, idx: int) -> Lobby:
        """

        :return:
        """
        return [_l for _l in self.lobbies if _l.index == idx][0]

    def _l_m(self):
        """

        :return:
        """
        for k, v in self.X.items():
            p1, p2, lobby = (self._player_obj_based_on_index(k[0]),
                             self._player_obj_based_on_index(k[1]),
                             self._lobby_obj_based_on_index(k[2]))

            self.L[k] = self.solver.NumVar(lb=0, ub=self.solver.infinity(), name=f"L_{k}")
            self.solver.Add(self.L[k] >= v * (p1.kill_score + p2.kill_score - lobby.score))

            self.M[k] = self.solver.NumVar(lb=0, ub=self.solver.infinity(), name=f"M_{k}")
            self.solver.Add(self.M[k] >= v * (- (p1.kill_score + p2.kill_score) + lobby.score))

    def _objective(self):
        """

        :return:
        """
        a = sum(self.L.values())
        b = sum(self.M.values())
        self.solver.Minimize(a + b)
