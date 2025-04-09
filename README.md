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
