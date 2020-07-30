import json
import random
import numpy as np

d = {'w': 0, 'c': 1, 's': 2}
print(len(d))

# i = 0
# j = i
# print(i)
# print(j)

# i = 1
# print(i)
# print(j)


# num = [7, 5, 1, 6, 9]
# indices = [*range(len(num))] # アンパック:引数としてリストやタプルなどを分解して渡す
# print(indices)

# num = [7, 5, 1, 6, 9]
# indices = [*range(len(num))]
# sorted_indices = sorted(indices, key=lambda i: -num[i])
# sorted_num = [num[i] for i in sorted_indices]
# print(sorted_num)      # ==> [9, 7, 6, 5, 1]
# print(sorted_indices)  # ==> [4, 0, 3, 1, 2]

# data = {
#     "result": {
#         "attacked": {
#             "position": [0,0],
#             "hit": "w",
#             "near": ["c"]
#         }
#     },
#     "condition": {
#         "me": {
#             "w": {
#                 "hp": 2,
#                 "position": [0,0]
#             },
#             "c": {
#                 "hp": 2,
#                 "position": [0,1]
#             },
#             "s": {
#                 "hp": 1,
#                 "position": [1,1]
#             }
#         },
#         "enemy": {
#             "w": {
#                 "hp": 3
#             },
#             "c": {
#                 "hp": 2
#             },
#             "s": {
#                 "hp": 1
#             }
#         }
#     }
# }

# if "result" in data and "attacked" in data["result"]:
# 	print(data["result"])
# 	if "hit" in data["result"]["attacked"]:
# 		print(data["condition"]["enemy"])
# 		ship = data["result"]["attacked"]["hit"]
# 		print(ship)
# 		print(data["condition"]["enemy"][ship]["hp"])
        # x = data["result"]["attacked"]["position"][0]
        # y = data["result"]["attacked"]["position"][1]
        # # hitした艦のhpがまだある
        # if data["condition"]["enemy"][ship]["hp"] > 0:
        #     player.updateEnemyField_WhenHit(ship, x, y)
        # # hitした艦のhpはゼロ
        # else:
        #     player.resetEnemy_Field_WhenDied(ship, x, y)



# a = {'attacked': {'position': [1, 1], 'near': ['w']}}
# m = {'moved': {'ship': 'c', 'distance': [0, 2]}}

# print("attacked" in a)
# print(a["attacked"]["position"])
# print(a["attacked"]["position"][0])
# # print(type(a["attacked"]["position"]))

# field = np.zeros((5, 5), dtype=np.int)

# field[1][2] = 100

# to = random.choice(field)
# print(to)
# # print(to.type)

# attackpos = np.unravel_index(np.argmax(field), field.shape)
# print(attackpos)
# print(list(attackpos))

# 艦の名前と番号の対応辞書
# d = {'w': 0, 'c': 1, 's': 2}

# # 敵艦の位置の候補を確率として持つ配列
# enemy_w_field = np.zeros((Player.FIELD_SIZE, Player.FIELD_SIZE), dtype=np.int)
# enemy_c_field = np.zeros((Player.FIELD_SIZE, Player.FIELD_SIZE), dtype=np.int)
# enemy_s_field = np.zeros((Player.FIELD_SIZE, Player.FIELD_SIZE), dtype=np.int)
# enemy_field = [enemy_w_field, enemy_c_field, enemy_s_field]


# def inside(field, r, c):
#     return 0 <= r < len(field) and 0 <= c < len(field[0])

# def updateEnemyField_WhenNear(near_ship, near_x, near_y):
#     ship_num = d[near_ship]
#     for i in range(near_x-1, near_x+2):
#         for j in range(near_y-1, near_y+2):
#             if inside(self.enemy_field[ship_num], i, j):
#                 enemy_field[ship_num][i][j] += 3

#     print(enemy_field[ship_num])
