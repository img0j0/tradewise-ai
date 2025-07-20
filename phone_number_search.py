#!/usr/bin/env python3
"""
Phone Number Search Tool for TradeWise AI
Helps find Google Voice numbers that spell TRADE, AI, or related words
"""

def number_to_letters(phone_number):
    """Convert phone number digits to possible letter combinations"""
    keypad = {
        '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL',
        '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ'
    }
    
    letters = []
    for digit in phone_number:
        if digit in keypad:
            letters.append(keypad[digit])
        else:
            letters.append(digit)
    
    return letters

def word_to_numbers(word):
    """Convert word to phone number digits"""
    letter_to_digit = {
        'A': '2', 'B': '2', 'C': '2',
        'D': '3', 'E': '3', 'F': '3',
        'G': '4', 'H': '4', 'I': '4',
        'J': '5', 'K': '5', 'L': '5',
        'M': '6', 'N': '6', 'O': '6',
        'P': '7', 'Q': '7', 'R': '7', 'S': '7',
        'T': '8', 'U': '8', 'V': '8',
        'W': '9', 'X': '9', 'Y': '9', 'Z': '9'
    }
    
    return ''.join(letter_to_digit.get(letter.upper(), letter) for letter in word)

def find_tradewise_numbers():
    """Find phone number patterns for TradeWise AI"""
    
    print("🔍 PHONE NUMBER SEARCH FOR TRADEWISE AI")
    print("=" * 50)
    
    # Target words and their number equivalents
    target_words = {
        'TRADE': word_to_numbers('TRADE'),
        'TRADER': word_to_numbers('TRADER'),  
        'AI': word_to_numbers('AI'),
        'SMART': word_to_numbers('SMART'),
        'WISE': word_to_numbers('WISE'),
        'INVEST': word_to_numbers('INVEST'),
        'STOCKS': word_to_numbers('STOCKS'),
        'MONEY': word_to_numbers('MONEY')
    }
    
    print("\n📱 WORD TO NUMBER CONVERSIONS:")
    print("-" * 30)
    for word, numbers in target_words.items():
        print(f"{word:8} = {numbers}")
    
    # Popular area codes for professional businesses
    area_codes = [
        ('212', 'New York City'),
        ('415', 'San Francisco'), 
        ('617', 'Boston'),
        ('202', 'Washington DC'),
        ('213', 'Los Angeles'),
        ('312', 'Chicago'),
        ('305', 'Miami'),
        ('404', 'Atlanta'),
        ('206', 'Seattle'),
        ('512', 'Austin')
    ]
    
    print(f"\n🌟 RECOMMENDED PHONE NUMBER PATTERNS:")
    print("-" * 40)
    
    # Generate recommended numbers
    for word, numbers in target_words.items():
        if len(numbers) <= 7:  # Standard phone number length
            print(f"\n{word} ({numbers}):")
            for area_code, city in area_codes[:5]:  # Show top 5 cities
                if len(numbers) == 5:
                    full_number = f"({area_code}) {numbers[:2]}-{numbers[2:]}"
                elif len(numbers) == 6:
                    full_number = f"({area_code}) {numbers[:3]}-{numbers[3:]}"
                elif len(numbers) == 7:
                    full_number = f"({area_code}) {numbers[:3]}-{numbers[3:]}"
                else:
                    full_number = f"({area_code}) {numbers}"
                    
                print(f"  {full_number} - {city}")
    
    print(f"\n💡 CREATIVE COMBINATIONS:")
    print("-" * 25)
    
    # Creative combinations
    combinations = [
        ('TRADEME', word_to_numbers('TRADEME')),
        ('TRADEIT', word_to_numbers('TRADEIT')),
        ('AITRADE', word_to_numbers('AITRADE')),
        ('GETRICH', word_to_numbers('GETRICH')),
        ('BUYLOW', word_to_numbers('BUYLOW')),
        ('PROFIT', word_to_numbers('PROFIT'))
    ]
    
    for word, numbers in combinations:
        if len(numbers) <= 7:
            formatted = f"({area_codes[0][0]}) {numbers[:3]}-{numbers[3:]}" if len(numbers) == 7 else f"({area_codes[0][0]}) {numbers}"
            print(f"{word:10} = {formatted}")
    
    print(f"\n🎯 NEXT STEPS:")
    print("-" * 15)
    print("1. Go to voice.google.com")
    print("2. Search for numbers in your preferred area code")
    print("3. Look for patterns matching the numbers above")
    print("4. Check availability and reserve your number")
    print("5. Set up call forwarding to your main phone")
    
    print(f"\n⭐ BEST OPTIONS FOR TRADEWISE AI:")
    print("-" * 35)
    print("• (555) 872-3324 - TRADE-AI (if 555 was real)")
    print("• (212) 872-3324 - TRADE (New York)")
    print("• (415) 872-3324 - TRADE (San Francisco)")
    print("• (617) 9473 - WISE (Boston)")
    print("• (202) 24 - AI (Washington DC)")

if __name__ == "__main__":
    find_tradewise_numbers()