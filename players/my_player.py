import json
import os
import random
import socket
import sys

import numpy as np

sys.path.append(os.getcwd())

from lib.player_base import Player, PlayerShip


class MyPlayer(Player):

    def __init__(self, seed=0):
        random.seed(seed)

        # フィールドを2x2の配列として持っている．
        self.field = [[i, j] for i in range(Player.FIELD_SIZE)
                      for j in range(Player.FIELD_SIZE)]

        # 艦の名前と番号の対応辞書
        self.d = {'w': 0, 'c': 1, 's': 2}

        # 敵艦の位置の候補を確率として持つ配列
        self.enemy_w_field = np.zeros((Player.FIELD_SIZE, Player.FIELD_SIZE), dtype=np.int)
        self.enemy_c_field = np.zeros((Player.FIELD_SIZE, Player.FIELD_SIZE), dtype=np.int)
        self.enemy_s_field = np.zeros((Player.FIELD_SIZE, Player.FIELD_SIZE), dtype=np.int)
        self.enemy_field = [self.enemy_w_field, self.enemy_c_field, self.enemy_s_field]

        # 敵艦の位置の確定の有無を示すフラグ
        self.enemy_w_known = False
        self.enemy_c_known = False
        self.enemy_s_known = False
        self.enemy_known = [self.enemy_w_known, self.enemy_c_known, self.enemy_s_known]

        # 確定した敵艦の位置
        self.enemy_w_pos = [-1, -1]
        self.enemy_c_pos = [-1, -1]
        self.enemy_s_pos = [-1, -1]
        self.enemy_pos = [self.enemy_w_pos, self.enemy_c_pos, self.enemy_s_pos]

        # 初期配置を非復元抽出でランダムに決める．
        ps = random.sample(self.field, 3)
        positions = {'w': ps[0], 'c': ps[1], 's': ps[2]}
        super().__init__(positions)

    #
    # 移動か攻撃かランダムに決める．
    # どれがどこへ移動するか，あるいはどこに攻撃するかもランダム．
    #
    def action(self):

        # attack
        i = 0
        to_candidate = self.decideAttackPosition()
        print()
        print(to_candidate)
        to = [int(x) for x in list(reversed(list(np.unravel_index(to_candidate[i], self.enemy_sum_field.shape))))]
        while not self.can_attack(to):
            print("can't attack", to)
            i += 1
            if i == 25:
                break;
            to = [int(x) for x in list(reversed(list(np.unravel_index(to_candidate[i], self.enemy_sum_field.shape))))]
        if i < 25:
            return json.dumps(self.attack(to))
        
        # move
        else:
            ship = random.choice(list(self.ships.values()))
            to = random.choice(self.field)
            while not ship.can_reach(to) or not self.overlap(to) is None:
                to = random.choice(self.field)
            return json.dumps(self.move(ship.type, to))

        # act = random.choice(["move", "attack"])
        # if act == "move":
        #     ship = random.choice(list(self.ships.values()))
        #     to = random.choice(self.field)
        #     while not ship.can_reach(to) or not self.overlap(to) is None:
        #         to = random.choice(self.field)
        #     print(type(to))
        #     print(type(to[0]))
        #     return json.dumps(self.move(ship.type, to))

        # elif act == "attack":
        #     to = random.choice(self.field)
        #     while not self.can_attack(to):
        #         to = random.choice(self.field)
        #     print(type(to))
        #     print(type(to[0]))
        #     return json.dumps(self.attack(to))


    # 要素の大きい順にインデックスをつくる
    def decideAttackPosition(self):
        self.enemy_sum_field = sum(self.enemy_field)
        self.flat_enemy_sum_field = self.enemy_sum_field.flatten()
        index = [*range(len(self.flat_enemy_sum_field))]
        sorted_index = sorted(index, key=lambda i: -self.flat_enemy_sum_field[i])
        sorted_flat_enemy_sum_field = [self.flat_enemy_sum_field[i] for i in sorted_index]
        # print(self.enemy_sum_field)
        return sorted_index

    def inside(self, field, r, c):
        return 0 <= r < len(field) and 0 <= c < len(field[0])

    # 水しぶきがあがった→near_shipのfieldのnear_pos周辺を+3
    def updateEnemyField_WhenNear(self, near_ship, near_x, near_y):
        ship_num = self.d[near_ship]
        for j in range(near_x-1, near_x+2):
            for i in range(near_y-1, near_y+2):
                if self.inside(self.enemy_field[ship_num], i, j):
                    self.enemy_field[ship_num][i][j] += 3
        # print(near_ship)
        # print(self.enemy_field[ship_num])
    
    #　hitしたが生存中→hit_shipの場所を特定し、追尾
    def updateEnemyField_WhenHit(self, hit_ship, hit_x, hit_y):
        ship_num = self.d[hit_ship]
        self.enemy_known[ship_num] == True
        self.enemy_pos[ship_num] == [hit_x, hit_y]

    #　hitし撃沈→died_shipのfieldを0にリセット
    def resetEnemy_Field_WhenDied(self, died_ship, died_x, died_y):
        ship_num = self.d[died_ship]
        self.enemy_known[ship_num] == False
        self.enemy_field[ship_num] = np.zeros((Player.FIELD_SIZE, Player.FIELD_SIZE), dtype=np.int)

    # 敵がattackしてきた→全ての艦のfieldのattacked_pos周辺を+1
    def updateEnemyField_WhenAttacked(self, attacked_x, attacked_y):
        for field in self.enemy_field:
            for j in range(attacked_x-1, attacked_x+2):
                for i in range(attacked_y-1, attacked_y+2):
                    if self.inside(field, i, j):
                        field[i][j] += 1
            # print(field)            

    # 敵がmoved→moved_shipの位置を知っていれば追尾続行
    #          知らなければmoved_shipのfieldの対象地域を+3
    def updateEnemyField_WhenMoved(self, moved_ship, distance_x, distance_y):
        ship_num = self.d[moved_ship]
        if self.enemy_known[ship_num]:
            self.enemy_pos[ship_num][0] += distance_x
            self.enemy_pos[ship_num][1] += distance_y
        else:
            if distance_y == 0:
                if distance_x < 0:
                    self.enemy_field[ship_num][:, 0:Player.FIELD_SIZE+distance_x] += 3
                else:
                    self.enemy_field[ship_num][:, distance_x:Player.FIELD_SIZE] += 3
            else:
                if distance_y < 0:
                    self.enemy_field[ship_num][0:Player.FIELD_SIZE+distance_y, :] += 3
                else:
                    self.enemy_field[ship_num][distance_y:Player.FIELD_SIZE, :] += 3

            # print(moved_ship)
            # print(self.enemy_field[ship_num])
        

# 仕様に従ってサーバとソケット通信を行う．
def main(host, port, seed=0):
    assert isinstance(host, str) and isinstance(port, int)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        with sock.makefile(mode='rw', buffering=1) as sockfile:
            get_msg = sockfile.readline()
            print(get_msg)
            # data = json.loads(get_msg)
            # print(json.dumps(data, indent = 2))
            player = MyPlayer()
            sockfile.write(player.initial_condition()+'\n')

            while True:
                info = sockfile.readline().rstrip()
                print(info)
                if info == "your turn":
                    action = player.action() # アクションを決定
                    print()
                    print("sum")
                    print(player.enemy_sum_field)
                    print()

                    # 自分がmoveしたとき
                    if "move" in action:
                        print(action)
                    sockfile.write(action+'\n') # アクションを送信
                    get_msg = sockfile.readline()
                    data = json.loads(get_msg)

                    # 自分がattackしたとき
                    if "result" in data and "attacked" in data["result"]:
                        print(data["result"])
                        # nearはその有無によらず表示される
                        near = data["result"]["attacked"]["near"]
                        # 水しぶきがたった
                        if near != []:
                            x = data["result"]["attacked"]["position"][0]
                            y = data["result"]["attacked"]["position"][1]
                            for i in range(len(near)):
                                player.updateEnemyField_WhenNear(near[i], x, y)
                        # hitした
                        if "hit" in data["result"]["attacked"]:
                            print(data["condition"]["enemy"])
                            ship = data["result"]["attacked"]["hit"]
                            x = data["result"]["attacked"]["position"][0]
                            y = data["result"]["attacked"]["position"][1]
                            # hitした艦のhpがまだある
                            if ship in data["condition"]["enemy"]:
                                player.updateEnemyField_WhenHit(ship, x, y)
                            # hitした艦のhpはゼロ(enemy内に記載されない)
                            else:
                                player.resetEnemy_Field_WhenDied(ship, x, y)

                        for field in player.enemy_field:
                            print(field)
                        print()
                        print(sum(player.enemy_field))

                    else:
                        pass

                    print()
                    print()
                    player.update(get_msg)


                elif info == "waiting":
                    get_msg = sockfile.readline()
                    data = json.loads(get_msg)

                    # {'attacked': {'position': [1, 1], 'near': ['w']}}
                    # {'moved': {'ship': 'c', 'distance': [0, 2]}}
                    print(data["result"])

                    # 相手がattackしてきたとき
                    if ("attacked" in data["result"]):
                        x = data["result"]["attacked"]["position"][0]
                        y = data["result"]["attacked"]["position"][1]
                        player.updateEnemyField_WhenAttacked(x, y)

                    #　相手がmoveしたとき
                    else:
                        ship = data["result"]["moved"]["ship"]
                        x = data["result"]["moved"]["distance"][0]
                        y = data["result"]["moved"]["distance"][1]
                        player.updateEnemyField_WhenMoved(ship, x, y)

                    print()
                    for field in player.enemy_field:
                        print(field)
                    # print()
                    # print(sum(player.enemy_field))
                    print()
                    print()
                    player.update(get_msg)

                elif info == "you win":
                    break
                elif info == "you lose":
                    break
                elif info == "even":
                    break
                else:
                    raise RuntimeError("unknown information")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Sample Player for Submaline Game")
    parser.add_argument(
        "host",
        metavar="H",
        type=str,
        help="Hostname of the server. E.g., localhost",
    )
    parser.add_argument(
        "port",
        metavar="P",
        type=int,
        help="Port of the server. E.g., 2000",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed of the player",
        required=False,
        default=0,
    )
    args = parser.parse_args()

    main(args.host, args.port, seed=args.seed)
