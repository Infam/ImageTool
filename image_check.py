##A script that checks if images in a given folder are the highest quality/resolution that can be found by SauceNao.

#Loop through images in folder
#Get resolution
#search online for matching image
#   If error, report
#   if no confident match, report and display highest.
#   If image
#        no image booru link
#            search pixiv link -> pixiv api get resolution
#        booru link
#            danbooru api -> resolution
#                catch errors
#            gelbooru api -> resolution
#                catch errors
#
#        if resolution match
#            move image to diff folder
#        else download?
#
#TODO check dupes?

#Requires Python 3+, Requests, and Pillow from saucenao's example implementation

################################### Basic Settings

checkfolderpath = './Check/*' #Directory of images to check
movefolderpath = '~/Pictures/Unsorted/*' #If images are fine, move here
rename = True

#### SauceNao Settings
api_key = "makeurown" #Create account for key
output_type = '2' #From Website: 0=normal html 1=xml api(not implemented) 2=json api
minsim = '80!' #Minimal similarity
numres = '1' #Number of results requested

################################### Imports

import glob
import requests
from PIL import Image
import io
import json 


################################### Indexes copied from saucenao example

                                     #Index_id
index_hmags='0'                       #0
index_reserved='0'                    #1
index_hcg='0'                         #2
index_ddbobjects='0'                  #3
index_ddbsamples='0'                  #4
index_pixiv='1'                       #5
index_pixivhistorical='1'             #6
index_reserved='0'                    #7
index_seigaillust='0'                 #8
index_danbooru='1'                    #9
index_drawr='0'                       #10
index_nijie='0'                       #11
index_yandere='0'                     #12
index_animeop='0'                     #13
index_reserved='0'                    #14
index_shutterstock='0'                #15
index_fakku='0'                       #16
index_hmisc='0'                       #17
index_2dmarket='0'                    #18
index_medibang='0'                    #19
index_anime='0'                       #20
index_hanime='0'                      #21
index_movies='0'                      #22
index_shows='0'                       #23
index_gelbooru='1'                    #24
index_konachan='0'                    #25
index_sankaku='0'                     #26
index_animepictures='0'               #27
index_e621='0'                        #28
index_idolcomplex='0'                 #29
index_bcyillust='0'                   #30
index_bcycosplay='0'                  #31
index_portalgraphics='0'              #32
index_da='0'                          #33
index_pawoo='0'                       #34
index_madokami='0'                    #35
index_mangadex='0'                    #36

###################################

db_bitmask = int(index_mangadex+index_madokami+index_pawoo+index_da+index_portalgraphics+index_bcycosplay+index_bcyillust+index_idolcomplex+index_e621+index_animepictures+index_sankaku+index_konachan+index_gelbooru+index_shows+index_movies+index_hanime+index_anime+index_medibang+index_2dmarket+index_hmisc+index_fakku+index_shutterstock+index_reserved+index_animeop+index_yandere+index_nijie+index_drawr+index_danbooru+index_seigaillust+index_anime+index_pixivhistorical+index_pixiv+index_ddbsamples+index_ddbobjects+index_hcg+index_hanime+index_hmags,2) #Create bitmask. Taken from saucenao example

url = 'http://saucenao.com/search.php?output_type='+output_type+'&numres='+numres+'&minsim='+minsim+'&dbmask='+str(db_bitmask)+'&api_key='+api_key

def search():
    imglist = glob.glob(checkfolderpath)
    if len(imglist) == 0:
        print("Cannot find folder or no images present.")
        return
 
    for imgpath in imglist:
        print("Checking "+imgpath+"...")

        #Image conversion and stuff
        img = Image.open(imgpath, mode='r')
        print("Image Height x Width: ",img.height," x ",img.width)
        imageData = io.BytesIO()
        img.save(imageData, format='PNG')
        files = {'file': ("image.png", imageData.getvalue())}
        imageData.close()

        r = requests.post(url, files=files)

        if r.status_code == 403:
            print('Incorrect or Invalid API Key! Please Edit Script to Configure...')
        #Other error codes

        #Got results
        results = r.json() #results are returned & sorted by highest similarity first

        #Check if index miss
        if results['header']['status'] > 0:
            print('One or more indexes failed. Skipping.')
            continue

        #Check if similarity too low
        if results['results'][0]['header']['similarity'] < minsim:
            print('No high confidence results for '+imgpath+'. Going next...')
            continue

        #Get url
        postid = results['results'][0]['data']['danbooru_id']
        r = requests.get('https://danbooru.donmai.us/posts/'+str(postid)+'.json')
        results = r.json()
        print("Fetched Image Height x Width: ",results['image_height']," x ",results['image_width'])
        if img.width < results['image_width'] and img.height < results['image_height']:
            print("Better Image Size")

        elif results['file_url'].endswith('png') and imgpath.endswith('jpg'):
            print("Found png when original is jpg")

        elif results['parent_id'] is not None:
            print("Not parent image. Fetching higher url...")



#def download():

if __name__ == "__main__":
    search()
