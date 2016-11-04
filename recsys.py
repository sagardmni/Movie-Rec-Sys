import csv
import math
import sys

#creates a list of dicts, one dict for each user, with movie_id as key and rating as value
def load_data():
  user_dict_list = []
  average_rating = 0
  count = 0

  with open('ratings.csv', 'rb') as movie_ratings_file:
    reader = csv.reader(movie_ratings_file, delimiter=',')
    next(reader, None)  # skip the headers

    previous = 1
    user_dict = {}
    for row in reader:
      if(int(row[0])==previous):
        user_dict[int(row[1])]=float(row[2])
      else:
        previous = int(row[0])
        user_dict_list.append(user_dict)
        user_dict = {}
        user_dict[int(row[1])]=float(row[2])
      average_rating += float(row[2])
      count+=1
    user_dict_list.append(user_dict)
  average_rating /= count
  return user_dict_list, average_rating

#Generates predictions on test_set using k nearest neighbors
def find_k_nearest_neighbor(user_dict_list,current_user,train_set,test_set,average_rating):

  #index in list is user_id - 1
  current_user -=1 
  
  nearest_neighbor_dict = {movie: [] for movie in test_set}
  super_dict = {movie: {} for movie in test_set}
  dict_of_euclidean_distances = {}

  for i in range(len(user_dict_list)):
    #if not same as current user, calculate euclidean distance
    if i!=current_user:
      euclidean_distance = 0
      common_train = 0
      for movie in user_dict_list[i]:
        #if both have rated the same movie
        if movie in train_set:
          euclidean_distance+= math.sqrt((user_dict_list[i][movie] - user_dict_list[current_user][movie])**2)
          common_train+=1
        #check if movie is in test_set of current_user
        elif movie in test_set:
          nearest_neighbor_dict[movie].append(i)

      #add to dict of euclidean distances if at least 3 movies from train_set common
      if common_train > 3:
        euclidean_distance /= common_train
        dict_of_euclidean_distances[i] = euclidean_distance
      else: dict_of_euclidean_distances[i] = float('inf')

  #combine nearest_neighbor_dict and dict_of_euclidean_distances into a dict of dicts. The key of the top-level dict is the movie_id,
  #its value is a dict comprising of users as keys and euclidean distances as values, where the key corresponding to the user is only
  #present in the dict of the user has rated the movie corresponding to the key of the top-level dict.

  for movie in nearest_neighbor_dict:
    for user in nearest_neighbor_dict[movie]:
      super_dict[movie][user] = dict_of_euclidean_distances[user]

  for movie in super_dict:
    while(len(super_dict[movie]) > 3):
      key_to_delete = max(super_dict[movie], key=lambda k: super_dict[movie][k])
      del super_dict[movie][key_to_delete]

  #get average predicted ratings
  predicted_ratings = {}
  for movie in super_dict:
    average = 0
    count = 0
    for user in super_dict[movie]:
      average+= user_dict_list[user][movie]
      count +=1
    if count > 0:
      average /= count
    #no such users
    else: average = average_rating
    predicted_ratings[movie] = average

  # print(predicted_ratings)
  return predicted_ratings

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

def find_mean_squared_error(user_dict_list,predicted_ratings, test_set, average_rating):
  sum_of_squares = 0
  count = 0
  for movie in test_set:
    if movie in predicted_ratings:
      predicted_rating = predicted_ratings[movie]
    #movie not seen by anyone else, arbitrary rating  
    else:
      predicted_rating = average_rating
    # print("Predicted rating for movie " + str(movie) + ": "+str(predicted_rating))
    # print("Actual rating for movie " + str(movie) + ": "+str(test_set[movie]))
    sum_of_squares += (predicted_rating - test_set[movie])**2
    count +=1
  mean_squared_error = sum_of_squares/float(count)
  return mean_squared_error

def find_squared_error_without_nn(test_set,average_rating):
  sum_of_squares = 0
  count = 0
  for movie in test_set:
    predicted_rating = average_rating
    sum_of_squares += (predicted_rating - test_set[movie])**2
    count+=1
  mean_squared_error = sum_of_squares/float(count)
  return mean_squared_error

def main():

  #get list of user dicts mapping movie_ids to ratings
  user_dict_list, average_rating = load_data()

  win = 0
  loss = 0
  for user_id in range(1,672):
    #split ID 1's movies into train and test set (each of train and test will be a dict with some movies and their ratings)
    train_set, test_set = train_test_split(user_dict_list,user_id)

    #Find a list of nearest_neighbors such that we have a nearest_neighbor for each movie in test_set
    predicted_ratings = find_k_nearest_neighbor(user_dict_list, user_id, train_set, test_set,average_rating)

    #check squared error with predictions made by nearest neighbors on test_set movies
    mean_squared_error = find_mean_squared_error(user_dict_list, predicted_ratings, test_set, average_rating)
    print("Mean squared error = " + str(mean_squared_error))

    #now do a comparison against using the mean as prediction for all movies in the test_set
    squared_error_without_nn = find_squared_error_without_nn(test_set,average_rating)
    print("Mean squared error without using NN is " + str(squared_error_without_nn))

    if squared_error_without_nn > mean_squared_error:
      win+=1
    else: loss +=1
  win_percentage = ((win)/float(win+loss))*100
  print("Win percentage = "+ str(win_percentage))

  #use 3 nearest neighbors rather than a single neighbor to predict.

if __name__ == "__main__":
  main()