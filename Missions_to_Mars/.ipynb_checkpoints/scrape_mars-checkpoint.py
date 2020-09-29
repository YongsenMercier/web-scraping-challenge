import time
import pandas as pd
import requests as req
from bs4 import BeautifulSoup as bs
from splinter import Browser


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()

    #
    ### NASA Mars News 
    #

    # Visit url for NASA Mars News -- Latest News
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html = browser.html

    # Parse HTML with Beautiful Soup  
    soup = bs(html, "html.parser")

    # Get article title and paragraph text
    article = soup.find("div", class_='list_text')
    news_title = article.find("div", class_="content_title").text
    news_p = article.find("div", class_ ="article_teaser_body").text

    #
    ### JPL Mars Space Images
    #

    # Visit url for JPL Featured Space Image
    image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)

    # Go to 'FULL IMAGE'
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)

    # Go to 'more info'
    browser.click_link_by_partial_text('more info')

    # Parse HTML with Beautiful Soup
    html = browser.html
    image_soup = bs(html, "html.parser")

    # Get featured image
    feat_img_url = image_soup.find('figure', class_='lede').a['href']
    featured_image_url = f'https://www.jpl.nasa.gov{feat_img_url}'

   
    # Visit Mars Facts webpage for interesting facts about Mars
    mars_facts_url = "https://space-facts.com/mars/"
    browser.visit(mars_facts_url)
    html = browser.html

    # Use Pandas to scrape the table containing facts about Mars
    table = pd.read_html(mars_facts_url)
    mars_facts = table[1]
    mars_facts = mars_facts.drop(['Earth'],axis = 1)
    
    # Rename columns
    mars_facts.columns = ['Description','Value']

    # Reset Index to be description
    mars_facts = mars_facts.set_index('Description')

    # Use Pandas to convert the data to a HTML table string
    mars_facts2 = mars_facts.to_html(index = True, header =True)

    #
    ### Mars Hemispheres
    #

    # Visit USGS webpage for Mars hemispehere images
    hemispheres_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemispheres_url)
    html = browser.html

    # Parse HTML with Beautiful Soup
    soup = bs(html, "html.parser")

    # Create dictionary to store titles & links to images
    hemisphere_image_urls = []

    # Retrieve all elements that contain image information
    results = soup.find("div", class_ = "result-list" )
    hemispheres = results.find_all("div", class_="item")

    # Iterate through each image
    for hemisphere in hemispheres:
        title = hemisphere.find("h3").text
        image_link = hemisphere.find("a")["href"]
        image_url = "https://astrogeology.usgs.gov" + image_link
        browser.visit(image_url)
        html = browser.html
        soup = bs(html, "html.parser")
        image_download = soup.find("div", class_ = "downloads")
        final_image = image_download.find("a")["href"]
        hemisphere_image_urls.append({"Title": title, "Img_url": final_image})

    #
    ### Store Data
    #

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_facts": mars_facts2,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data

if __name__ == '__main__':
    scrape()