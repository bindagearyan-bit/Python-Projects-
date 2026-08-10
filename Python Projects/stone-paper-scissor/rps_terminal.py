import random
from colorama import init, Fore, Style

init(autoreset=True)  # so colors reset automatically after each print

def check(comp, user):
    if comp == user:
        return 0
    elif comp == "rock" and user == "paper":
        return 1
    elif comp == "paper" and user == "scissor":
        return 1
    elif comp == "scissor" and user == "rock":
        return 1
    else:
        return -1

def get_user_choice(input_mode):
    valid_words = ["rock", "paper", "scissor"]
    num_to_word = {"0": "rock", "1": "paper", "2": "scissor"}
    while True:
        if input_mode == "word":
            user = input("Type rock, paper, or scissor: ").strip().lower()
            if user in valid_words:
                return user
            else:
                print(Fore.YELLOW + "Invalid input! Please type rock, paper, or scissor.")
        else:
            user = input("Enter 0 for rock, 1 for paper, 2 for scissor: ").strip()
            if user in num_to_word:
                return num_to_word[user]
            else:
                print(Fore.YELLOW + "Invalid input! Please enter 0, 1, or 2.")

def play_game(input_mode):
    choices = ["rock", "paper", "scissor"]
    comp = random.choice(choices)
    user = get_user_choice(input_mode)
    score = check(comp, user)
    print("You :", user.capitalize())
    print("Computer :", comp.capitalize())
    if score == 0:
        print(Fore.CYAN + "It's a draw!")
    elif score == 1:
        print(Fore.GREEN + "You Win!")
    else:
        print(Fore.RED + "You Lose!")
    return score

print("=" * 30)
print("  ROCK PAPER SCISSOR GAME")
print("=" * 30)

if __name__ == "__main__":
    print("Choose input mode:")
    print("1. Words (rock, paper, scissor)")
    print("2. Numbers (0, 1, 2)")
    mode_choice = input("Enter 1 or 2: ").strip()
    input_mode = "word" if mode_choice == "1" else "number"

    print("\nChoose mode:")
    print("1. Best of 3")
    print("2. Best of 5")
    mode = input("Enter 1 or 2: ").strip()
    total_rounds = 3 if mode == "1" else 5

    wins = 0
    losses = 0
    draws = 0

    for round_num in range(1, total_rounds + 1):
        print(f"\n--- Round {round_num} ---")
        result = play_game(input_mode)
        if result == 1:
            wins += 1
        elif result == -1:
            losses += 1
        else:
            draws += 1

    print(Style.BRIGHT + "\n--- Final Score ---")
    print(Fore.GREEN + f"Wins   : {wins}")
    print(Fore.RED + f"Losses : {losses}")
    print(Fore.CYAN + f"Draws  : {draws}")

    if wins > losses:
        print(Fore.GREEN + "You won the match! 🎉")
    elif losses > wins:
        print(Fore.RED + "You lost the match!")
    else:
        print(Fore.CYAN + "The match is a draw!")
