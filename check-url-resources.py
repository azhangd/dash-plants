import os
import pandas as pd
import requests

count = 100
count_list = []
image_list = []
image_formats = ["image/png", "image/jpeg", "image/jpg"]

# Set relative data path
this_directory = os.path.dirname(__file__)
csv_file = os.path.join(this_directory, 'data', 'usda_plants_filtered.csv')
output = os.path.join(this_directory, 'data', 'usda_plants_filtered_v2.csv')

# Get iterations list
for i in range(1, count+1):
    count_list.append(str(i).zfill(3))

# Load CSV and read column to list
df = pd.read_csv(csv_file, encoding='latin-1')
url_list = df.Symbol.to_list()

# Check if url has image
def is_url_image(image_url):
   r = requests.head(image_url)
   if r.headers["content-type"] in image_formats:
      return True
   return False

# Create CSV with boolean 'has_image' column
def main():
    image_counter = 0
    for i in url_list:
        for j in count_list:
            url = 'https://plants.sc.egov.usda.gov/ImageLibrary/standard/' + i + '_' + j + '_svp.jpg'
            if is_url_image(url):
                image_counter += 1
                print(str(i) + '_' + str(j) + ' True')
                continue
            else:
                print(str(i) + '_' + str(j) + ' False')
                break
        image_list.append(image_counter)
        image_counter = 0
        print(image_list)
    df['has_image'] = image_list
    df.to_csv(output)
    print('Done')

if __name__ == "__main__":
    main()