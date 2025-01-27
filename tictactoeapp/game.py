
win=[
        [0,1,2],
        [3,4,5],
        [6,7,8],
        [0,3,6],
        [1,4,7],
        [2,5,8],
        [0,4,8],
        [2,4,6]
    ]
dashbord = [
    False, False, False,
    False, False, False,
    False, False, False
    ]
def update_dashboard(value, index):
    dashbord[index] = value
def check_win():
    for i in range(8):
        # print(dashbord[0])
        if dashbord[win[i][0]] == dashbord[win[i][1]] and dashbord[win[i][1]] == dashbord[win[i][2]] and \
            dashbord[win[i][0]]!= False and dashbord[win[i][1]]!= False and dashbord[win[i][0]]!= False:
            return str(dashbord[win[i][0]]) + " won"
    return False
def check_draw():
    if False in dashbord: return False
    if check_win() != False: return False
    return True
def change_turn(TURN):
    # print(TURN)
    if TURN == "O":
        x = "X"
    elif TURN == "X":
        x = "O"
    print(x)
    return x
if __name__ == "__main__":
    print(check_draw())
    print(check_win())