import sys
import cs50
import string
def main():
    if len(sys.argv) != 2:
        print("Usage: python vigenere.py k")
        return 1
    key = sys.argv[1]
    key = key.lower()
    l = len(key)
    if not key.isalpha():
        print("Usage: python vigenere.py k")
    print("plaintext: ", end = "")    
    plaintext =cs50.get_string()
    ciphertext = ""
    summand = ""
    j = 0
    for i in range(len(plaintext)):
        c = plaintext[i]
        if (ord(c) >= 41) and (ord(c) <= 90):
            summand = chr((ord(c) - ord("A") + ord(key[j%l]) - ord("a")) % 26 + ord("A")) 
            j +=1
        elif (ord(c) >= 97) and (ord(c) <= 122):
            summand = chr((ord(c) - ord("a") + ord(key[j%l]) - ord("a")) % 26 + ord("a")) 
            j+=1
        else:
            summand = c
        ciphertext += summand
    print("ciphertext: {}".format(ciphertext))
    
if __name__ == "__main__":
    main()