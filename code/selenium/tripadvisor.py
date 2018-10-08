from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import numpy as np

WINDOW_SIZE = "1024,4096"

chrome_options = Options()
#chrome_options.add_argument("--headless")
#chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

def get_reviews_from_user(user):
    ''' Returns all reviews from a user. Selenium is required here to
    change pages and click on the webpage since it is dynamic content management.'''
    def source_to_dict(page_source):
        ''' From page soruce (html), returns a list of reviews [{place:place_href, rating:rating},...]'''
        output = {}
        parsed = BeautifulSoup(page_source, 'html.parser')
        #print(i, "FOUND", len(parsed.find_all('li', class_='cs-review')))
        for idx, review in enumerate(parsed.find_all('li', class_='cs-review')):
            place = review.find('a')['href']
            #print(place)
            rating = int(review.select_one('span.ui_bubble_rating')['class'][1][7]) * 100 / 5.0  # rating in percent

            try: output[place].append(rating)
            except KeyError: output[place] = [rating]

        return output

    assert ' ' not in user #TODO better url check

    all_reviews = {}
    url = 'https://www.tripadvisor.com/members-reviews/'+str(user)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    try:
        driver.get(url)
        time.sleep(3) # sleep time required for the page to load, otherwise we scrape the previous page
        total_reviews = int(driver.find_element_by_xpath('//*[@id="MODULES_MEMBER_CENTER"]/div[1]/div[2]/div/ul/li[1]/a').text.split(' ')[0])
        print("Scraping ",total_reviews,'reviews from',user) #TODO not all reviews are scraped ?
        all_reviews = {**all_reviews, **source_to_dict(driver.page_source)}
        while(True):
            try: driver.find_element_by_xpath('//*[@id="cs-paginate-next"]').click()
            except: break
            time.sleep(3)
            all_reviews = {**all_reviews, **source_to_dict(driver.page_source)}
            # driver.get_screenshot_as_file("capture"+str(i)+".png")
    finally:
        driver.close()
    return all_reviews

def get_users_from_place(place_href):
    ''' Returns all users that have reviewed this place.
    argument place_href is of form: /Attraction_Review-g187147-d188151-Reviews-Eiffel_Tower-Paris_Ile_de_France.html'''
    all_users = set()
    url = 'https://www.tripadvisor.com' + str(place_href)

    driver = webdriver.Chrome(chrome_options=chrome_options)
    try:
        driver.get(url)
        time.sleep(1) # sleep time required for the page to load, otherwise we scrape the previous page
        driver.find_element_by_xpath('//*[@id="taplc_location_review_filter_controls_0_filterLang_ALL"]').click()#get reviews in all langages

        time.sleep(4)
        #scrap all reviews, get users, click next and repeat
        # parsed = BeautifulSoup(driver.page_source, 'html.parser')
        #for idx, review in enumerate(parsed.find_all('div', class_='review-container')):
        #    print(idx,review)
        #print(driver.find_elements_by_xpath("//*[contains(text(), 'expand_inline srcname ')]") #//*[@id="UID_1C5361910FC816E6EBED014375CB355C-SRC_615662064"]/div[2]/span)
        #TODO implement this
        print("Not implemented yet")

    finally:
        driver.close()

    return all_users

def get_similarity_score(reviews_user_1,reviews_user_2):
    ''' Returns similarity score between to review lists of different users.
    Similarity score is in [0,+inf]
    Perfect similarity is 0, no similarity is 100, anti-similarity is greater than 100
    '''
    ACCEPTABLE_RATING_DIFFERENCE = 15
    similarity_score = 0
    comparable_places = 0
    # Review users is of format {place:[ratings]}
    for place,ratings in reviews_user_1.items():
        if place in reviews_user_2.keys():
            print("They have reviewed the same place",ratings,reviews_user_2[place])
            rating_difference = ((np.mean(ratings)-np.mean(reviews_user_2[place]))/ACCEPTABLE_RATING_DIFFERENCE)**2
            #rating difference is > 1 if the diff between rating is above the acceptable difference
            similarity_score += rating_difference
        # else:
        #     similarity_score += 1 #TODO consider places that have not been visited by both ?
            comparable_places += 1

    # Perfect similarity is 0, no similarity is 100, anti-similarity is greater than 100
    return 100*similarity_score/comparable_places

SIMILARITY_THRESHOLD = 85 # Similarity threshold for the similarity score

MIN_RATING = 80 # Minimum rating in percent of a good place

def recommendation_algorithm(username,location_gtag):
    ''' The actual recommendation algorithm. Prints list of recoomendation as it computes.'''
    def get_similar_users(user_reviews):
        '''  Returns list of similar users [{'user':user,'reviews':[]}], (according to the
         similarity score) by looking at all users having commented on the same places as in user_reviews.'''
        potential_similar_users = []
        similar_users = []
        for r in user_reviews:
            potential_similar_users += get_users_from_place(r['place'])
        for u in potential_similar_users:
            ru = get_reviews_from_user(u)
            if (get_similarity_score(ru, user_reviews) > SIMILARITY_THRESHOLD):
                similar_users.append({'user':u,'reviews':ru})
        return similar_users
    def print_recommendations(user_reviews_list, loc):
        ''' Print recommendations. Places that are well reviewed by most similar users are
        considered, as well as the location we are interested in.
        Input: list of user:reviews and location (-g number in the href)'''

        recommendations = {} # Format = {place: number of time it has been recommended}
        for ur in user_reviews_list:
            for r in ur['reviews']:
                if r['rating']>MIN_RATING and '-g'+str(loc) in r['place']:
                    try: recommendations[r['place']] += 1
                    except: recommendations[r['place']] = 1

        # Sort recommendations by most recommended first
        recommendations = sorted(recommendations, key=recommendations.get)
        print(recommendations)
        return recommendations

    reviews = get_reviews_from_user(username)
    similar_users = get_similar_users(reviews)
    # end iteration 1: we got similar users from original user so we can compute first approx (recoupement good places)
    similar_users.append({'user':username,'reviews':reviews})
    print_recommendations(similar_users,location_gtag)

    # start iteration 2: look into similar users of similar users, and put them with lower weight
    # for u in similar_users:
    #     reviews = get_reviews_from_user(u)
    #     similar_users = get_similar_users(reviews)
    #     print_recommendations(username, similar_users, location_gtag) #TODO ?



if __name__ == '__main__':
    # Test get all users from place page
    r = get_users_from_place('/Restaurant_Review-g34467-d393249-Reviews-Baleen_Naples-Naples_Florida.html')
    print(len(r))
    print(r)
    exit(1)


    # Test get reviews from user:
    r = get_reviews_from_user('DavidBS')
    print(len(r))
    # for k,v in r.items():
    #     print(k,v)

    # Test similarity score
    r2 = get_reviews_from_user('msusandel')
    s = get_similarity_score(r,r2)
    print(s)