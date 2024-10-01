## Dataset Description


## Dataset Description
The dataset includes several CSV files that provide training, testing, and
auxiliary data. Below is a detailed description of each file and its columns:

### train.csv
Contains the training data with problem statements in English, along with
their respective answers.
* `problem_id`: Unique identifier for each problem.
* `problem_text`: The mathematical problem statement in English.
* `answer`: The correct answer to the problem.

### rus_train.csv
Contains the training data with problem statements in Russian, along with
their respective answers and hints.
* `problem_id`: Unique identifier for each problem.
* `problem_text`: The mathematical problem statement in Russian.
* `answer`: The correct answer to the problem.
* `hint`: A hint or additional information to help solve the problem (not available for test!).

### train_unchecked.csv
Contains additional training data in English, with problem statements and
their respective answers. These problems are unchecked and may contain errors.
* `problem_id`: Unique identifier for each problem.
* `problem_text`: The mathematical problem statement in English.
* `answer`: The correct answer to the problem.

### rus_train_unchecked.csv
Contains additional training data in Russian, with problem statements and
their respective answers. These problems are unchecked and may contain errors.
* `problem_id`: Unique identifier for each problem.
* `problem_text`: The mathematical problem statement in Russian.
* `answer`: The correct answer to the problem.

### test.csv
Contains the test data with problem statements in English. Participants are
required to predict the answers for these problems.
* `problem_id`: Unique identifier for each problem.
* `problem_text`: The mathematical problem statement in English.

### rus_test.csv
Contains the test data with problem statements in Russian. This is provided
for reference.
* `problem_id`: Unique identifier for each problem.
* `problem_text`: The mathematical problem statement in Russian.

### sample_submission.csv
A sample submission file to demonstrate the expected format for the final
submission.
* `problem_id`: Unique identifier for each problem.
* `answer`: The predicted answer to the problem. Initially set to 'No answer'.
Ensure to use these datasets appropriately for training, testing, and
submission purposes.


## Files
7 files


## Size
361.64 kB


## Type
csv


## License
Subject to Competition Rules


## Data Explorer
361.64 kB
rus_test.csv
rus_train.csv
rus_train_unchecked.csv
sample_submission.csv
test.csv
train.csv
train_unchecked.csv


## Summary
7 files
19 columns
