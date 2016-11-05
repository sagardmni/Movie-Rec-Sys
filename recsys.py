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

#Generates predictions on validation_dict_list using k nearest neighbors with train_dict_list
def find_k_nearest_neighbor(train_dict_list, validation_dict_list,average_rating,k_for_knn):
  predicted_ratings_dict = {}
  for current_user in range(671):
    train_set = train_dict_list[current_user]
    validation_set = validation_dict_list[current_user]

    nearest_neighbor_dict = {movie: [] for movie in validation_set}
    super_dict = {movie: {} for movie in validation_set}
    dict_of_euclidean_distances = {}

    for user in range(len(train_dict_list)):
      if user!= current_user:
        common_train = 0
        euclidean_distance = 0
        for movie in train_dict_list[user]:
          if movie in train_dict_list[current_user]:
            euclidean_distance+= math.sqrt((train_dict_list[user][movie] - train_dict_list[current_user][movie])**2)
            common_train+=1
          if movie in validation_set:
            nearest_neighbor_dict[movie].append(user)
        #add to dict of euclidean distances if at least 3 movies from train_set common
        if common_train > 2:
          euclidean_distance /= common_train
          dict_of_euclidean_distances[user] = euclidean_distance
        else: dict_of_euclidean_distances[user] = float('inf')

    #combine nearest_neighbor_dict and dict_of_euclidean_distances into a dict of dicts. The key of the top-level dict is the movie_id,
    #its value is a dict comprising of users as keys and euclidean distances as values, where the key corresponding to the user is only
    #present in the dict of the user has rated the movie corresponding to the key of the top-level dict.

    for movie in nearest_neighbor_dict:
      for user in nearest_neighbor_dict[movie]:
        super_dict[movie][user] = dict_of_euclidean_distances[user]

    for movie in super_dict:
      while(len(super_dict[movie]) > k_for_knn):
        key_to_delete = max(super_dict[movie], key=lambda k: super_dict[movie][k])
        del super_dict[movie][key_to_delete]

    #get average predicted ratings
    predicted_ratings = {}
    for movie in super_dict:
      average = 0
      count = 0
      for user in super_dict[movie]:
        average+= train_dict_list[user][movie]
        count +=1
      if count > 0:
        average /= count
      #no such users
      else: average = average_rating
      predicted_ratings[movie] = average
    predicted_ratings_dict[current_user] = predicted_ratings
    # print(predicted_ratings)

  return predicted_ratings_dict

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

#splits the user's ratings into 60-20-20 train-validation-test set
def train_validation_test_split(user_dict_list):
  train_dict_list = []
  validation_dict_list = []
  test_dict_list = []
  for current_user in range(671):
    train = {}
    validation = {}
    test = {}
    train_end_index = math.floor(0.6*len(user_dict_list[current_user]))
    validation_end_index = math.floor(0.8*len(user_dict_list[current_user]))
    count = 0
    current_user_dict = user_dict_list[current_user] 
    for key in current_user_dict:
      if count < train_end_index:
        train[key] = current_user_dict[key]
      elif count < validation_end_index:
        validation[key] = current_user_dict[key]
      else:
        test[key] = current_user_dict[key]
      count+=1
    train_dict_list.append(train)
    validation_dict_list.append(validation)
    test_dict_list.append(test)
  return train_dict_list, validation_dict_list, test_dict_list

def find_mean_squared_error(validation_dict_list, predicted_ratings_dict, average_rating):
  sum_of_squares = 0
  count = 0
  for user in range(len(validation_dict_list)):
    validation_set = validation_dict_list[user]
    predicted_ratings = predicted_ratings_dict[user]
    for movie in validation_set:
      if movie in predicted_ratings:
        predicted_rating = predicted_ratings[movie]
      #movie not seen by anyone else, use average rating  
      else:
        predicted_rating = average_rating
      # print("Predicted rating for movie " + str(movie) + ": "+str(predicted_rating))
      # print("Actual rating for movie " + str(movie) + ": "+str(test_set[movie]))
      sum_of_squares += (predicted_rating - validation_set[movie])**2
      count +=1
  mean_squared_error = math.sqrt(sum_of_squares/float(count))
  return mean_squared_error

def find_squared_error_without_nn(validation_dict_list,average_rating):
  sum_of_squares = 0
  count = 0
  for user in range(len(validation_dict_list)):
    validation_set = validation_dict_list[user]
    for movie in validation_set:
      predicted_rating = average_rating
      sum_of_squares += (predicted_rating - validation_set[movie])**2
      count+=1
  mean_squared_error = math.sqrt(sum_of_squares/float(count))
  return mean_squared_error

def main():

  #get list of user dicts mapping movie_ids to ratings
  user_dict_list, average_rating = load_data()

  #split entire set at once rather than splitting on each user
  train_dict_list, validation_dict_list, test_dict_list = train_validation_test_split(user_dict_list)
  previous_mean_squared_error = float('inf')
  predicted_ratings_dict = {}
  
  squared_error_without_nn = find_squared_error_without_nn(validation_dict_list,average_rating)
  print("RMSE without using NN is " + str(squared_error_without_nn))

  for k in range(1,100):
    predicted_ratings_dict = find_k_nearest_neighbor(train_dict_list, validation_dict_list,average_rating,k)

    mean_squared_error = find_mean_squared_error(validation_dict_list, predicted_ratings_dict, average_rating)
    print("RMSE with k= " + str(k) + " is " +str(mean_squared_error))

    if mean_squared_error > previous_mean_squared_error:
      break
    previous_mean_squared_error = mean_squared_error
    
  #check on test set using chosen k
  k -=1
  predicted_ratings_dict = find_k_nearest_neighbor(train_dict_list, test_dict_list,average_rating,k)
  mean_squared_error = find_mean_squared_error(test_dict_list, predicted_ratings_dict, average_rating)
  print("RMSE = " + str(mean_squared_error))
  squared_error_without_nn = find_squared_error_without_nn(test_dict_list,average_rating)
  print("RMSE without using kNN is " + str(squared_error_without_nn))
  percentage_improvement = ((squared_error_without_nn -mean_squared_error)/float(squared_error_without_nn))*100
  print("Percentage improvement: "+str(percentage_improvement))

if __name__ == "__main__":
  main()