import cs50

print("Number: ", end = '')
card = cs50.get_float()
temp = card
digits = 0
cardtype = None
while temp > 0:
    temp //= 10
    digits += 1
if ((digits == 15) and ((card // 10000000000000 == 34) or (card // 10000000000000 == 37))):
    cardtype = "AMEX"
if (digits == 16):
    if ((card // 100000000000000 > 50) and (card // 100000000000000 < 56)):    
        cardtype = "MASTERCARD"
    elif (card // 1000000000000000 == 4):
        cardtype = "VISA"
if ((digits == 13) and (digits // 1000000000000 == 4)):
    cardtype = "VISA"
card_sum = 0
summand = 0
valid = False
for i in range(1, digits+1):
    if (i % 2 == 0):
        summand = 2 * (card % 10)
        if summand > 9:
            summand = summand % 10 + summand // 10
#        print(summand)    
    else:
        summand = card % 10
#        print(summand)
    card_sum += summand
#    print("SUM: ", card_sum) 
    card //= 10
#print("{}".format(card_sum))    
if card_sum % 10 == 0:
    valid = True
if (valid) and (cardtype != None):    
    print("{}".format(cardtype))
else:
    print("INVALID")