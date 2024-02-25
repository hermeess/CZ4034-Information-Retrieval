# CZ4034-Information-Retrieval

### Project Overview.

This project aims to create a information retrieval system that can explore topics regarding Mental Health.

## Crawling

The crawling folder contains four `.csv` files which can be used for indexing purposes.
The crawling was done on various subreddits regarding mental helath:
Subreddits crawled:

1. r/mentalhealth
1. r/socialanxiety
1. r/mentalhealthsupport
1. r/depression
1. r/mentalillness
1. r/anxiety
1. r/bipolar
1. r/ptsd
1. r/eatingdisorders
1. r/schizophrenia
1. r/MMFB
1. r/offmychest
1. r/anxietyhelp
1. r/truoffmychest
1. r/traumatoolbox
1. r/CPTSD

The various files that were produced are as follows

1.  `reddit_post_title_only.csv` contains reddit posts from subreddits <b>1-16</b> and their title and sentiments based on the title.
    The breakdown of the sentiments in this file is as follow:

    ```py
     neutral     5747
     negative    2390
     positive    1970
    ```

1.  `reddit_post_with_compiled_comments.csv` contains reddit posts from subreddits <b>1-16</b>, alongside the post's title, body and compiled comments.
    The sentiments in this section is obtained by combining the post's title, body and all comments from the post.
    The breakdown of the sentiments in this file is as follows:

    ```py
     positive    6763
     negative    3180
     neutral      164
    ```

1.  `reddit_post_with_separated_comments.csv` contains reddit posts from subreddits <b>1-10</b> alongside the post's title, body and individual comments.
    The sentiments in this section is obtained from combining the post's title, body and individual comments from the post.
    The breakdown of the sentiments in this file is as follows:

    ```py
     positive    10472
     negative     6416
     neutral       267
    ```

1.  `reddit_post_with_comments_only.csv.csv` contains reddits posts from subreddits <b>1-10</b> alongside the indivdual comments. The sentiments in this section is obtain from the individual comments itself.
    The breakdown of the sentiments in this file is as follows:
        ```py
        positive    9679
        negative    4462
        neutral     3014
        ```
