import csv
import math
import sys

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

#Takes train set, test set, current user ID, and returns 1nn and his ratings for the common test set movies.
def find_nearest_neighbor(user_dict_list,current_user,train_set,test_set):
  nearest_neighbor = -1
  current_user -=1 #index in list is user_id - 1 
  best_euclidean_distance = float('inf')
  for i in range(len(user_dict_list)):
    #if not same as current user, calculate euclidean distance
    if i!=current_user:
      euclidean_distance = 0
      common_train = 0
      common_test = 0
      for movie in user_dict_list[i]:
        #if both have rated the same movie
        if movie in train_set:
          # used to check that there is at least one movie in common
          common_train += 1
          euclidean_distance+= math.sqrt((user_dict_list[i][movie] - user_dict_list[current_user][movie])**2)
        #check if it has any common test_set movies as well
        elif movie in test_set:
          common_test +=1
      #check if best neighbor yet (with at least five movie matching in train set and at least two in test set)
      if common_train > 4 and common_test > 1:
        euclidean_distance /= common_train
        if euclidean_distance < best_euclidean_distance:
          best_euclidean_distance = euclidean_distance
          nearest_neighbor = i
  #return User ID of nearest neighbor
  return nearest_neighbor+1

#splits the user's ratings into 70-30 train and test set
def train_test_split(user_dict_list,current_user):
  #get index
  current_user -=1
  train = {}
  test = {}
  train_end_index = math.floor(0.7*len(user_dict_list[current_user]))
  count = 0
  current_user_dict = user_dict_list[current_user] 
  for key in current_user_dict:
    if count < train_end_index:
      train[key] = current_user_dict[key]
    else:
      test[key] = current_user_dict[key]
    count+=1
  return train, test

def find_mean_squared_error(nearest_neighbor_dict, test_set):
  sum_of_squares = 0
  count = 0
  print("Predictions using this neighbor for test set are: ")
  for movie in test_set:
    if movie in nearest_neighbor_dict:
      print("Predicted rating for movie " + str(movie) + ": "+str(nearest_neighbor_dict[movie]))
      print("Actual rating for movie " + str(movie) + ": "+str(test_set[movie]))
      sum_of_squares += (nearest_neighbor_dict[movie] - test_set[movie])**2
      count +=1
  mean_squared_error = sum_of_squares/float(count)
  return mean_squared_error


def main():
  #get list of user dicts mapping movie_ids to ratings
  user_dict_list = load_data()

  #take user_id is input and output the predictions on some subset of his ratings, and the error rate on the same
  user_id = int(sys.argv[1])

  #split ID 1's movies into train and test set (each of train and test will be a dict with some movies and their ratings)
  train_set, test_set = train_test_split(user_dict_list,user_id)

  #find an nn that has rated >4 movies in the train set and >1 movies in the test set as well
  nearest_neighbor = find_nearest_neighbor(user_dict_list, user_id, train_set, test_set)

  print("User ID of Nearest neighbor of 1 is: ")
  print(nearest_neighbor)

  #check squared error with predictions made by nearest neighbor on test_set common movies
  nearest_neighbor_dict = user_dict_list[nearest_neighbor-1]
  mean_squared_error = find_mean_squared_error(nearest_neighbor_dict, test_set)
  print("Mean squared error = " + str(mean_squared_error))

if __name__ == "__main__":
  main()