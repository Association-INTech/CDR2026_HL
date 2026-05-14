from utilities.position import Position


class Strat230:
    def get_start_pos(robot_cls) -> Position:
        return Position(
            130 + robot_cls.WIDTH,
            540 - robot_cls.DISTANCE_CODEUSES - robot_cls.HEIGHT,
            90,
        )

    def get_strat(gauche: int, droite: int, nb_list: list[int]) -> list[str]:
        nb_2, nb_3 = nb_list[2] * 50 - 20, nb_list[3] * 50 - 20
        strat = [
            "move 400",
            f"rotate {gauche}",
            "move 1050",
            f"rotate {droite}",
            "move 500",
            f"rotate {droite}",
        ]

        if nb_2 > 0:
            strat += [f"move {260 + nb_2}", f"move -{260 + nb_2}"]
        else:
            strat += ["move 260", "move -260"]

        strat += [
            f"rotate {gauche}",
            "move 430",
            f"rotate {droite}",
        ]

        if nb_3 > 0:
            strat += [f"move {330 + nb_3}", f"move -{330 + nb_3}"]
        else:
            strat += ["move 330", "move -330"]

        strat += [
            f"rotate {droite}",
            "move 700",
            f"rotate {gauche}",
            "move 1350",
            f"rotate {droite}",
            "move 520",
        ]

        return strat