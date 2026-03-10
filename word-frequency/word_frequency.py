#!/usr/bin/env python3
"""
Simple Word Frequency Analyzer.

This script reads a text file and shows the 10 most common words.
It works with English and Spanish text, including accents and ñ.
"""

import re
import sys
from collections import Counter


def clean_text(text):
    """
    Clean the raw text before analyzing it.

    We remove punctuation and special characters but keep letters and spaces.
    This also supports Spanish characters like á, é, ñ, ü, etc.

    Finally, everything is converted to lowercase so that words like
    "Hello" and "hello" are counted as the same word.
    """

    # Remove punctuation and special characters
    # Keep only letters and whitespace
    cleaned = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)

    # \w also includes numbers and underscores, which we don't want
    cleaned = re.sub(r'[\d_]', '', cleaned)

    return cleaned.lower()


def count_words(text):
    """
    Split the cleaned text into words and count how many times
    each one appears.

    Counter works like a dictionary where:
    key   = word
    value = number of occurrences
    """
    words = text.split()
    return Counter(words)


def display_top_words(word_counter, top_n=10):
    """
    Print the most frequent words in a simple formatted list.
    """

    print(f"\nTop {top_n} most frequent words:")
    print("-" * 40)

    for i, (word, count) in enumerate(word_counter.most_common(top_n), 1):
        print(f"{i:2d}. {word:<20} : {count:>5} occurrences")


def main():
    # Make sure the user provided a file path
    if len(sys.argv) != 2:
        print("Usage: python word_frequency.py <text_file>")
        print("Example: python word_frequency.py sample.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # Read the entire file
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        # If the file is empty, stop early
        if not text.strip():
            print("Error: The file is empty or contains only whitespace.")
            sys.exit(1)

        # Prepare the text and count word frequencies
        cleaned_text = clean_text(text)
        word_counter = count_words(cleaned_text)

        # Basic statistics about the text
        total_words  = sum(word_counter.values())
        unique_words = len(word_counter)

        print(f"\nWord Frequency Analysis for: {input_file}")
        print(f"Total words processed : {total_words}")
        print(f"Unique words found    : {unique_words}")

        # Show the most common words
        display_top_words(word_counter)

        # Some additional stats just for extra insight
        most_common_word, most_common_count = word_counter.most_common(1)[0]

        print(f"\nAdditional Statistics:")
        print(f"- Average word frequency : {total_words / unique_words:.2f}")
        print(f"- Most common word       : '{most_common_word}' ({most_common_count} times)")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    except PermissionError:
        print(f"Error: No permission to read '{input_file}'.")
        sys.exit(1)

    except Exception as e:
        # Catch any unexpected error so the script doesn't crash silently
        print(f"Error: Something went wrong: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()