#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mac.hmac import HMAC

def test_rfc_4231():

    test_cases = [
        {
            'name': 'Test Case 1',
            'key': '0b' * 20,  # 20 bytes of 0x0b
            'data': '4869205468657265',  # "Hi There"
            'expected': 'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7'
        },
        {
            'name': 'Test Case 2',
            'key': '4a656665',  # "Jefe"
            'data': '7768617420646f2079612077616e7420666f72206e6f7468696e673f',  # "what do ya want for nothing?"
            'expected': '5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843'
        },
        {
            'name': 'Test Case 3',
            'key': 'aa' * 20,  # 20 bytes of 0xaa
            'data': 'dd' * 50,  # 50 bytes of 0xdd
            'expected': '773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe'
        },
        {
            'name': 'Test Case 4',
            'key': '0102030405060708090a0b0c0d0e0f10111213141516171819',  # 25 bytes
            'data': 'cd' * 50,  # 50 bytes of 0xcd
            'expected': '82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b'
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases):
        key = bytes.fromhex(test['key'])
        data = bytes.fromhex(test['data'])
        
        hmac = HMAC(key, 'sha256')
        result = hmac.compute(data)
        
        if result == test['expected']:
            print(f"✓ {test['name']} passed")
        else:
            print(f"✗ {test['name']} failed")
            print(f"  Expected: {test['expected']}")
            print(f"  Got:      {result}")
            all_passed = False
    
    return all_passed

def main():
    print("Testing HMAC with RFC 4231 test vectors...")
    print("=" * 60)
    
    if test_rfc_4231():
        print("=" * 60)
        print("All tests passed!")
        return 0
    else:
        print("=" * 60)
        print("Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
