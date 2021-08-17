import random
num=random.randint(1,10) #to generate a random number to guess

Player_Name=input("Hey there!, What's your Name?")
num_of_try=0 #counter to record number of trails
print("So "+Player_Name+ " guess the number between 1-10 ;)")

while num_of_try<5: #will only get 5 chances to guess
    guess=int(input())
    num_of_try+=1
    if guess<num:
        print("Its to low")
    elif guess>num:
        print("It's To high")
    elif guess==num:
        break
if guess==num:
    print("Uh You Read My Mind in "+str(num_of_try)+" guess")
else:
    print("hehe It's Never easy to read my mind but still the number is"+str(num))
    
