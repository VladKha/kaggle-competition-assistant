[](/organizations/arc)Abstraction and Reasoning Corpus  · Featured Code
Competition · a month to go
# ARC Prize 2024
Create an AI capable of solving reasoning tasks it has never seen before


## ARC Prize 2024
how_to_reg
This competition requires identity verification
To submit to this competition, you'll need to verify your identity. [Learn
More](/contact#/account/verify/why)
Verify now


## Overview
In this competition, you’ll develop AI systems to efficiently learn new skills
and solve open-ended problems, rather than depend exclusively on AI systems
trained with extensive datasets. The top submissions will show improvement
toward human reasoning benchmarks.
Start
4 months ago
###### Close
a month to go
Merger & Entry

### Description
Current AI systems can not generalize to new problems outside their training
data, despite extensive training on large datasets. LLMs have brought AI to
the mainstream for a large selection of known tasks. However, progress towards
Artificial General Intelligence (AGI) has stalled. Improvements in AGI could
enable AI systems that think and invent alongside humans.
The Abstraction and Reasoning Corpus for Artificial General Intelligence (ARC-
AGI) benchmark measures an AI system's ability to efficiently learn new
skills. Humans easily score 85% in ARC, whereas the best AI systems only score
34%. The [ARC Prize competition](https://www.arcprize.org) encourages
researchers to explore ideas beyond LLMs, which depend heavily on large
datasets and struggle with novel problems.
This competition includes several components. The competition as described
here carries a prize of $100,000 with an additional $500,000 available if any
team can beat a score of 85% on the leaderboard. Further opportunities outside
of Kaggle are also available with associated prizes- to learn more visit
[ARCprize.org](https://www.arcprize.org/).
Your work could contribute to new AI problem-solving applicable across
industries. Vastly improved AGI will likely reshape human-machine
interactions. Winning solutions will be open-sourced to promote transparency
and collaboration in the field of AGI.

### Evaluation
This competition evaluates submissions on the percentage of correct
predictions. For each task, you should predict exactly 2 outputs for every
test input grid contained in the task. (Tasks can have more than one test
input that needs a predicted output.) Each task test output has one ground
truth. For a given task output, any of the 2 predicted outputs matches the
ground truth exactly, you score `1` for that task test output, otherwise `0`.
The final score is the sum averaged of the highest score per task output
divided by the total number of task test outputs.


## Submission File
The submission file for this competition must be a json named
`submission.json`.
For each task output in the evaluation set, you should make exactly 2
predictions (`attempt_1`, `attempt_2`). The structure of predictions is shown
below. Most tasks only have a single output (a single dictionary enclosed in a
list), although some tasks have multiple outputs that must be predicted. These
should contain two dictionaries of predictions enclosed in a list, as is shown
by the example below. When a task has multiple test outputs that need to be
predicted (e.g., task `12997ef3` below), they must be in the same order as the
corresponding test inputs.
**IMPORTANT:** All the task_ids in the input challenges json file must also be
present in the `submission.json` file. Both "attempt_1" and "attempt_2" must
be present, even if your submission doesn't have 2 predictions.
{"00576224": [{"attempt_1": [[0, 0], [0, 0]], "attempt_2": [[0, 0], [0, 0]]}],
"009d5c81": [{"attempt_1": [[0, 0], [0, 0]], "attempt_2": [[0, 0], [0, 0]]}],
"12997ef3": [{"attempt_1": [[0, 0], [0, 0]], "attempt_2": [[0, 0], [0, 0]]},
{"attempt_1": [[0, 0], [0, 0]], "attempt_2": [[0, 0], [0, 0]]}],
...
}


### Timeline
* **June 11, 2024**  - Start Date
* **November 3, 2024**  - Entry deadline. You must accept the competition rules before this date in order to compete.
* **November 3, 2024**  \- Team Merger deadline. This is the last day participants may join or merge teams.
* **November 10, 2024**  \- Final submission deadline.
* **November 12, 2024**  \- Paper Award submission deadline.
All deadlines are at 11:59 PM UTC on the corresponding day unless otherwise
noted. The competition organizers reserve the right to update the contest
timeline if they deem it necessary.

### Prizes
**TOTAL PRIZES AVAILABLE: $1,100,000**
* 2024 Progress Prizes: $125,000
* Grand Prize: $600,000
* To Be Announced Prizes (on [ARCprize.org](https://arcprize.org)): $375,000
**2024 Progress Prizes**
* **Prizes for Top-Ranking Teams in this Competition** : $50,000
* First Prize: $25,000
* Second Prize: $10,000
* Third Prize: $5,000
* Fourth Prize: $5,000
* Fifth Prize: $5,000
* **Paper Award Prizes** : $75,000
* Winner: $50,000
* First Runner Up: $20,000
* Second Runner Up: $5,000
See the [Paper Award](https://www.kaggle.com/competitions/arc-
prize-2024/overview/prizes) tab for more details on submission and evaluation.
**Grand Prize**
A Grand Prize of an additional $600,000 will be unlocked in the event that a
team achieves a score of at least 85% accuracy on the competition leaderboard.
At the end of the competition, the Grand Prize will be divided among the Top 5
teams that have achieved 85% accuracy as outlined below. In the event that
fewer than 5 teams have achieved 85% accuracy, those prizes will be divided
proportionately among qualifying teams.
* First Prize: $300,000
* Second Prize: $120,000
* Third Prize: $60,000
* Fourth Prize: $60,000
* Fifth Prize: $60,000
**To Be Announced Prizes** (Off Kaggle)
$375,000 in additional prizes will be announced later on
[ARCprize.org](https://arcprize.org)

### Code Requirements
![Kerneler](https://storage.googleapis.com/kaggle-
media/competitions/general/Kerneler-white-desc2_transparent.png)

### This is a Code Competition
Submissions to this competition must be made through Notebooks. In order for
the "Submit to Competition" button to be active after a commit, the following
conditions must be met:
* CPU Notebook <= 12 hours run-time
* GPU Notebook <= 12 hours run-time
* No internet access enabled
* External data, freely & publicly available, is allowed, including pre-trained models
* Submission file must be named `submission.json`
Please see the [Code Competition
FAQ](https://www.kaggle.com/docs/competitions#kernels-only-FAQ) for more
information on how to submit.

### Paper Award
You may choose to submit a paper to be eligible to win a Paper Award Prize.
To be eligible for a Paper Award, you must separately submit a paper (Kaggle
Notebook, PDF, arXiv, txt, etc.) documenting and describing the conceptual
approach of your eligible ARC Prize 2024 Kaggle submission. Paper submissions
must be submitted within 48 hours of the competition ending.
Paper Awards are evaluated equally on the following six components, where a
score of 0 (lowest) and 5 (highest) is given in each category.
Category    | Description |
---|---|---
**Accuracy** | How accurate is the submission based on its performance on the leaderboard? (Note: you will be asked to provide your submission ID to match your notebook to your submission)   |
**Universality**   | How general and universal is the Submission approach beyond the competition? Does your submission translate to other similar problems? How well does your method generalize? |
**Progress** | How much does the paper increase the overall chance of anyone achieving 85% on ARC Prize? |
**Theory** | How well does the paper describe why the Submission works (as opposed to merely describing how it works)? |
**Completeness** | How thoroughly and completely does the paper cover your submission to the leaderboard? |
**Novelty** | How novel is the Submission relative to existing public research? |
The Paper Award will be awarded to the Submission with the most points and the
Paper Award Runner Up will the second most points. Your Paper rubric
evaluation will not be shared with you. In the event of a tie, the Paper that
was entered first to the Competition will be the winner. In the event a
potential winner is disqualified for any reason, the Paper that received the
next highest score rank will be chosen as the potential winner.

### Click here to go to the [Submission
form](https://docs.google.com/forms/d/e/1FAIpQLSfhmYE6AMYfMBkxj5_G8QHyWTWWEe1wUg98LM1UQsUR8ci-1w/viewform)

### Citation
Francois Chollet, Mike Knoop, Bryan Landers, Greg Kamradt, Hansueli Jud,
Walter Reade, Addison Howard. (2024). ARC Prize 2024. Kaggle.
https://kaggle.com/competitions/arc-prize-2024


## Competition Host
Abstraction and Reasoning Corpus
[](/organizations/arc)


## Prizes & Awards
$1,100,000
Awards Points & Medals


## Participation
14,272 Entrants
1,165 Participants
1,070 Teams
10,228 Submissions
