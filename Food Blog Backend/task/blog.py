import sqlite3
import sys
import argparse


def full_ingridients(con, cursor, result_r):

    while True:
        try:
            quantity, *measure, ingredient = input("Input quantity of ingredient <press enter to stop>: ").split()
        except ValueError:
            return
        else:
            if not measure:
                measure = ['']
            if (measure[0],) not in cursor.execute(f"SELECT (measure_name) FROM measures").fetchall():
                print("The measure is not conclusive!")
                continue
            f = 0
            for i in cursor.execute(f"SELECT (ingredient_name) FROM ingredients").fetchall():
                if i[0].startswith(ingredient):
                    f = 1
                    ingredient = i[0]

            if not f:
                print("The ingredient is not conclusive!")
                continue

            result_mes = cursor.execute(f"SELECT (measure_name) FROM measures WHERE measure_name = '{measure[0]}'")
            r_mes = result_mes.fetchone()
            result_i = cursor.execute(f"SELECT (ingredient_name) FROM ingredients WHERE ingredient_name = '{ingredient}'")
            r_i = result_i.fetchone()
            cursor.execute(f"INSERT INTO quantity(measure_id, ingredient_id, quantity, recipe_id) VALUES (?, ?, ?, ?)", (*r_mes, *r_i, quantity, result_r))
            con.commit()


def full_recipes(con, cursor):
    print("Pass the empty recipe name to exit.")
    while True:
        r_name = (input("Recipe name: "))
        if not r_name:
            break
        r_des = (input("Recipe description: "))
        args = (r_name, r_des)
        result_r = cursor.execute(f"INSERT INTO recipes(recipe_name, recipe_description) VALUES (?, ?)", args).lastrowid
        con.commit()
        print("1) breakfast  2) brunch  3) lunch  4) supper")
        d_meals = {1: 'breakfast', 2: 'brunch', 3: 'lunch', 4: 'supper'}
        user_serv = [int(i) for i in input("When the dish can be served: ").split()]
        for i in user_serv:
            result_m = cursor.execute(f"SELECT (meal_id) FROM meals WHERE meal_name = '{d_meals[i]}'")
            r_m = result_m.fetchone()
            cursor.execute(f"INSERT INTO serve(recipe_id, meal_id) VALUES (?, ?)", (result_r, *r_m))
            con.commit()

        full_ingridients(con, cursor, result_r)


def create_tables(cursor, con):
    cursor.execute("CREATE TABLE IF NOT EXISTS meals(meal_id INTEGER PRIMARY KEY, meal_name TEXT UNIQUE NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS ingredients(ingredient_id INTEGER PRIMARY KEY, ingredient_name TEXT "
                   "UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS measures(measure_id INTEGER PRIMARY KEY, measure_name TEXT UNIQUE)")
    con.commit()

    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    for table in data:
        name = ''.join(list(table)[:-1])+"_name"
        for item in data[table]:
            cursor.execute(f"INSERT INTO {table}({name}) VALUES ('{item}')")
    con.commit()

    cursor.execute("CREATE TABLE IF NOT EXISTS recipes(recipe_id INTEGER PRIMARY KEY, recipe_name TEXT NOT NULL, "
                   "recipe_description TEXT);")

    cursor.execute("CREATE TABLE IF NOT EXISTS serve(serve_id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL, "
                   "meal_id INTEGER NOT NULL, FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), FOREIGN KEY("
                   "meal_id) REFERENCES meals(meal_id));")
    cursor.execute("CREATE TABLE IF NOT EXISTS quantity(quantity_id INTEGER PRIMARY KEY, measure_id INTEGER NOT NULL, "
                   "quantity INTEGER NOT NULL, recipe_id INTEGER NOT NULL, ingredient_id INTEGER NOT NULL, "
                   "FOREIGN KEY(measure_id) REFERENCES measures(measure_id), FOREIGN KEY(ingredient_id) REFERENCES "
                   "ingredients(ingredient_id), FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id));")
    con.commit()


def check_recipe(ingredients, meals, cursor):
    ingredient = ingredients.split(',')
    meals = tuple(meals.split(','))


    dict_rec = {}
    result_recipe_id = []
    res = cursor.execute("SELECT recipe_id, ingredient_id FROM quantity")
    list_res = res.fetchall()
    for index, i in enumerate(list_res, 0):
        dict_rec.setdefault(list_res[index][0], set()).add(list_res[index][1])
    for el in dict_rec:
        if set(ingredient).issubset(dict_rec[el]):
            result_recipe_id.append(el)


    new_res = cursor.execute(f"SELECT r.recipe_id, r.recipe_name, m.meal_name "
                             f"FROM recipes AS r "
                             f"INNER JOIN serve AS s "
                             f"ON s.recipe_id = r.recipe_id "
                             f"INNER JOIN meals AS m "
                             f"ON m.meal_id = s.meal_id ")
    list_new_res = [i[1] for i in new_res.fetchall() if i[0] in result_recipe_id and i[2] in meals]
    if list_new_res:
        print(f"Recipes selected for you: {', '.join(list_new_res)}")
    else:
        print("There are no such recipes in the database.")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("db_name")
    parser.add_argument("--ingredients")
    parser.add_argument("--meals")

    args = parser.parse_args()
    db_name = args.db_name
    ingredients = args.ingredients
    meals = args.meals

    con = sqlite3.connect(db_name)
    cursor = con.cursor()

    if not ingredients and not meals:
        create_tables(cursor, con)
        full_recipes(con, cursor)
    else:
        check_recipe(ingredients, meals, cursor)


if __name__ == "__main__":
    main()
