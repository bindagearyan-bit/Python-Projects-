import random

def check(comp, user):
    if comp == user:
        return 0
    elif comp == 0 and user == 1:  # rock vs paper -> user wins
        return -1
    elif comp == 1 and user == 2:  # paper vs scissors -> user wins
        return -1
    elif comp == 2 and user == 0:  # scissors vs rock -> user wins
        return -1
    else:
        return 1

def get_user_choice():
    while True:
        try:
            user = int(input("0 for rock, 1 for paper, 2 for scissor: "))
            if user in (0, 1, 2):
                return user
            else:
                print("Invalid input! Please enter 0, 1, or 2.")
        except ValueError:
            print("Invalid input! Please enter a number (0, 1, or 2).")

comp = random.randint(0, 2)
user = get_user_choice()
score = check(comp, user)

choices = {0: "Rock", 1: "Paper", 2: "Scissor"}
print("You :", choices[user])
print("Computer :", choices[comp])

if score == 0:
    print("It's a draw!")
elif score == -1:
    print("You Win!")
else:
    print("You Lose!")
