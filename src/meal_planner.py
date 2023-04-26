import random
from copy import deepcopy

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

'''
The program takes a CSV file as an input, reads the data, sort the food items by remaining validity period, 
tell the user one item best before n days, creates a conflict graph, assigns colors to recipes by graph coloring 
algorithm, and recommends recipes based on food item expiration date.
The program calculate the minimum remaining validity period of a food item in the recipe, 
the shorter the period, the higher the recommended order.
'''


def main(file_path=None):
    # 1. import the csv file, define the food items, sort the food items by expired date

    if file_path is not None:
        df = pd.read_csv(file_path, header=0)
        starches_with_date = list(df['Starches'].dropna())
        meats_with_date = list(df['Meats'].dropna())
        vegetables_with_date = list(df['Vegetables'].dropna())

        starches_dict = dict([item.split(' ') for item in starches_with_date])
        meats_dict = dict([item.split(' ') for item in meats_with_date])
        vegetables_dict = dict([item.split(' ') for item in vegetables_with_date])

        # calculate the valid day and update it as a value to the dict
        update_valid_days(starches_dict)
        update_valid_days(meats_dict)
        update_valid_days(vegetables_dict)
        food_dict = {**starches_dict, **meats_dict, **vegetables_dict}
        food_dict = dict(sorted(food_dict.items(), key=lambda item: item[1]))  # sort the dict by key

        # display the food items with the expired days to the user
        print("############# Here are the food items in your fridge: ##############\n")
        for key, value in food_dict.items():
            print("{}: will expire in {} days".format(key, value))

        starches = list(starches_dict.keys())
        meats = list(meats_dict.keys())
        vegetables = list(vegetables_dict.keys())

        # let the length of three lists are the same
        min_len = min(len(starches), len(meats), len(vegetables))
        starches = starches[:min_len]
        meats = meats[:min_len]
        vegetables = vegetables[:min_len]

        # shuffle the lists randomly
        random.shuffle(starches)
        random.shuffle(meats)
        random.shuffle(vegetables)

        food_items = starches + meats + vegetables

    # 2. Create the conflict graph. Compute the chromatic number, which is the total number of meals

    G = nx.Graph()
    G.add_nodes_from(food_items)
    nx.draw_shell(G, with_labels=True, font_weight='bold')  # draw the nodes
    plt.show()

    # Add conflict edges
    for food1 in food_items:
        for food2 in food_items:
            if food1 != food2 and (food1 in starches and food2 in starches
                                   or food1 in meats and food2 in meats
                                   or food1 in vegetables and food2 in vegetables):
                G.add_edge(food1, food2)

    # Draw the first graph: CONFLICT GRAPH, two vertices are connected if they cannot be part of the same meal
    nx.draw_shell(G, with_labels=True, font_weight='bold')
    plt.show()

    chromatic_num = nx.algorithms.coloring.greedy_color(G)

    # Assign colors to recipes
    recipes = {}
    color_list = []

    n = len(set(chromatic_num.values()))  # number of meals

    # Color the nodes
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'brown', 'gray', 'black', 'white',
              'magenta', 'cyan', 'turquoise', 'maroon']
    colors = colors[0:n]

    num_list = []
    for i in range(len(colors)):
        num_list.append(i)

    for food, num in chromatic_num.items():
        for i in range(len(num_list)):
            if num == num_list[i]:
                color_list.append(colors[i])

    # Draw the second graph: the nodes will be colored
    nx.draw_shell(G, with_labels=True, font_weight='bold', node_color=color_list)
    plt.show()

    # update the graph, add edges for the nodes with the same color, i.e. can be a meal
    G.clear()
    G.add_nodes_from(chromatic_num.keys())
    for food, color in chromatic_num.items():
        for food2, color2 in chromatic_num.items():
            if food != food2 and color == color2:
                G.add_edge(food, food2)

    # Draw the final graph
    nx.draw_shell(G, with_labels=True, font_weight='bold', node_color=color_list)
    plt.show()

    # 3. Create the recipes, make recommendations
    for food, color in chromatic_num.items():
        if color not in recipes:
            recipes[color] = [food]
        else:
            recipes[color].append(food)

    for i in range(len(recipes)):
        if len(recipes.get(i)) != 3:
            recipes.popitem()

    # sort the meals by the food items' expired date, here we use the minimum food item's valid day in a recipe
    # if the minimum expired date in two recipes are the same, then order them by the original order when construct the graph
    recipe_dict = {}
    min_days = 0
    for i in range(len(recipes)):
        recipe = recipes[i]
        min_days = min(food_dict[recipe[0]], food_dict[recipe[1]], food_dict[recipe[2]])
        recipe_dict[' '.join(recipe)] = min_days

    recipe_dict = dict(sorted(recipe_dict.items(), key=lambda item: item[1]))  # sort the dict by key

    # 4. Output the meal plan
    print("\n############# Meal recommendation based on expired date ##############\n")
    output = [f"Day {index}: Recipe with {key} will expire in {value} days" for index, (key, value) in
              enumerate(recipe_dict.items())]
    output.append(f"Recipe with {list(recipe_dict.keys())} will expire in {list(recipe_dict.values())} days")
    print('\n'.join(output[:-1]))

    # 5. Other feature: define user preferences by their keyboard input, eat their favorite food first

    starch = input("Enter your favorite starch in the fridge: ")
    meat = input("Enter your favorite meat in the fridge: ")
    vegetable = input("Enter your favorite vegetable in the fridge: ")
    input_str = starch + ' ' + meat + ' ' + vegetable
    user_prefs = input_str.split(' ')
    # user_prefs = ['bread', 'duck', 'beans']

    print("\n########### Meal recommendation based on your preferences ##############\n")
    recipe_dict_temp = deepcopy(recipe_dict)
    i = 0
    for recipe, days in recipe_dict.items():
        if common_member(recipe.split(' '), user_prefs):
            print('Day {}: Recipe with {} will expire in {} days'.format(i, recipe, recipe_dict[recipe]))
            i += 1
            recipe_dict_temp.pop(recipe)

    output = [f"Day {index+i}: Recipe with {key} will expire in {value} days" for index, (key, value) in
              enumerate(recipe_dict_temp.items())]
    output.append(
        f"Recipe with {list(recipe_dict_temp.keys())} will expire in {list(recipe_dict_temp.values())} days")
    print('\n'.join(output[:-1]))




# A helper function to calculate the valid day of each food item
def valid_days(date_string):
    date_format = "%Y-%m-%d"
    date_obj = datetime.strptime(date_string, date_format)
    today = datetime.today()
    delta = date_obj - today
    return delta.days


# A helper function to update the dictionary's value to the valid day
def update_valid_days(my_dict):
    for starch in my_dict:
        date = my_dict.get(starch).replace("(", "").replace(")", "")
        my_dict[starch] = valid_days(date)


def common_member(a, b):
    a_set = set(a)
    b_set = set(b)
    if (a_set & b_set):
        return True
    else:
        return False


#  Run the program
main("food_items.csv")
