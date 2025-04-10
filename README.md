# Rivals-Data-Analysis
Course work for Masters of Data Science

## What are we investigating? 

This is the real question. Long since the original hero-shooter (Overwatch) there's been a general consensus of the community at high ranks that "**stats don't matter**". Since Overwatch doesn't have a public API where you amass any of this data, people have just accepted this as *fact*. The idea of this investigation is prove and/or challenge it through a series of questions. Some of the proposed questions are:

- Kills/Deaths/Assists 
    - do these values impact win likelihood?
    - which one has the strongest correlation with win % ?
    - does last_hit spread win games or solo carry more impactful? 
- Dmg/Mit/Heal
    - does healing win games or is it damage?
    - how much does blocking damage impact the outcome of a game? 
- META
    - do meta characters have high winrates in general or is it comp dependent?
    - is tripple support really that strong?
***
# How much data do we need?

### Estimating the Required Data Size
A common rule of thumb for machine learning is to have at least 10 times as many samples as features for simple models like logistic regression. For more complex models (e.g., random forests, neural networks), this can be 50–100x or more.

#### **Step 1: Estimate Data Points per Match**
Since each match involves 12 players, you need to decide if you:

- Treat each player individually → 12 data points per match
- Aggregate team stats → 2 data points per match
- Keep match-level stats → 1 data point per match

#### **Step 2: Estimate Required Matches**
For a simple logistic regression, let’s assume you have 20 features (e.g., damage, KDA, hero, healing, etc.):

- **Logistic Regression** → Needs 200–500 matches (4,000–12,000 player data points)
- **Random Forest/XGBoost** → Needs 1,000–5,000 matches (20,000–60,000 player data points)
- **Neural Network** → Needs 5,000+ matches (100,000+ player data points)

Ideally, I want ~5000+ matches as a neural network is most likely to give the best answer to this multifacted problem, however for the nature of this project and time commitment, we'll settle for 1000 matches for the time being. 

***
## Assumptions

It is impossible to account for general player variance (e.g. poor performance due to life events) so we have to consider some factors outside of our control. Here are some reasonable assumptions to be made regarding the game. 

### **1. Players in the top 5%-10% understand the game (*but can't always impact it*)**

The idea here is that you're good enough to be in the top of the upper quartile of the entire playerbase, but you aren't the top 1% who can solo-carry or meaningfully change the game with your presence alone. At this range it's expected:
- All players generally know what all characters do (abilities/cooldowns/comp-types/etc.)
- All players are able to somewhat effectively coordinate with a team (regardless of verbal communication)
- Most players can land skill-shots (i.e. non-targeted abilities) and have a semi-consistent accuracy (for non-melee characters)
- All players know what the job of their role is, as well as what K/D/A & Dmg/Mit/Heal are

This range mostly consists of Diamond → Grand Master players, but excludes the Celestial rank which is made up of the top 'Carry' players whose presence drastically changes the outcome of the match. 

So for this exercise, most match samples will be take from **Diamond** to **Grand Master**, with the exception of a smaller sample pool of lower ranked and/or quickplay games to test against a null group. 

**Benefits of Filtering to Upper Ranks**
- ✅ More Consistent Gameplay → Reduces randomness from players who don’t fully grasp the game.
- ✅ Better Hero Understanding → Ensures win rates reflect actual hero strengths rather than misplays.
- ✅ More Useful Insights → The model will be more applicable to serious players looking to improve.

**Potential Downsides**
- ❌ Less Data Overall → You may need more matches to reach the same level of statistical confidence.
- ❌ Not Representative of All Players → If you ever want to predict win likelihood for lower-ranked players, the model might not generalize well.

### **2. Team Coordination vs. Solo-play**

There isn't a great way to check for this other than individually tagging each player in a match and counting how often they appear relative to other players. While possible, it can severly limit the amount of data I can collect since the likelyhood of *N-stack vs N-stack* is high. 

**I'll be assuming that if there is a team with N-stack, the enemy team also has a N-stack of equal players.**

### **3. Match Duration & Early FFs**

Any matches that resulted in a surrender will be removed from the sampling pool. There are unlikely to give data either way that is important. This also includes matches that had leavers. 

## Methods

This analysis investigates the relationship between individual and team **performance metrics** and their impact on match outcomes. The dataset is preprocessed to calculate performance scores for players and teams using z-scores, which measure deviations from role or team averages. 

#### Steps:
1. **Data Preprocessing**:
    - Load and clean the dataset to ensure all required columns are present and numeric values are properly formatted.
    - Group data by roles and teams to calculate average performance metrics (e.g., kills, assists, damage) and their standard deviations.

2. **Performance Score Calculation**:
    - For individual players:
      - Compute z-scores for each player by comparing their metrics (e.g., kills, deaths, assists, damage dealt, healing, damage taken) to the average metrics of their respective roles.
      - The formula for the z-score is:

```math
z = \frac{x - \text{mean}}{\text{std\_dev}}
```
here $`x`$ is the player's metric, $`\text{mean}`$ is the role average, and $`\text{std\_dev}`$ is the standard deviation for that metric.

- Combine z-scores across all metrics to calculate an overall performance score for each player.
    - For teams:
      - Compute z-scores for team-level metrics (e.g., total kills, assists, damage, healing) by comparing them to the overall team averages.
      - Aggregate these z-scores to derive a team performance score.

3. **Statistical Analysis**:
    - Conduct t-tests to evaluate the significance of individual and team metrics (e.g., `hero_damage`, `total_damage`) in determining match outcomes.
    - Train Random Forest classifiers to predict match outcomes based on individual and team-based features.
    - Extract feature importance rankings to identify key predictors of success.

4. **Visualization**:
    - Use scatter plots to explore the relationship between individual and team performance scores and match outcomes.
    - Generate histograms to analyze the distribution of performance scores for winning and losing players/teams.
    - Create heatmaps to examine correlations between features.

The analysis also examines the influence of team compositions and roles on match success, highlighting the contributions of specific roles like `STRATEGIST` to overall team performance.

***
## Results

![image](https://github.com/user-attachments/assets/0c635293-d87f-4c56-ad44-667d43dbb0ad)
![image](https://github.com/user-attachments/assets/4cad689e-8698-402f-b1cf-3d3b94e4667a)
![image](https://github.com/user-attachments/assets/a5ad4b67-63cd-4132-9ac1-f3ebe3ec0d0d)
![image](https://github.com/user-attachments/assets/22f1bb22-5e34-4bd3-bdc3-eda205297497)
![image](https://github.com/user-attachments/assets/15f6b310-aa96-4768-8f94-d83c7d935674)
![image](https://github.com/user-attachments/assets/ab43255d-a78e-470e-89b6-c56a5d231e04)
![image](https://github.com/user-attachments/assets/d38ec75b-2f6f-4771-8201-24bdfc782d15)
![image](https://github.com/user-attachments/assets/e9de683d-db10-41d8-b351-0d09c8a9f5b2)
![image](https://github.com/user-attachments/assets/a5aa5f76-1394-43c7-9730-db9a13a49312)
![image](https://github.com/user-attachments/assets/2eb87f33-1072-4eab-9c27-db12c07abc79)
![image](https://github.com/user-attachments/assets/31467c3b-b696-4d56-a435-6ad4399f8fcb)
![image](https://github.com/user-attachments/assets/02502e3e-0df2-4f8f-8af0-512acfd4e34d)
![image](https://github.com/user-attachments/assets/a489315a-ad2a-40a6-99a9-51a88d3c27d8)
![image](https://github.com/user-attachments/assets/5e9cfa96-9708-4d73-9196-2397f076e808)
![image](https://github.com/user-attachments/assets/ffb9c1c8-ee73-4ba9-b46c-731c75394c56)

***
## Team Performance
Accuracy: **0.81**

Classification Report:

                 precision   recall    f1-score    support
           0       0.87      0.72      0.79        18
           1       0.76      0.89      0.82        18
    accuracy                           0.81        36
    macro avg      0.81      0.81      0.80        36
    weighted avg   0.81      0.81      0.80        36


Feature Importance:

              Feature        Importance
    0         total_kills    0.353035
    1       total_assists    0.204208
    2        total_deaths    0.130392
    5  total_damage_taken    0.122390
    4       total_healing    0.096894
    3        total_damage    0.093081


## Individual Performance
Accuracy: **0.88**

Classification Report:

                precision    recall    f1-score   support
           0       0.88      0.88      0.88       226
           1       0.88      0.88      0.88       231
    accuracy                           0.88       457
    macro avg      0.88      0.88      0.88       457
    weighted avg   0.88      0.88      0.88       457


Feature Importance:

            Feature    Importance
    0       kills_x    0.321518
    1      deaths_x    0.160811
    3   hero_damage    0.158794
    5  damage_taken    0.155595
    2     assists_x    0.113196
    4   hero_healed    0.090086

## By Role

Correlation between performance score and win by role:

         role           correlation      abs_correlation
    0    STRATEGIST     0.382134         0.382134
    1    DUELIST        0.346564         0.346564
    2    VANGUARD       0.309352         0.309352


*** 
# Conclusion


More data is needed to build better insights. Current sample size is ~400-500 matches with around 3000 individual players. To better sample data, start at a single match, request and pick a random player_uid aside from your starting point, go grab a random match from their history, continue this process for ~5000 matches. 

## Classification Reports

Based on the classification reports and feature importance, **individual performance matters most in securing a win**. Here's the supporting evidence:

1. **Feature Importance (Individual Stats)**:
    - The most important features for predicting individual performance (`is_win`) are `kills_x`, `assists_x`, and `hero_damage`. These metrics directly reflect a player's contribution to the match outcome.
    - For example, `kills_x` has a significant impact, as players who secure more kills are likely to influence the match positively.

2. **Classification Accuracy**:
    - The Random Forest model trained on individual stats achieved a higher accuracy compared to the team-based model. This indicates that individual performance metrics are more predictive of match outcomes.

3. **Statistical Significance**:
    - The t-test for `hero_damage` (individual stats) shows a statistically significant difference between winning and losing players (p-value = 0.002). This highlights the importance of individual contributions like damage output in determining match outcomes.

4. **Team-Based Metrics Are Less Predictive**:
    - The feature importance for team-based stats shows that metrics like `total_damage` and `total_healing` have lower importance compared to individual stats. Additionally, the t-test for `total_damage` (team-based stats) shows no statistically significant difference (p-value = 0.53), suggesting that team-level metrics are less decisive.

**Individual performance**, as measured by metrics like `kills_x`, `assists_x`, and `hero_damage`, is the most **critical factor** in securing a win. The statistical significance, higher feature importance, and better model accuracy for individual stats strongly support this conclusion.

## Role Dominance 

**STRATEGIST** role contributes the most to team success. According to the `role_stats` dataframe, **STRATEGISTs** exhibit the highest average assists (14.68) and healing (16,497.25), which are critical for enabling other roles to perform effectively. These metrics highlight the **STRATEGIST's** role in sustaining team momentum and facilitating coordination during matches.

Furthermore, the correlation analysis, as presented in the `role_correlation` dataframe, reveals that the **STRATEGIST** role demonstrates the strongest correlation with match victories (0.382134), surpassing other roles. This finding underscores the significant relationship between the performance of **STRATEGISTs** and the likelihood of winning matches. Additionally, the `role_win_stats` dataframe indicates that **STRATEGISTs** achieve the highest average win rate (0.433628), further emphasizing their impact on team success.

## Role-Swapping (Counter-Swap etc.)

![image](https://github.com/user-attachments/assets/899f076d-6ae5-47e1-86e3-6689eb2753ec)
![image](https://github.com/user-attachments/assets/fe0dc526-376b-4895-a6ea-888391679c39)

Overall, the larger number of swaps a player/team makes is associated with a negative winrate. Role swapping has a negative associated winrate fairly even accross the board, however, the lower winrate for **STRATEGIST** does suggest a large impact on game outcome. This concept should not be conflated with the idea that players are swapping are already losing, so they'll continue to lose. The reasoning is highlighted in the charts above as we can see that **average player's winrate increases** as time is spent on a single hero per match. 

![image](https://github.com/user-attachments/assets/9235ddce-3c13-49c3-a801-205d88c09774)
![image](https://github.com/user-attachments/assets/9a070ddb-e5e6-4632-88bc-ab2e6e25820f)
![image](https://github.com/user-attachments/assets/f1a18946-9503-4dab-97bb-00f155bbf13d)

Late swaps actually correlate to a better overall performance for the player, however, this does not change the outcome of the match. This could indicate that the team was just 'better' and no amount of individual change would have impact. 

![image](https://github.com/user-attachments/assets/e3d86aae-875f-41e6-968c-3ba99a60e75e)

Instead, swaps normally have an effect of slightly decreasing the average performance of your team rather than improving it.

The box plot illustrates how players who do swap and in are on average out performing the enemy team by 1.96x the Performance score which is a significant value given the context of how it is calculated (see DATA ANALYSIS 3).

![image](https://github.com/user-attachments/assets/3541821a-80cc-413c-988c-d0478ca87be5)
![image](https://github.com/user-attachments/assets/ba393594-5f15-44b2-ab50-43d864e88720)

The above histograms further illustrate that while player performance increases and reduces the likelihood of loss, the team's overall performance decreases and likelihood of loss increeases. This suggests along with the above charts showing number of swaps vs. winrate that if a swap is to occur, the rest of the teams should swap and adjust as well. From a contextual standpoint of the game, this indicates a need for team cohesion and composition. A swap make improve your average performance, but if the hero swapped to doesn't play well with your teammates, you decrease the likelihood of winning. 

When normalizing the winrate on role swapping, the character swap (*e.g. **DUELIST -> DUELIST***) categories across all roles are significantly the lowest. This is likely due to team composition issues, *'one-trick'* players, lower profeciency at the hero at the same skill level, and or lack of hero kits in that role to deal with the enemy.

### Lowest Win-rate Swap (Adjusted)

The lowest winrate swap after adjusting is **DUELIST -> STRATEGIST**. There are many implications can be drawn about this such as:
- **DUELISTs** on average understand less about supporting priority / ultimate economy
- **STRATEGISTs** were under-performing significantly, and the match was going to be lost regardless

As **STRATEGIST -> DUELIST** win rate remains larger, it suggests that **STRATEGISTs** aren't swapping to fill the role of DUELIST at the same rate, meaning it's likely a 2-1-3 or 1-2-3 comp being formed. We can see from the [chart](https://private-user-images.githubusercontent.com/35696198/432047189-d38ec75b-2f6f-4771-8201-24bdfc782d15.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDQyMzc2MzcsIm5iZiI6MTc0NDIzNzMzNywicGF0aCI6Ii8zNTY5NjE5OC80MzIwNDcxODktZDM4ZWM3NWItMmY2Zi00NzcxLTgyMDEtMjRiZGZjNzgyZDE1LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA0MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNDA5VDIyMjIxN1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWY5M2I3M2ZjNDY1YThjNTUzOTdiNDZlYzY1N2RhMTUxMDllYTNhOWM0M2M3NWQ3Njk5NWQyYTc5OWNmZWEwYTkmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.--PPSiJ37sovFwGu7GVsbD5F5vF6ploMjsbBntwcCFQ) in **DATA ANALYSIS (3)** that these comps heavily underperform compared to the classic 2-2-2 that has been ideal since the start of Hero Shooters.

## **On Win-rate per Number of Swaps**

There is a noticable downwards trend in the number of swaps lowering the overall likelihood to win. However, we can see around 5 swaps in a match can actually improve your ability to win. Considering these are grouped by `match_uid`  and by teams that won, it can imply that team composition matters more than swapping itself. 

For example, 1-VANGUARD (Melee/Dive), 3-DUELISTs (1 Melee / 2 Projectile), 2-STRATEGISTS (1 Projectile / 1 Hitscan) has no necessary cohesion. If 5 members were to swap and fulfill a team identity (Brawl/Dive/Poke, etc.) around the member carrying on the team, or into a composition that counter's the enemy (Dive -> Poke), you would see a drastic increase in likelihood to win regardless of current performance score.

