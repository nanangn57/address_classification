class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False
        self.original_word = []

class PrefixTree:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, origin_word) -> None:
        curr = self.root
        for c in word:
            if c not in curr.children:
                curr.children[c] = TrieNode()
            curr = curr.children[c]
        curr.end = True
        if origin_word not in curr.original_word:
            curr.original_word.append(origin_word)

    def search(self, word: str) -> bool:
            curr = self.root
            for c in word:
                if c not in curr.children:
                    return False, None
                curr = curr.children[c]
            return curr.end, curr.original_word

    def isContain(self, word):
            curr = self.root
            for char in word:
                if char not in node.children:
                    return False
                node = node.children[char]
            return curr.end


