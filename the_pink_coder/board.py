import math
import the_pink_coder.game as game
from copy import deepcopy
import the_pink_coder.gametheory as gt
import numpy as np
import random

class Board:
    
    # Initialize the board
    def __init__(self, ally, oppo, board={"upper": [], "lower": []}):
        self.ally = ally
        self.oppo = oppo
        self.board = board
        self.available_ally_throws = []
        self.available_oppo_throws = []
        self.possible_ally_throws = []
        self.ally_index = []
        self.protected = True
        self.ally_throw_remain = 9
        self.oppo_throw_remain = 9
        self.type = ["r", "p", "s"]
        self.all_index = {4: (-4, 0), 3: (-4, 1), 2: (-4, 2), 1: (-4, 3), 0: (-4, 4), -1: (-3, 4), -2: (-2, 4), -3: (-1, 4), -4: (0, 4)}
        self.last_position = ()
        self.round = 0


    # Update the board, called by player's update function
    def update_board(self, oppo_action, ally_action, printRes):
        self.round+=1
        if ally_action[0] == "THROW":
            self.ally_throw_remain -= 1
        if oppo_action[0] == "THROW":
            self.oppo_throw_remain -= 1

        if self.oppo_throw_remain < 4 or self.round > 10:
            self.protected = False
        # Update ally action
        id = getattr(self, "ally")
        action = ally_action
        self.last_position = ally_action
        if action[0] == "THROW":
            self.board[self.ally].append([action[1],(action[2][0],action[2][1])])
        else:
            for piece in self.board[self.ally]:
                index = piece[1]
                if index == action[1]:
                    new_piece = [piece[0],(action[2][0], action[2][1])]
                    self.board[self.ally].remove(piece)
                    self.board[self.ally].append(new_piece)
                    break
        
        action = oppo_action

        if action[0] == "THROW":
            self.board[self.oppo].append([action[1],(action[2][0],action[2][1])])
        else:
            for piece in self.board[self.oppo]:
                index = piece[1]
                if index == action[1]:
                    new_piece = [piece[0],(action[2][0], action[2][1])]
                    self.board[self.oppo].remove(piece)
                    self.board[self.oppo].append(new_piece)
                    break
        
        # Update combat result
        tokens = self.board["upper"] + self.board["lower"]
        
        for i in tokens:
            for j in self.board["upper"]:
                if game.same_coord(i, j) and game.defeat(i, j):
                    self.board["upper"].remove(j)

            for k in self.board["lower"]:
                if game.same_coord(i, k) and game.defeat(i, k):
                    self.board["lower"].remove(k)

        self.update_available_throw()

    # Calculate the distance between two pieces
    def distance(self, piece_1, piece_2):
        coord_1 = game.get_coord(piece_1)
        coord_2 = game.get_coord(piece_2)
        return math.sqrt(pow(coord_1[0] - coord_2[0], 2) + pow(coord_1[1] - coord_2[1], 2))


    # Calculate the defeated score for two piece, used by evaluation function
    def defeat_score(self, type_1, type_2, factor):
        if ((type_1 == 'r') and (type_2 == 's')) or ((type_1 == 's') and (type_2 == 'p')) or ((type_1 == 'p') and (type_2 == 'r')):
            return 1.22 * factor
        elif ((type_1 == 'r') and (type_2 == 'p')) or ((type_1 == 's') and (type_2 == 'r')) or ((type_1== 'p') and (type_2 == 's')):
            return -0.77 * factor
        elif ((type_1 == 'r') and (type_2 == 'r')) or ((type_1 == 'p') and (type_2 == 'p')) or ((type_1 == 's') and (type_2 == 's')):
            return 0
    
    
    # Generate evaluative value for one actions
    def evaluation(self, old_board):   
        
        # 
        score = 0

        # Calculating the distance score, basically is on how far of ally token
        # from the opponent token which it could defeat and the opponent which 
        # could defeated it
        distance_score = 0
        for i in self.board[self.ally]:
            min_defeated = 99999
            max_defeated = -99999
            for j in self.board[self.oppo]: 
                current_score = self.defeat_score(i[0], j[0], (12 - self.distance(i, j)))
                if current_score < 0 and current_score > max_defeated:
                    max_defeated = current_score
                elif current_score > 0 and current_score < min_defeated:
                    min_defeated = current_score

            if max_defeated != -99999:
                distance_score += max_defeated
            if min_defeated != 99999:
                distance_score += min_defeated

        if len(self.board[self.ally]) > 0:
            distance_score = distance_score / len(self.board[self.ally])

        # Compare the difference of amount of ally token and opponent token
        diff_ally = len(old_board.board[self.ally]) - len(self.board[self.ally])
        diff_oppo = len(old_board.board[self.oppo]) - len(self.board[self.oppo])

        # Assign weight to different feature and 
        score = 1.5 * distance_score - 12 * diff_ally + 16 * diff_oppo
            
        return score

    # Update the available throw of both ally and opponent in each turn
    def update_available_throw(self):
    
        # Update ally throws
        id = getattr(self, "ally") 
        throw = getattr(self, "ally_throw_remain")
        available_throws = getattr(self, "available_ally_throws")

        for i in range (0, 2, 1):
            if throw > 0:
                if id == "upper":
                    line = 4 - (9 - throw)
                    min_Col = self.all_index[line][0]
                    max_Col = self.all_index[line][1]
                    if (line, min_Col) in available_throws:
                        pass
                    else:
                        available_throws.clear()
                        for j in range(min_Col,max_Col+1):
                            available_throws.append((line, j))
                            if i == 0:
                                self.possible_ally_throws.append((line, j))
                else:
                    line = -4 + (9 - throw)
                    min_Col = self.all_index[line][0]
                    max_Col = self.all_index[line][1]
                    if (line, min_Col) in available_throws:
                        pass
                    else:
                        available_throws.clear()
                        for j in range(min_Col,max_Col+1):
                            available_throws.append((line, j))
                            if i == 0:
                                self.possible_ally_throws.append((line, j))
            
            ## Update opponent throws
            id = getattr(self, "oppo") 
            throw = getattr(self, "oppo_throw_remain")
            available_throws = getattr(self, "available_oppo_throws")

    # Strategy 1:
    # While there are some opponent token in our throwable area, definetly
    # choose to throw the token which could kill it 
    def generate_action_strategy_1(self):
        ally_dict = {"r":0,"p":0,"s":0}
        for peice in self.board[self.ally]:
            ally_dict[peice[0]] += 1

        remain_oppo = len(self.board[self.oppo]) + self.oppo_throw_remain
        possible_ally_actions = []
        if self.ally_throw_remain > 2:
            for piece in self.board[self.oppo]:
                if piece[1] in self.possible_ally_throws:
                    if (piece[0] == 'r' and ally_dict["p"]/len(self.board[self.ally]) <= 0.6) or (piece[0] == 'r' and remain_oppo < 2):
                        possible_ally_actions.append(("THROW", "p", (piece[1])))
                    elif (piece[0] == 'p' and ally_dict["s"]/len(self.board[self.ally]) <= 0.6) or (piece[0] == 'p' and remain_oppo < 2):
                        possible_ally_actions.append(("THROW", "s", (piece[1])))
                    elif (piece[0] == 's' and ally_dict["r"]/len(self.board[self.ally]) <= 0.6) or (piece[0] == 's' and remain_oppo < 2):
                        possible_ally_actions.append(("THROW", "r", (piece[1])))
              
        if len(possible_ally_actions) > 0:
            percentage = 1 - (1 / len(self.board[self.oppo]))
            if percentage >= 0.65:
                pass
            elif len(self.board[self.oppo]) + self.oppo_throw_remain < 4: 
                pass
            else:
                possible_ally_actions = []
        # print(possible_ally_actions) 
        # if possible_ally_actions != []:
        #     return 0
        return possible_ally_actions


    # Generate the best action
    def generate_best_action(self, multi=False):
        # Strategy 1:
        possible_ally_actions = self.generate_action_strategy_1()

        if len(possible_ally_actions) == 1:
            return possible_ally_actions[0] 
        

        # If there is no any actions in strategy 1, apply strategy 2, get all
        # actions which choose to be considered as good action based on current
        # board status 
        if len(possible_ally_actions) == 0:
            possible_ally_actions = self.get_actions("ally")

        possible_oppo_actions = self.get_actions("oppo")
        # print(possible_ally_actions)
        # print(possible_oppo_actions)
        # Generate the matrix, representing the evaluation of the board 
        # after applying one of ally action and opponent acction
        matrix = []
        for ally_action in possible_ally_actions:
            temp_array = []
            for oppo_action in possible_oppo_actions:
                board = deepcopy(self)
                board.update_board(oppo_action, ally_action, False)
                temp_array.append(board.evaluation(self))
            
            matrix.append(temp_array)

        list_res, expect = gt.solve_game(matrix)

        # Multi stage part
        if multi == True and len(list_res) >= 2:
            possible_ally_actions_2 = []
            # Median
            median_score = np.percentile(list_res, 50)
            for ally_action_score in list_res:
                if ally_action_score > median_score:
                    best_action_2 = possible_ally_actions[list(list_res).index(ally_action_score)]
                    possible_ally_actions_2.append(best_action_2)
                    np.delete(list_res, list(list_res).index(ally_action_score))
            
            matrix_2 = []
            for ally_action in possible_ally_actions_2:   
                temp_array = []
                flag = 0
                for oppo_action in possible_oppo_actions:
                    if flag%3 == 0:
                        board = deepcopy(self)
                        board.update_board(oppo_action, ally_action, False)
                        temp_array.append(board.multi_stage())
                    flag += 1
                matrix_2.append(temp_array)

            list_res_2, expect = gt.solve_game(matrix_2)
            max_score_2 = max(list_res_2)
            best_action = possible_ally_actions_2[list(list_res_2).index(max_score_2)]

        # Single-stage
        else:

            # Use random choice to choose the action based on the probability
            # list provided, to avoid the best action being predicted
            size = len(possible_ally_actions)
            index = np.random.choice(np.arange(size), p = list(list_res))
            best_action = possible_ally_actions[index]
        

        return best_action


    # Get the action, including move or throw
    def get_actions(self, id):
    

        possible_throw_actions = []
        possible_move_actions = []

        if id == "ally":
            throw_remain = self.ally_throw_remain
            oppo_id = "oppo"
        elif id == "oppo":
            throw_remain = self.oppo_throw_remain
            oppo_id = "ally"

        if throw_remain > 0:
            possible_throw_actions = self.get_throws(id)

        all_token = self.board[getattr(self, id)]

        # Choose one action which is closest to kill the opponent token for 
        # each type, the would be the token which can move in this round
        dict = {"r": 99999, "p":99999,"s":99999}
        dict_piece = {}
        moveable = []
        
        for i in moveable:
            flag = 0
            for oppo in self.board[getattr(self, oppo_id)]:
                if game.defeat(i, oppo) and self.distance(i, oppo) < dict[i[0]]:
                    dict[i[0]] = self.distance(i, oppo)
                    dict_piece[i[0]] = i 
                # Emergency
                if flag == 0 and game.defeat(oppo, i) and self.distance(i, oppo) < 1:
                    moveable.append(i)
                    flag = 1

        for i in dict_piece:
            moveable.append(dict_piece[i])

        if len(moveable) == 0:
            moveable = all_token


        # For those choosen token, get all their move action, (slide, swing)
        possible_move_actions = self.get_move(id, moveable)
        
        # Remove pieces on same spot, avoid two ally token being in a same
        # coordinate




        if id == "ally":
            current_index = []
            for piece in self.board[self.ally]:
                current_index.append(piece[1])
            print(current_index)
            for action in possible_move_actions:
                if action[2] in current_index:
                    possible_move_actions.remove(action)
            
            for action in possible_throw_actions:
                if action[2] in current_index:
                    possible_throw_actions.remove(action)

        return possible_move_actions + possible_throw_actions


    def get_move(self, id, moveable):

        possible_move_actions = []

        limit_list = []
        if self.ally == "lower":
            limit_list = [4,3,2,1,0]
        else:
            limit_list = [-4,-3,-2,-1,0]
        
        # for i in moveable:
        #     action_list = game.move(self, i, id)
        #     slide_move = game.slide(i)
        #     for index in action_list:
        #         if index in slide_move and ("SLIDE", index, i[1]) != self.last_position: 
        #             possible_move_actions.append(("SLIDE", (i[1]), index))
        #         elif index not in slide_move and ("SWING", index, i[1]) != self.last_position:
        #             possible_move_actions.append(("SWING", (i[1]), index))
        #         else:
        #             pass

        if id == "ally":
            for i in moveable:
                action_list = game.move(self, i, id)
                slide_move = game.slide(i)
                for index in action_list:
                    if self.protected == True and index[0] in limit_list:
                        pass
                    else:
                        if index in slide_move and ("SLIDE", index, i[1]) != self.last_position: 
                            possible_move_actions.append(("SLIDE", (i[1]), index))
                        elif index not in slide_move and ("SWING", index, i[1]) != self.last_position:
                            possible_move_actions.append(("SWING", (i[1]), index))
                        else:
                            pass

        else:
            for i in moveable:
                action_list = game.move(self, i, id)
                slide_move = game.slide(i)
                for index in action_list:
                    if index in slide_move and ("SLIDE", index, i[1]) != self.last_position: 
                        possible_move_actions.append(("SLIDE", (i[1]), index))
                    elif index not in slide_move and ("SWING", index, i[1]) != self.last_position:
                        possible_move_actions.append(("SWING", (i[1]), index))
                    else:
                        pass
        return possible_move_actions



    # Get all the throw action based on remaining throw amount
    def get_throws(self, id):
        possible_throws = []
        
        if id == "ally":
            available_throws = self.possible_ally_throws
        elif id == "oppo":
            available_throws = self.available_oppo_throws


        # Avoid unnecessary throw
        wanted_type = ["r","p","s"]
        if id == "ally":    
            current_type_ally = []
            for piece in self.board[self.ally]:
                if piece[0] not in current_type_ally:
                    current_type_ally.append(piece[0])
            
            current_type_oppo = []
            for piece in self.board[self.oppo]:
                if piece[0] not in current_type_oppo:
                    current_type_oppo.append(piece[0])

            if ('r' in current_type_oppo and 'p' in current_type_ally) or 'r' not in current_type_oppo:
                wanted_type.remove('p')
            if ('s' in current_type_oppo and 'r' in current_type_ally) or 's' not in current_type_oppo:
                wanted_type.remove('r')
            if ('p' in current_type_oppo and 's' in current_type_ally) or 'p' not in current_type_oppo:
                wanted_type.remove('s')

            if len(wanted_type) == 0 and self.oppo_throw_remain == 9:
                wanted_type = self.type
        
        if id == "oppo":      
            current_type_ally = []
            for piece in self.board[self.oppo]:
                if piece[0] not in current_type_ally:
                    current_type_ally.append(piece[0])
            
            current_type_oppo = []
            for piece in self.board[self.ally]:
                if piece[0] not in current_type_oppo:
                    current_type_oppo.append(piece[0])

            if ('r' in current_type_oppo and 'p' in current_type_ally) or 'r' not in current_type_oppo:
                wanted_type.remove('p')
            if ('s' in current_type_oppo and 'r' in current_type_ally) or 's' not in current_type_oppo:
                wanted_type.remove('r')
            if ('p' in current_type_oppo and 's' in current_type_ally) or 'p' not in current_type_oppo:
                wanted_type.remove('s')

            if len(wanted_type) == 0 and self.ally_throw_remain == 9:
                wanted_type = self.type
        
        for i in wanted_type:
            for j in available_throws:
                possible_throws.append(("THROW",i,j))
        random.shuffle(possible_throws)

        return possible_throws

    # Function for multi-stage section of the implementation
    def multi_stage(self):
        possible_ally_actions = self.get_actions("ally")
        possible_oppo_actions = self.get_actions("oppo")
        matrix = []
        for ally_action in possible_ally_actions:
            temp_array = []
            for oppo_action in possible_oppo_actions:
                board = deepcopy(self)
                board.update_board(oppo_action, ally_action, False)
                temp_array.append(board.evaluation(self))
            matrix.append(temp_array)
        list_res, expect = gt.solve_game(matrix)
        return expect