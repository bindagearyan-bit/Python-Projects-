import random

def check(comp, user):
    if comp == user:
        return 0
    elif comp == "rock" and user == "paper":
        return -1
    elif comp == "paper" and user == "scissor":
        return -1
    elif comp == "scissor" and user == "rock":
        return -1
    else:
        return 1

def get_user_choice():
    valid_choices = ["rock", "paper", "scissor"]
    while True:
        user = input("Type rock, paper, or scissor: ").strip().lower()
        if user in valid_choices:
            return user
        else:
            print("Invalid input! Please type rock, paper, or scissor.")

choices = ["rock", "paper", "scissor"]
comp = random.choice(choices)
user = get_user_choice()
score = check(comp, user)

print("You :", user.capitalize())
print("Computer :", comp.capitalize())

if score == 0:
    print("It's a draw!")
elif score == -1:
    print("You Win!")
else:
    print("You Lose!")
