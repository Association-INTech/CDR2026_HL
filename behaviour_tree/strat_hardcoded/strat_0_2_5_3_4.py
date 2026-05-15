from utilities.position import Position


class Strat02534:
    @staticmethod
    def get_start_pos(robot_cls) -> Position:
        return Position(
            130 + robot_cls.WIDTH / 2,
            540 - robot_cls.DISTANCE_CODEUSES - robot_cls.HEIGHT,
            90,
        )

    @staticmethod
    def get_strat(
        gauche: int, droite: int, nb_list: list[int], orange=True
    ) -> list[str]:
        nb_0 = nb_list[0] * 50 - 20
        nb_2 = nb_list[2] * 50 - 20
        nb_3 = nb_list[3] * 50 - 20
        nb_4 = nb_list[4] * 50 - 20
        nb_5 = nb_list[5] * 50 - 20

        move_nb_zero = 510
        if nb_0 > 0:
            strat = [
                f"move {move_nb_zero + nb_0}",
                f"move -{nb_0}",
            ]
        else:
            strat = [f"move {move_nb_zero}"]

        if orange:
            move = 1270

        else:
            move = 1220

        strat += [
            f"rotate {gauche}",
            f"move {move}",
            f"rotate {droite}",
            "move 500",
            f"rotate {droite}",
        ]

        nb_2_dist = 340
        nb_5_dist = 320
        strat += [
            f"move {nb_2_dist + nb_2}",
            f"move -{nb_2_dist + nb_2 + nb_5_dist + nb_5}",
            f"move {nb_5_dist + nb_5}",
        ]

        strat += [
            f"rotate {gauche}",
            "move 530",
            f"rotate {droite}",
        ]

        # nb_3 and nb_4

        if orange:
            nb_3_dist = 360
        else:
            nb_3_dist = 460
        nb_4_dist = 480

        strat += [
            f"move {nb_3_dist + nb_3}",
            f"move -{nb_3_dist + nb_3 + nb_4_dist + nb_4}",
            f"move {nb_4_dist + nb_4}",
        ]

        strat += [
            f"rotate {droite}",
            "move 1060",
            f"rotate {gauche}",
            "move 1150",
            f"rotate {droite}",
            "move 700",
        ]

        return strat
