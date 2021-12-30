"""
CSSE1001 2019s2a1
"""

from a1_support import *
from _ast import Or


# Write the expected functions here

def get_position_in_direction(position, direction):
    """ Given direction then move to the position then return position.
        The type of position is a tuple and the direction is the one of four chars
    """
    if direction == "r":
        position = (position[0] + 1, position[1])
    elif direction == "l":
        position = (position[0] - 1, position[1])
    elif direction =="u":
        position = (position[0], position[1]+1)
    elif direction =="d":
        position = (position[0], position[1]-1)
    return position
    
def get_tile_at_position(level, position):
    """ The type of level is string and position is tuple 
        Return what tile will be in the position 
    """
    return level[position_to_index(position, level_size(level))]
       
def get_tile_in_direction(level, position, direction):
    """ The type of level is string,position is tuple and direction is char.
        Return what will be in the new position 
    """
    return get_tile_at_position(level, get_position_in_direction(position, direction))
    
def remove_from_level(level, position):
    """ The type of level is string and position is tuple.
        Becaue level is string and immutable. Convert it and replace to air.
        Return the given position replace to " ".       
    """  
    convert=list(level)
    convert[position_to_index(position, level_size(level))] =" "
    level = "".join(convert)
    return level

def move(level, position, direction):
    """ The type of level is string ,position is tuple and direction is char.
        Return the new position from given direction       
    """  
    if get_tile_in_direction(level, position, direction) == "#":
        position = get_position_in_direction(position,direction)
        position = get_position_in_direction(position, "u")
        while get_tile_at_position(level, position) == "#":
            position = get_position_in_direction(position, "u")
        return position
       
    if get_tile_in_direction(level, get_position_in_direction(position, direction), "d") == " ":
        position = get_position_in_direction(get_position_in_direction(position, direction), "d")
        while get_tile_at_position(level, get_position_in_direction(position, "d")) == " ":
            position = get_position_in_direction(position, "d")
        return position
    return get_position_in_direction(position, direction)

def print_level(level, position):
    """ The type of level is string ,position is tuple.
        Print the new level and replace the given position to "*"      
    """  
    convert = list(level)
    convert[position_to_index(position, level_size(level))] = "*"
    level = "".join(convert)
    print(level)
     
def attack(level, position):
    """ The type of level is string ,position is tuple.
        If left or right of player is monster then print "Attacking the monster on your left!"
        Return the new level with monster removed or no change of level.
    """
    if get_tile_in_direction(level, position, "l") == "@":
        print("Attacking the monster on your left!")
        convert= list(level)
        convert[position_to_index(get_position_in_direction(position, "l"), level_size(level))]=" "
        level= "".join(convert)

    elif get_tile_in_direction(level, position, "r") == "@":
        print("Attacking the monster on your right!")
        convert= list(level)
        convert[position_to_index(get_position_in_direction(position, "r"), level_size(level))]=" "
        level= "".join(convert)    
    else:
        print("No monsters to attack!")
    return level

def tile_status(level, position):
    """The type of level is string and position is tuple.
       Return a tuple one is tile status one is level status.     
    """
    new_level = level
    if get_tile_at_position(level, position) == "I":
        print("Congratulations! You finished the level")
    elif get_tile_at_position(level, position) == "@":
        print("Hit a monster! Game over!")
    elif (get_tile_at_position(level, position) == "^") or (get_tile_at_position(level, position) == "$"):
        tile = get_tile_at_position(level, position)
        convert=list(level)
        convert[position_to_index(position, level_size(level))]=" "
        new_level="".join(convert)
    return (get_tile_at_position(level, position),new_level)


def main():
    """Handles the  interaction with the user.
    """
    while True:
        chosenMap = input("Please enter the name of the level file (e.g. level1.txt): ")
        if (chosenMap == "level1.txt" or chosenMap == "level2.txt"):
             level = load_level(chosenMap)
             break
         
    score = 0
    position = (0, 1)
    print("Score: " + str(score))
    print_level(level,position)
    check_point = 0

    while True:
        direction = input("Please enter an action (enter '?' for help): ")
        if direction == "?":
            print(HELP_TEXT)
            print("Score: " + str(score))
            print_level(level,position) 
        elif direction =="r":
            position = move(level, position, direction)
            (tile,level) = tile_status(level,position)
            if tile == "@":
                if check_point == 0:
                    break
                elif check_point == 1:
                    score = back
                    position = back2
                    level = back3
            elif tile == "$":
                score += 1
            elif tile == "I":
                break
            elif tile == "^":
                back = score
                back2 = position
                back3 = level
                check_point = 1
            print("Score: " + str(score))
            print_level(level,position)

        elif direction =="l":
            position = move(level, position, direction)
            print("Score: " + str(score))
            print_level(level,position)
        elif direction=="q":
            break
        elif direction == "a":
            level= attack(level, position)
            print("Score: " + str(score))
            print_level(level,position)
        elif direction == "n":
            if check_point == 0:
                pass
            elif check_point == 1:
                score = back
                position = back2
                level = back3
            print("Score: " + str(score))
            print_level(level,position)



       
if __name__ == "__main__":
    main()
