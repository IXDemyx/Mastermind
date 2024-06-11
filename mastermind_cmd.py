
def check_game_state(input_colors, random_colors):
    exact_matches = 0
    contained_matches = 0
    random_list = []
    for i,color in enumerate(input_colors):
            if color == random_colors[i]:
                random_list.append("y")
                input_colors[i] = "x"
                exact_matches += 1
            else:
                random_list.append(random_colors[i]) 
    for color in random_list:
        if color in input_colors:
            input_colors[input_colors.index(color)] = "x"
            contained_matches += 1
            
            
    return exact_matches, contained_matches

test_input_color = ['red', 'red', 'red', 'red']
test_random_colors = ['red', 'red', 'red', 'red']

#print(check_game_state(test_input_color, test_random_colors))