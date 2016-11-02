import csv
import math

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

#takes User ID, and returns corresponding nearest neighbor
def find_nearest_neighbor(user_dict_list,current_user):
  nearest_neighbor = -1
  current_user -=1 #index in list is user_id - 1 
  best_euclidean_distance = float('inf')
  for i in range(len(user_dict_list)):
    #if not same as current user, calculate euclidean distance
    if i!=current_user:
      euclidean_distance = 0
      common = 0
      for movie in user_dict_list[i]:
        #if both have rated the same movie
        if movie in user_dict_list[current_user]:
          # used to check that there is at least one movie in common
          common += 1
          euclidean_distance+= math.sqrt((user_dict_list[i][movie] - user_dict_list[current_user][movie])**2)
      #check if best neighbor yet (with at least five movie matches)
      if common > 4:
        euclidean_distance /= common 
        if euclidean_distance < best_euclidean_distance:
          best_euclidean_distance = euclidean_distance
          nearest_neighbor = i
  #return User ID of nearest neighbor
  return nearest_neighbor+1

def main():
  #get list of user dicts mapping movie_ids to ratings
  user_dict_list = load_data()
  print(user_dict_list)
  #use 1-nn (euclidean distance) to find nearest neighbor for ID 1
  nearest_neighbor = find_nearest_neighbor(user_dict_list,1)
  print("User ID of Nearest neighbor of 1 is: ")
  print(nearest_neighbor)

if __name__ == "__main__":
  main()