# Address Classification Algorithm

A Python algorithm to classify an input address string into wards, districts, and provinces.

## Features
- Parses raw address text and categorizes it into administrative levels (wards, districts, provinces).
- Handles misspellings, not case sensitive.
- Supports Vietnamese address structures (can be adapted for other regions).
- Optimized for fast lookup using Trie/Dictionary-based structures.

## Current limitation:
- Ward, District, Province are handled separately. Sometimes can return wards that's not actually within given province.
- Unable to cover misspelling all word components in the province/ district/ ward names
