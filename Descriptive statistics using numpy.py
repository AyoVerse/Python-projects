import numpy as np
num_students =10
num_subjects = 5

scores = np.random.randint(40, 101, size=(num_students, num_subjects))
print("Student Scores(Rows = Students, Columns = Subjects):\n")
print(scores)

averagescores= np.mean(scores, axis= 1)
averagesubject= np.mean(scores, axis =0)
highest_score= np.max(scores)
lowest_score = np.min(scores)
standard_dev = np.std(scores)

print("\nANALYSIS:")
print("Average Score Per Student: ", averagescores)
print("Average Score Per Subject: ", averagesubject)
print("Highest score from data: ", highest_score)
print("Lowest score from data: ", lowest_score)
print("Standard Deviation: ", round(standard_dev,2))









