from bs4 import BeautifulSoup
import requests
import re
#import webbrowser

def get_soup(url):
    
    s = requests.Session()

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}

    r = s.get(url, headers=headers)

    #with open('temp.html', 'wb') as f:
    #    f.write(r.content)
    #    webbrowser.open('temp.html')

    if r.status_code != 200:
        print('status code:', r.status_code)
    else:
        return BeautifulSoup(r.text, 'html.parser')

def parse_member_restaurants(name,b='4',loc='-1'):
    o = []
    if ' ' in name:
        return o
    url = 'https://www.tripadvisor.com/members-reviews/'+name
    response = get_soup(url)
    #print('memeber:',url)
    if not response:
        print('no response:', url)
        return o
    #only get reviews of first page because cs #TODO
    for idx, review in enumerate(response.find_all('li', class_='cs-review')):
        pts = review.find('a')['href']
        url_ = 'https://www.tripadvisor.com'+pts
        rating = review.select_one('span.ui_bubble_rating')['class'][1][7]
        locin = True if '-g'+loc in pts else False
        #print('url:', url_)
        #print(pts,rating,b,loc)
        if locin and int(rating) >= int(b):
            o += parse_restaurant(url_)
    return o


    def parse_restaurant(url):
        response = get_soup(url)
    o = []
    if not response:
        print('no response:', url)
        return o
    try:
        # get number of reviews
        num_reviews = response.find('span', class_='reviews_header_count').text
        num_reviews = num_reviews[1:-1] # remove `( )`
        num_reviews = num_reviews.replace(',', '') # remove `,`
        num_reviews = int(num_reviews)
        # print('num_reviews:', num_reviews, type(num_reviews))

        # create template for urls to pages with reviews
        url = url.replace('.html', '-or{}.html')
        #print('template:', url)

        # load pages with reviews
        for offset in range(0, num_reviews, 10): #10 by 10 ?
            #print('url:', url.format(offset))
            url_ = url.format(offset)
            o += parse_restaurant_reviews(url_, get_soup(url_))
            #break #TODO remove stop
    except Exception as e:
        print(e)
    return o


def parse_restaurant_reviews(url, response):
    o = []
    #print('review:', url)

    if not response:
        print('no response:', url)
        return


    if 'Restaurant_Review' not in url:
        return o
    restaurant_page = url.split('Restaurant_Review')[1].split('.html')[0]

    # get every review
    for idx, review in enumerate(response.find_all('div', class_='review-container')):
        #print(idx,review)
        item = {
            #'hotel_name': response.find('h1', class_='heading_title').text,
            #'review_title': review.find('span', class_='noQuotes').text,
            #'review_body': review.find('p', class_='partial_entry').text,
            'review_date': review.find('span', class_='ratingDate')['title'],#.text,#[idx],
            #'num_reviews_reviewer': review.find('span', class_='badgetext').text,
            'reviewer_name': review.find('span', class_='expand_inline scrname').text,
            'bubble_rating': review.select_one('span.ui_bubble_rating')['class'][1][7:],
            'page':restaurant_page
        }

        o.append(item)

        #~ yield item
        #for key,val in item.items():
        #    print(key, ':', val)
    return o


# --- main ---
# restaurant_urls = [
#     'https://www.tripadvisor.com/Restaurant_Review-g1064253-d10750060-Reviews-Ca_Mario-Telde_Gran_Canaria_Canary_Islands.html',
#     #'https://www.tripadvisor.com/Hotel_Review-g60795-d102542-Reviews-Courtyard_Philadelphia_Airport-Philadelphia_Pennsylvania.html',
#     #'https://www.tripadvisor.com/Hotel_Review-g60795-d122332-Reviews-The_Ritz_Carlton_Philadelphia-Philadelphia_Pennsylvania.html',
# ]
#
# results = [] # <--- global list for items
#
# #for url in restaurant_urls:
# #    results += parse_restaurant(url)
#
# print(results)
#
# print(parse_member_restaurants('JohnGrahamUK',b='4',loc='186338')) #returns all user reviews of reviews >= b of member, in location loc
#location = g tag of url

#search function:
name = 'JohnGrahamUK'
minrating = '4'
loc = '186338' #london
results_iter1 = parse_member_restaurants(name,minrating,loc)
selected_places = {}
for r in results_iter1:
    if int(r['bubble_rating'])>=10*int(minrating) and '-g'+loc in r['page']:
        try:selected_places[r['page']] += 1
        except: selected_places[r['page']] = 1

print('ITER 1')
print(sorted(selected_places, key=selected_places.get))

# for r in results_iter1:
#     results_iter2 = parse_member_restaurants(r['reviewer_name'],minrating,loc)
#     for r2 in results_iter2:
#         if int(r2['bubble_rating'])>=10*int(minrating) and '-g'+loc in r2['page']:
#             try:selected_places[r2['page']] += 1
#             except: selected_places[r2['page']] = 1
#
# print('ITER 2')
# print(sorted(selected_places, key=selected_places.get))