import csv

def currencyFix(price):
    price = price.replace(',','')
    if price[0] is '$':
        price = float(price[1:])
    else:
        price = float(price[2:-1]) * -1
    return price
'''
def makeFloatToCurrency(price):
    currencyPrice = ''
    if price < 0:
        currencyPrice = '-$' + str(abs(price))
    else:
        currencyPrice = '$' + str(price)
'''

allSales = [[
            'Booking ID',
            'Status',
            'Activity / Add-On',
            'First Name',
            'Last Name',
            'Tickets / Items',
            'Purchase Date',
            'Activity Date',
            'Activity Time',
            'Promotion Code',
            'Voucher Code',
            'Bookings',
            'Guests',
            'List Price',
            'Discount',
            'Customer Fees',
            'Total',
            'Credit Card Fees',
            'Peek Fees',
            'Reseller Commission',
            'Fee totals',
            'Total - Net',
            'Your Net Revenue',
            'Notes',
            'Payout Date',
            'Payout Transaction ID',
            'Gap',
            'Check Me'
        ]]

otherVendorList = [
    'Anyperk',
    'Cloud',
    'Expedia',
    'Get Your Guide',
    'Adventures',
    'Nyhavn',
    'Xperience',
    'American',
    'Zola',
    'Veltra'
]

with open('peek-sales.csv', 'rU') as f:
    reader = csv.DictReader(f)
    for row in reader:

        sales = []


        if 'Viator' in row['Notes']:
            thirdPartyAgent = 'Viator'
        elif any(otherVendor in row['Notes'] for otherVendor in otherVendorList):
            thirdPartyAgent = 'Other'
        else:
            thirdPartyAgent = False

        alcatraz = 'Alcatraz' in row['Activity / Add-On']

        foodPantry = 'Food Pantry' in row['Activity / Add-On']

        alcoholPairing = 'Alcohol Pairing' in row['Activity / Add-On']

        additionalCharges = ('Additional Charges' in row['Activity / Add-On']) or ('dessert add-on' in row['Activity / Add-On']) or ('Private Tour Alcohol Pairing' in row['Activity / Add-On'])

        guideGratuity = 'Guide gratuity' in row['Activity / Add-On']

        cashGiftCard = 'Cash Gift Card' in row['Activity / Add-On']

        compedTour = 'COMP' in row['Promotion Code']

        if not cashGiftCard and not row['Activity Time']:
            tourGiftPurchase = True
        else:
            tourGiftPurchase = False

        guests = float(row['Guests'])

        listPrice = currencyFix(row['List Price'])
        totalPrice = currencyFix(row['Total'])

        # Fixing List Price and Total Price for Viator
        if thirdPartyAgent is 'Viator':
            if alcatraz:
                listPrice = 142.0 * guests
                totalPrice = 142.0 * guests
            else:
                listPrice += listPrice * (15.0/85.0)
                totalPrice += totalPrice * (15.0/85.0)


        creditCardFees = 0

        # No 0.30 fee

        noCreditCardFees = thirdPartyAgent or (listPrice == 0)
        noThirty = noCreditCardFees or foodPantry or alcoholPairing or additionalCharges

        if not noCreditCardFees:
            creditCardFees = (0.023 * totalPrice)
            if (totalPrice > 0) and not noThirty:
                creditCardFees += 0.3
            elif (totalPrice < 0) and not noThirty:
                creditCardFees -= 0.3

            #TODO check for multibooking

        noPeekFees = thirdPartyAgent or (listPrice == 0) or guideGratuity or alcoholPairing or foodPantry or cashGiftCard or additionalCharges or compedTour

        peekFees = 0
        if not noPeekFees:
            peekFees = Total * 0.01

        # TODO Manually Booked Private: the gap = the Peek Fee - delete Peek Fee

        # TODO peek fee for gift certificate


        resellerCommission = 0
        # Viator
        if 'Viator' in row['Notes']:
            if 'Alcatraz' in row['Activity / Add-On']:
                resellerCommission = (listPrice - (37.25 * guests)) * 0.15
            else:
                resellerCommission = listPrice * 0.15
        elif thirdPartyAgent is 'Other':
            resellerCommission = listPrice * 0.15

        feeTotals = peekFees + creditCardFees + resellerCommission




        netRevenue = currencyFix(row['Your Net Revenue'])

        #TODO cash gift card, 3rd party agent

        if cashGiftCard:
            netRevenue = totalPrice - feeTotals

        totalMinusNet = totalPrice - netRevenue

        gapInTotal = totalMinusNet - feeTotals

        # Multi booking
        if (0.13 < abs(gapInTotal)) and (abs(gapInTotal) < 0.17):
            creditCardFees += gapInTotal
            feeTotals = peekFees + creditCardFees + resellerCommission
            totalMinusNet = totalPrice - netRevenue
            gapInTotal = totalMinusNet - feeTotals

        # Manual booking
        if gapInTotal == guests:
            peekFees = 0

        if abs(gapInTotal) > 0.01:
            if tourGiftPurchase:
                checkMe = 'Add peek fee for tour gift purchase'
            else:
                checkMe = "Check me!"
        else:
            checkMe = ''



        # save row
        sales.append(row['Booking ID'])
        sales.append(row['Status'])
        sales.append(row['Activity / Add-On'])
        sales.append(row['First Name'])
        sales.append(row['Last Name'])
        sales.append(row['Tickets / Items'])
        sales.append(row['Purchase Date'])
        sales.append(row['Activity Date'])
        sales.append(row['Activity Time'])
        sales.append(row['Promotion Code'])
        sales.append(row['Voucher Code'])
        sales.append(row['Bookings'])
        sales.append(row['Guests'])
        sales.append(listPrice) # Viatour
        sales.append(row['Discount'])
        sales.append(row['Customer Fees'])
        sales.append(totalPrice) # Viatour
        sales.append(creditCardFees) # Viatour
        sales.append(peekFees) # Viatour
        sales.append(resellerCommission)
        sales.append(feeTotals)
        sales.append(totalMinusNet)
        sales.append(netRevenue)
        sales.append(row['Notes'])
        sales.append(row['Payout Date'])
        sales.append(row['Payout Transaction ID'])
        sales.append(gapInTotal)
        sales.append(checkMe)

        allSales.append(sales)

    # Export
    with open("sales-output.csv", "wb") as sf:
        writer = csv.writer(sf)
        writer.writerows(allSales)


print allSales
