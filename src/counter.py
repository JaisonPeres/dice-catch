class Counter:
    def __init__(self, max_count: int):
        self.max_count = max_count
        self.count = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1

    def get_count(self):
        return self.count
    
    def is_max(self):
        return self.count == self.max_count
    
    def get_max(self):
        return self.max_count
    
    def reset(self):
        self.count = 0
        return self.count