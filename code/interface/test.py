import random
from code.interface.models import *
from code.core.search import *

class FakeMap:
    def __init__(self):
        self.all_places = []
        for place_id in range(100):
            all_reviews = []
            r1 = random.randint(1,30)
            ts = 0
            for review_id in range(r1):
                s = random.choice([1,2,3,4,5])
                ts += s
                all_reviews.append(Review(random.choice(['A','B','C','D','E','F','G','H','I','TEST']),s,'review number'+str(review_id)))
            self.all_places.append(Place('place'+str(place_id),ts/r1,all_reviews))
            
    def search(self):
        search('TEST',self.all_places)


if __name__ == "__main__":
    FM = FakeMap()
    FM.search()

