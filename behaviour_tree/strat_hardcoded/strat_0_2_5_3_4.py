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
    def get_strat(gauche: int, droite: int, nb_list: list[int]) -> list[str]:
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

        strat += [
            f"rotate {gauche}",
            "move 1220",
            f"rotate {droite}",
            "move 350",
            f"rotate {droite}",
        ]
        
        move_nb_2 = 270
        if nb_2 > 0:
            strat += [f"move {move_nb_2 + nb_2}", f"move -{move_nb_2 + nb_2}"]
        else:
            strat += [f"move {move_nb_2}", f"move -{move_nb_2}"]

        move_nb_5 = 360
        if nb_5 > 0:
            strat += [f"move -{move_nb_5 + nb_5}", f"move {move_nb_5 + nb_5}"]
        else:
            strat += [f"move -{move_nb_5}", f"move {move_nb_5}"]

        strat += [
            f"rotate {gauche}",
            "move 550",
            f"rotate {droite}",
        ]

        move_nb_3 = 360
        if nb_3 > 0:
            strat += [f"move {move_nb_3 + nb_3}", f"move -{move_nb_3 + nb_3}"]
        else:
            strat += [f"move {move_nb_3}", f"move -{move_nb_3}"]

        move_nb_4 = 480
        if nb_4 > 0:
            strat += [f"move -{move_nb_4 + nb_4}", f"move {move_nb_4 + nb_4}"]
        else:
            strat += [f"move -{move_nb_4}", f"move {move_nb_4}"]

        strat += [
            f"rotate {droite}",
            "move 1060",
            f"rotate {gauche}",
            "move 1300",
            f"rotate {droite}",
            "move 700",
        ]

        return strat
