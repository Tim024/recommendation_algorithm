# Import your newly installed selenium package
from selenium import webdriver

def get_places_from_user(url):
    driver = webdriver.Chrome()
    driver.get(url)

    driver.close()

testuser = 'https://www.google.com/maps/contrib/113840797516007487166/reviews/@45.0499787,3.9400393,6z?hl=en-NL'