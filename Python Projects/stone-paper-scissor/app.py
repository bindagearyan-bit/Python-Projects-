import random
def check(comp,user):
    if comp==user:
        return 0
    elif comp==0 and user==1:
        return -1
    elif comp==1 and user==2:
        return -1
    elif comp==2 and user==0:
        return -1    
    else:    
        return 1
comp=random.randint(0,2)
user=int(input("O for rock , 1 for paper and 2 for scissor"))
score=check(comp,user)
print("You : ",user)
print("Computer : ",comp) 
if score==0:
    print("It's a draw!")
elif score==-1:
    print("You Win!")
else:
    print("You Lose!") 
                 