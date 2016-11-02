import csv

#creates a list of dicts, one dict for each user, with movie_id as key and rating as value
def load_data():
  user_dict_list = []
  with open('ratings.csv', 'rb') as movie_ratings_file:
    reader = csv.reader(movie_ratings_file, delimiter=',')
    for count in range(1,672):
      user_dict={}
      next(reader, None)  # skip the headers
      for row in reader:
        if(int(row[0])==count):
          user_dict[int(row[1])]=float(row[2])
      count+=1
      user_dict_list.append(user_dict)
      movie_ratings_file.seek(0)
  return user_dict_list

def main():
  #get list of user dicts mapping movie_ids to ratings
  user_dict_list = load_data()
  print(user_dict_list)

if __name__ == "__main__":
  main()