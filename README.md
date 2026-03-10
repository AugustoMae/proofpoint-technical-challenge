# Proofpoint Intern Program 2026 – Technical Challenge

---

## Part A – Questions

### 1. Describe the most relevant learnings from programming-related subjects during your career.

During the programming courses in my career, I developed skills to analyze problems and solve them by designing algorithms and logical structures. These subjects helped me learn how to approach different computing problems in a structured way and how software solutions are built.

I also learned concepts related to system design, including how to choose the correct language or technology depending on the type of application that needs to be developed. In this context, I worked with different programming paradigms, including object-oriented programming using Java.

In addition, I gained experience in web development using technologies such as JavaScript and React. I also learned basic concepts about servers, networks, and how applications work in connected environments.

During my studies, I had my first contact with cybersecurity. I used tools like Wireshark to analyze network traffic and Burp Suite to study the behavior of web applications and identify possible vulnerabilities. This helped me understand some practical challenges related to the security of systems and applications.

Finally, I also worked with data science tools using Python and learned the basic ideas behind some artificial intelligence and machine learning algorithms. This helped me understand how data can be analyzed and how models can be built to solve different problems.

---

### 2. Describe a situation you had to resolve with a teammate from a study or work group.

In an Artificial Intelligence course at university, I worked on a group project where we built an image search system similar to Google Photos. The idea was that a user could write a text query and the system would return relevant images using AI models.

The system was based on embeddings and vector representations of both images and text. This allowed us to compare queries and images in a semantic way instead of using simple keyword matching. We also experimented with different techniques such as reranking to improve the final results.

One of the main challenges was that the model we used to connect text and images was trained mainly in English. Because of this, when the queries were written in Spanish, the results were not always very good.

At the beginning of the project, each team member was trying different solutions separately. This made our progress slower and the communication in the team was not very clear. I suggested that we meet and analyze the problem together to decide on a common approach.

During that meeting, I proposed dividing the queries into positive and negative terms and translating them into English before running the search. We implemented this idea using a small language model to reformulate the queries and then compared the results with the base system.

After applying this change, we started to get more relevant results and we were able to improve our position in the course ranking. This experience helped me better understand how modern AI systems work, especially how embeddings, vector search, and reranking techniques can be combined to improve the performance of an AI application.

It also showed me that sometimes simple changes, like reorganizing or reformulating a query, can significantly improve the results of an AI system.

---

### 3. Describe your personal learning plans or development expectations in technical areas in the short and long term.

In the short term, my main goal is to make the transition from academic projects to real production environments. At university I have learned many concepts and built projects that helped me develop technical skills, but I know that working on real systems brings a completely different level of challenges and learning.

During this internship I would like to understand how professional software development works in practice: how teams collaborate, how code is reviewed and tested, how systems are deployed and monitored, and how technical decisions are made in a real company. I am also interested in discovering which technical areas motivate me the most when working on real problems, since I am still exploring whether I enjoy more the backend engineering side, the data and AI side, or the security and infrastructure side.

In the long term, I would like to grow into a software engineer who can work on complex systems that have a real impact on people and organizations. Proofpoint's work on cybersecurity and threat detection is particularly interesting to me because it combines large-scale software engineering with a clear and meaningful purpose: protecting users and companies from real threats.

I also hope to keep learning continuously, both from the people I work with and from the technical challenges I face, since I believe that the ability to adapt and learn quickly is one of the most important skills in this field.

---

## Part B – The Streaming Service's Lost Episodes

### Problem

A streaming platform's episode catalog was ingested without any validation or uniqueness checks, resulting in a corrupted dataset with missing fields, invalid formats, and duplicate entries.

### Solution

**File:** `streaming-episodes/process_episodes.py`

A Python pipeline that reads a CSV file and produces a clean, deduplicated episode catalog along with a data quality report.

#### What the program does

**1. Parsing and correction**

Each row is parsed and the following rules are applied:

| Field | Rule |
|-------|------|
| Series Name | If missing → discard the record |
| Season Number | If missing, invalid, or negative → set to `0` |
| Episode Number | If missing, invalid, or negative → set to `0` |
| Episode Title | If missing → replace with `"Untitled Episode"` |
| Air Date | If missing or invalid → replace with `"Unknown"` |

Records where Episode Number, Episode Title **and** Air Date are all missing are also discarded.

**2. Date validation**

Dates are validated strictly in `YYYY-MM-DD` format. Values like `"0000-00-00"` or `"2022-40-99"` that some parsers accept are explicitly rejected through additional range checks.

**3. Deduplication**

Two records from the same normalized series are considered duplicates when any of the following criteria is met:

- Same `SeasonNumber` and same non-zero `EpisodeNumber`
- Both `SeasonNumber` values are `0`, same `EpisodeNumber`, and same normalized `EpisodeTitle`
- Same `SeasonNumber`, both `EpisodeNumber` values are `0`, and same normalized `EpisodeTitle`

Normalization means: trim whitespace, collapse multiple spaces, convert to lowercase.

After the initial grouping, a **transitive merge pass** is applied to correctly collapse groups that are only connected indirectly (if A matches B and B matches C, all three end up in the same group).

**4. Best record selection**

Within each duplicate group, the best record is kept using this priority:

1. Valid `AirDate` over `"Unknown"`
2. Known `EpisodeTitle` over `"Untitled Episode"`
3. Non-zero `SeasonNumber` and `EpisodeNumber`
4. First record encountered in the file

#### Output files

- `episodes_clean.csv` — cleaned and deduplicated episode catalog
- `report.md` — data quality report including total records, discarded, corrected, duplicates, correction breakdown by field, and explanation of the deduplication strategy

#### How to run

```bash
python process_episodes.py <input_csv>
```

Example:
```bash
python process_episodes.py sample_input.csv
```

**Requirements:** Python 3.7+, no external dependencies.

---

## Part C – Word Frequency Analyzer *(optional)*

### Problem

Write a program that reads a text file and performs a word frequency analysis, showing the top 10 most frequent words.

### Solution

**File:** `word-frequency/word_frequency.py`

A Python script that reads any text file and counts how many times each word appears.

#### What the program does

- Reads the input file encoded in UTF-8
- Removes punctuation and special characters using regex, keeping only letters and spaces
- Supports both **English and Spanish** text (accents, ñ, ü, etc.) using Unicode-aware regex
- Converts all text to lowercase for case-insensitive comparison
- Counts word frequencies using Python's `collections.Counter`
- Displays the top 10 most frequent words with their counts
- Shows additional statistics: total words, unique words, and average frequency

#### How to run

```bash
python word_frequency.py <text_file>
```

Example:
```bash
python word_frequency.py sample.txt
```

**Requirements:** Python 3.7+, no external dependencies.
