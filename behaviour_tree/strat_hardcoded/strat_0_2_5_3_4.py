from utilities.position import Position


class Strat02534:
    def get_start_pos(robot_cls) -> Position:
        return Position(
            130 + robot_cls.WIDTH / 2,
            540 - robot_cls.DISTANCE_CODEUSES - robot_cls.HEIGHT,
            90,
        )

    def get_strat(gauche: int, droite: int, nb_list: list[int]) -> list[str]:
        nb_0 = nb_list[0] * 50 - 20
        nb_2 = nb_list[2] * 50 - 20
        nb_3 = nb_list[3] * 50 - 20
        nb_4 = nb_list[4] * 50 - 20
        nb_5 = nb_list[5] * 50 - 20

        move_nb_zero = 450
        if nb_0 > 0:
            strat = [
                f"move {move_nb_zero + nb_0}",
                f"move -{nb_0}",
            ]
        else:
            strat = [f"move {move_nb_zero}"]

        strat += [
            "move -120",
            f"rotate {gauche}",
            "move 1250",
            f"rotate {droite}",
            "move 500",
            f"rotate {droite}",
        ]

        if nb_2 > 0:
            strat += [f"move {310 + nb_2}", f"move -{310 + nb_2}"]
        else:
            strat += ["move 310", "move -310"]

        if nb_5 > 0:
            strat += [f"move -{340 + nb_5}", f"move {340 + nb_5}"]
        else:
            strat += ["move -340", "move 340"]

        strat += [
            f"rotate {gauche}",
            "move 430",
            f"rotate {droite}",
        ]

        if nb_3 > 0:
            strat += [f"move {360 + nb_3}", f"move -{360 + nb_3}"]
        else:
            strat += ["move 360", "move -360"]

        if nb_4 > 0:
            strat += [f"move -{480 + nb_4}", f"move {480 + nb_4}"]
        else:
            strat += ["move -480", "move 480"]

        strat += [
            f"rotate {droite}",
            "move 800",
            f"rotate {gauche}",
            "move 1150",
            f"rotate {droite}",
            "move 620",
        ]

        return strat