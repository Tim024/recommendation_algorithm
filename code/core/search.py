from code.interface.models import *

def search(person_name,all_places):
    def get_all_reviews(person,minimum_stars):
        o = []
        ostr = []
        for p in all_places:
            for r in p.reviews:
                if r.owner == person and r.score >= minimum_stars:
                    o.append(r)
                    ostr.append(str(r))
        print(f"getting all reviews > {minimum_stars} of {person}: {ostr}")
        return o
    def get_all_persons(place,minimum_stars):
        o = []
        for p in all_places:
            if p.name == place.name:
                for r in p.reviews:
                    if r.score >= minimum_stars and r.owner != person_name:
                        o.append(r.owner)
        print(f"getting all persons with review > {minimum_stars} of {place.name}: {o}")
        return o

    #search 4.5 star ratings
    ms = 4.5
    good_reviews = get_all_reviews(person_name,ms)
    #for each place, list person who put 4.5 stars
    all_ppl_matches_r1 = set()
    for gr in good_reviews:
        ppl_match = get_all_persons(gr.place,ms)
        for p in ppl_match:
            all_ppl_matches_r1.add(p)
    places_r1 = set()
    for p in all_ppl_matches_r1:
        good_reviews_r1 = get_all_reviews(p,ms)
        for gr1 in good_reviews_r1:
            places_r1.add(gr1.place)
    print("places r1",[str(p) for p in places_r1])
    #iter again on the eprson with decreasing weight
