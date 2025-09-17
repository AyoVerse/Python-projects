import string
import numpy as  np
def validate_password(password):
    if len((password)) < 8:
        return "password cannot be less than 8 characters."
    if not any(char.islower() for char in password):
        return "Sorry, your password must contain at least a number, an uppercase, a lowercase, and a special character."
    if not any(char.isupper() for char in password):
        return "Sorry, your password must contain at least a number, an uppercase, a lowercase, and a special character."
    if not any(char.isdigit() for char in password):
        return "Sorry, your password must contain at least a number, an uppercase, a lowercase, and a special character."
    if not any(char in string.punctuation for char in password):
        return "Sorry, your password must contain at least a number, an uppercase, a lowercase, and a special character."
    return "Password is valid!"

def generate_password(length =12):
    characters = list(string.ascii_letters + string.digits + string.punctuation)
    password_length = 12
    password = ''.join(np.random.choice(characters, password_length))
    return password


while True:
    Username = str(input(" Enter your Username:___________________"))  
    if len(Username) < 5:
        print("Sorry, Username has to be above 5 characters. Try Again...")
        Username = str(input(" Enter your Username:___________________"))
    else:
        print(" Your Username iS : ", Username)
        break

response = input("Would you like a suggested password, Yes/No : ").strip().lower()
if response=='yes':
    userpassword = generate_password()
    print("Generated password: ", userpassword)
else:
    userpassword = input("Enter your password: ")
    while True:
        message = validate_password(userpassword)
        print(message)
        if message != 'Password is valid!':
            userpassword = input("Enter your password: ")
        else:
            #print('Password is valid!')
            break
        
        
        

            
        
            



















