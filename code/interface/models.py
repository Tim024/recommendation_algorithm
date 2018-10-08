class Place:
    def __init__(self,name,avg_score,reviews):
        self.name = name
        self.avg_score = avg_score
        self.reviews = reviews
        for r in self.reviews:
            r.bind_place(self)
    def __str__(self):
        return self.name
class Review:
    def __init__(self,owner,score,text):
        self.score = score
        self.owner = owner
        self.text = text
        self.place = None
    def bind_place(self,place):
        self.place = place
    def __str__(self):
        return f"R[{self.owner},{self.score},{self.text},{self.place}]"