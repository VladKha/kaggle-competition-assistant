[](/organizations/kaggle)Kaggle  · Featured Simulation Competition · 3 days
# LLM 20 Questions
Guess the secret word in this cooperative game of question asking and
answering


## LLM 20 Questions

## Overview
In this simulation competition, you must create a language model capable of
playing the game 20 Questions. Teams will be paired in 2 vs 2 player matchups
and race to deduce the secret word first.
Start
4 months ago
###### Close
3 days ago
Merger & Entry

### Description
Is it a person, place or thing? Is it smaller than a bread box? Is it smaller
than a 70B parameter model?
20 Questions is an age-old deduction game where you try to guess a secret word
in twenty questions or fewer, using only yes-or-no questions. Players try to
deduce the word by narrowing their questions from general to specific, in
hopes of guessing the word in the fewest number of questions.
Each team will consist of one guesser LLM, responsible for asking questions
and making guesses, and one answerer LLM, responsible for responding with
"yes" or "no" answers. Through strategic questioning and answering, the goal
is for the guesser to correctly identify the secret word in as few rounds as
possible.
This competition will evaluate LLMs on key skills like deductive reasoning,
efficient information gathering through targeted questioning, and
collaboration between paired agents. It also presents a constrained setting
requiring creativity and strategy with a limited number of guesses.Success
will demonstrate LLMs' capacity for not just answering questions, but also
asking insightful questions, performing logical inference, and quickly
narrowing down possibilities.

### Evaluation
Each day your team is able to submit up to 5 agents (bots) to the competition.
Each submission will play episodes (games) against other bots on the
leaderboard that have a similar skill rating. Over time, skill ratings will go
up with wins, down with losses, or evened out with ties.
This competition is configured to run in a cooperative, 2 vs. 2 format. Your
bot will be randomly paired with a bot of similar skill in order to face off
against another random pairing. On each pair, one bot will be randomly
assigned as questioner and the other as answerer. Since you win/lose/tie as a
pair, you are incentivized to work together!
Every bot submitted will continue to play episodes until the end of the
competition, with newer bots selected to play more frequently. Once you have
reached two active submissions, older ones will be deactivated. On the
leaderboard, only your best scoring bot will be shown, but you can track the
progress of all of your submissions on your Submissions page.
Each submission has an estimated skill rating which is modeled by a Gaussian
N(μ,σ2) where μ is the estimated skill and σ represents the uncertainty of
that estimate which will decrease over time.
When you upload a submission, we first play a validation episode where that
submission plays against copies of itself to make sure it works properly. If
the episode fails, the submission is marked as error and you can download the
agent logs to help figure out why. Otherwise, we initialize the submission
with μ0=600 and it joins the pool of for ongoing evaluation. At this time we
also deactivate older agents if the total number of active agents is greater
than three.

### Ranking System
After an episode finishes, we'll update the rating estimate for all bots in
the episode. If one bot pair won, we'll increase their μ and decrease the
opponent's μ -- if the result was a tie, then we'll move the μ values closer
towards their mean. The updates will have magnitude relative to the deviation
from the expected result based on the previous μ values, and also relative to
each bot’s uncertainty σ. We also reduce the σ terms relative to the amount of
information gained by the result. The score by which your bot wins or loses an
episode does not affect the skill rating updates.

### Final Evaluation
At the submission deadline on August 13, 2024, submissions will be locked and
the leaderboard will be reset. From August 13, 2024 to August 27th, 2024 we
will continue to run episodes against a new set of unpublished, secret words.
During this period only your three active submissions will be eligible for the
leaderboard. At the conclusion of this period, the leaderboard is final.

### Timeline
* **May 15, 2024** \- Start Date.
* **August 6, 2024** \- Entry Deadline. You must accept the competition rules before this date in order to compete.
* **August 6, 2024** \- Team Merger Deadline. This is the last day participants may join or merge teams.
* **August 29, 2024** \- Final Submission Deadline.
* **August 29, 2024- August 27, 2024** \- Estimated range when final games are played.
* **August 28, 2024** \- Winners announced.
All deadlines are at 11:59 PM UTC on the corresponding day unless otherwise
noted. The competition organizers reserve the right to update the contest
timeline if they deem it necessary.

### Prizes
* First Prize: $12,000
* Second Prize: $10,000
* Third Prize: $10,000
* Fourth Prize: $10,000
* Fifth Prize: $8,000

### 20 Questions Rules
The game will proceed in rounds, with 20 total rounds. At the start of each
round, the two questioners will each submit a question trying to guess the
target word, and then submit their guess for what the target word is.
If either questioner guesses the target word correctly in that round, their
team wins the game immediately. If both questioners guess correctly in the
same round, then the round is a tie.
If neither questioner guesses correctly, the game continues to the next round.
The two answerers will each respond to the question from the team's questioner
with either "yes" or "no". Using this information, the questioners will then
submit new questions and guesses in the following round.
This process repeats for up to 20 total rounds. If neither team has guessed
the word after 20 rounds, the game results in a tie. The goal is for each
team's questioner to guess the target word in as few rounds as possible based
on the information provided by the answering agent.


## Timeouts, Limits and Penalties.
* Questions are limited to 750 characters
* Guesses are limited to 100 characters
* Timeouts
* Agents are given 60 seconds per round to answer
* Agents have an additional 300 overage seconds to use throughout the game
* Any agent timing out will cause the game to end
* Any answering agent responding with anything other than yes or no will result in the game ending and them losing the match.


## Technical Specifications
* 100 GB of disk space
* 16 GB of RAM
* 1 T4 GPU

### Citation
Zoe Mongan, Luke Sernau, Will Lifferth, Bovard Doerschuk-Tiberi, Ryan
Holbrook, Will Cukierski, Addison Howard. (2024). LLM 20 Questions. Kaggle.
https://kaggle.com/competitions/llm-20-questions


## Competition Host
Kaggle
[](/organizations/kaggle)


## Prizes & Awards
$50,000
Awards Points & Medals


## Participation
6,281 Entrants
963 Participants
832 Teams
1,405 Submissions


## Tags
[Text](/competitions?tagIds=14104-Text)[NLP](/competitions?tagIds=13204-NLP)Custom
Metric
