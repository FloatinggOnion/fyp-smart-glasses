#!/usr/bin/env python3
"""
Test script to verify markdown stripping functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scene_service import strip_markdown

def test_markdown_stripping():
    """Test the markdown stripping function with various examples"""
    print("=== Markdown Stripping Test ===\n")
    
    test_cases = [
        {
            "input": "# Header\nThis is **bold** text and *italic* text.",
            "expected": "Header\nThis is bold text and italic text."
        },
        {
            "input": "Here's a `code snippet` and a [link](http://example.com).",
            "expected": "Here's a code snippet and a link."
        },
        {
            "input": "**Bold text** with __more bold__ and *italic* with _more italic_.",
            "expected": "Bold text with more bold and italic with more italic."
        },
        {
            "input": "```\ncode block\n```\nRegular text.",
            "expected": "Regular text."
        },
        {
            "input": "- List item 1\n- List item 2\n1. Numbered item",
            "expected": "List item 1\nList item 2\nNumbered item"
        },
        {
            "input": "> Blockquote text\nRegular text after.",
            "expected": "Blockquote text\nRegular text after."
        },
        {
            "input": "---\nHorizontal rule above\n***\nAnother rule",
            "expected": "Horizontal rule above\nAnother rule"
        },
        {
            "input": "**Complex** example with `inline code`, [links](url), and\n- Lists\n- Items",
            "expected": "Complex example with inline code, links, and\nLists\nItems"
        },
        {
            "input": "No markdown here, just plain text.",
            "expected": "No markdown here, just plain text."
        },
        {
            "input": "",
            "expected": ""
        },
        {
            "input": None,
            "expected": None
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case["input"]
        expected = test_case["expected"]
        
        try:
            result = strip_markdown(input_text)
            
            if result == expected:
                print(f"✓ Test {i}: PASSED")
                passed += 1
            else:
                print(f"✗ Test {i}: FAILED")
                print(f"  Input:    '{input_text}'")
                print(f"  Expected: '{expected}'")
                print(f"  Got:      '{result}'")
                print()
        except Exception as e:
            print(f"✗ Test {i}: ERROR - {e}")
            print(f"  Input: '{input_text}'")
            print()
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All markdown stripping tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")

def test_real_world_examples():
    """Test with real-world markdown examples that might come from Gemini"""
    print("\n=== Real-World Examples Test ===\n")
    
    real_examples = [
        "**My Approach (If I had the Images):**\n\n1. **Chronological Ordering:** I would arrange the scenes...",
        "Here's what I found:\n\n- **Person:** John Smith\n- **Location:** Kitchen\n- **Activity:** Cooking",
        "```\nScene 1: 04:24:22 - A woman is asleep in bed\nScene 2: 04:25:22 - The woman is sitting up\n```",
        "**Example (if I were to make up some hypothetical images):**\n\n* **Scene 1:** A woman is asleep...",
        "**To Give You a Proper Description, Please Provide:**\n\n* **Image Files:** (Ideal) If possible...",
    ]
    
    for i, example in enumerate(real_examples, 1):
        print(f"Example {i}:")
        print(f"Original: {repr(example)}")
        cleaned = strip_markdown(example)
        print(f"Cleaned:  {repr(cleaned)}")
        print()

if __name__ == "__main__":
    test_markdown_stripping()
    test_real_world_examples() 