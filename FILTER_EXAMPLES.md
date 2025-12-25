# 🎯 Filter Examples - Quick Reference

## Filter Scenarios with Expected Results

### Scenario 1: Current Season Only
**Goal**: Analyze 2025 season performance

**Filters**:
```
Season: [2025]
Ground: All
Team: All
Venue Type: All
Innings: All
```

**What You Get**:
- Only 2025 season data
- All grounds included
- All teams included
- Best for current form analysis

**Use When**:
- Planning for upcoming matches
- Checking recent form
- Comparing with live season stats

---

### Scenario 2: Home Ground Mastery
**Goal**: How does a player perform at their home ground?

**Filters**:
```
Season: All
Ground: [Wankhede Stadium, Mumbai]
Team: All
Venue Type: Home
Innings: All
```

**What You Get**:
- Historical data at Wankhede
- Only when playing at home
- Full picture of home advantage

**Use When**:
- Mumbai Indians home match preparation
- Analyzing home ground advantage
- Understanding venue-specific tactics

---

### Scenario 3: Rivalry Analysis
**Goal**: Performance against a specific rival

**Filters**:
```
Season: [2024, 2025]
Ground: All
Team: [Chennai Super Kings]
Venue Type: All
Innings: All
```

**What You Get**:
- Recent 2 seasons only
- Only matches vs CSK
- All venues included

**Use When**:
- Preparing for rivalry matches
- Understanding head-to-head patterns
- Strategic planning against specific opponents

---

### Scenario 4: Chasing Specialist
**Goal**: Identify 2nd innings performers

**Filters**:
```
Season: [2025]
Ground: All
Team: All
Venue Type: All
Innings: 2
```

**What You Get**:
- Only 2nd innings data
- Current season only
- Perfect for chasing analysis

**Use When**:
- Selecting batsmen for run chases
- Analyzing pressure performance
- Understanding chasing strategies

---

### Scenario 5: Away Challenge
**Goal**: Performance at away venues

**Filters**:
```
Season: [2025]
Ground: All
Team: All
Venue Type: Away
Innings: All
```

**What You Get**:
- Only away matches
- Current season
- Shows adaptability

**Use When**:
- Planning for away tours
- Understanding travel impact
- Selecting touring squad

---

### Scenario 6: Death Overs Specialist (Combined with UI)
**Goal**: Find best death overs batsmen in current season chasing

**Filters**:
```
Season: [2025]
Ground: All
Team: All
Venue Type: All
Innings: 2
```

**Then in UI**:
- Use "Batsman vs Bowling Type"
- Look for high strike rates
- Low dot ball percentages

**What You Get**:
- Finishers for chasing
- Pressure performers
- Current form indicators

---

### Scenario 7: Specific Venue Weakness
**Goal**: Find opponent weaknesses at a specific ground

**Filters**:
```
Season: All
Ground: [Eden Gardens, Kolkata]
Team: [Royal Chal Bengaluru]
Venue Type: All
Innings: All
```

**What You Get**:
- Historical Eden Gardens data
- Only vs RCB
- Venue-specific patterns

**Use When**:
- KKR preparing home match vs RCB
- Exploiting known weaknesses
- Strategic bowling/field placements

---

### Scenario 8: Powerplay Defending
**Goal**: Best bowlers for powerplay when defending

**Filters**:
```
Season: [2025]
Ground: All
Team: All
Venue Type: All
Innings: 1
```

**Then in UI**:
- Use "Bowler Economy by Phase"
- Focus on Powerplay stats
- Look for low economy + wickets

**What You Get**:
- 1st innings powerplay specialists
- Economy rates while defending
- Wicket-taking bowlers

---

### Scenario 9: Multi-Season Comparison
**Goal**: Compare performance across seasons

**Run 1**:
```
Season: [2024]
[Other filters as needed]
→ Take screenshot/notes
```

**Run 2**:
```
Season: [2025]
[Same other filters]
→ Compare with Run 1
```

**What You Get**:
- Season-by-season comparison
- Form trends
- Improvement/decline indicators

---

### Scenario 10: Ultimate Pressure Test
**Goal**: Hardest possible conditions

**Filters**:
```
Season: [2025]
Ground: All
Team: [Strongest opponent, e.g., Gujarat Titans]
Venue Type: Away
Innings: 2
```

**What You Get**:
- Chasing away from home
- Against top team
- Current season
- True test of capability

**Use When**:
- Identifying mental strength
- Clutch performance analysis
- High-pressure player selection

---

## Pro Tips

### 🎯 Tip 1: Start Broad, Then Narrow
```
Start: All filters = "All"
Step 1: Add season filter
Step 2: Add venue type if pattern unclear
Step 3: Add specific team/ground only if needed
```

### 📊 Tip 2: Maintain Sample Size
```
Good: 50+ records after filtering
Okay: 20-49 records (use with caution)
Poor: <20 records (statistical significance questionable)
```

### 🤖 Tip 3: AI Works Better with Context
```
Filtered: Season=2025, Venue=Home
AI Question: "Why is performance better at home in 2025?"
Result: AI provides season and venue-specific insights
```

### ⚡ Tip 4: Performance Optimization
```
Fast: Single season + venue type
Medium: Multiple teams/grounds
Slow: Very specific multi-ground + multi-team
```

### 🔄 Tip 5: Reset and Compare
```
Analysis 1: With filters → save insights
Reset: All filters to "All"
Analysis 2: Without filters → compare
Insight: Understand filter impact
```

---

## Common Filter Combinations

### For Coaches
```yaml
Match Preparation:
  Season: [Current]
  Team: [Opponent]
  Ground: [Match venue]
  
Squad Selection:
  Season: [Current]
  Venue Type: [Upcoming match type]
  
Form Check:
  Season: [Current]
  Innings: [Team batting preference]
```

### For Analysts
```yaml
Trend Analysis:
  Season: [Multiple seasons]
  Ground: [Specific]
  
Pattern Recognition:
  Season: [Current]
  Ground: [All]
  Team: [All]
  
Deep Dive:
  Season: [Specific]
  Ground: [Specific]
  Team: [Specific]
  Innings: [Specific]
```

### For Fantasy Players
```yaml
Player Selection:
  Season: [Current]
  Ground: [Next match venue]
  Venue Type: [Home/Away]
  
Captain Choice:
  Season: [Current]
  Team: [Opponent]
  Innings: [Batting order]
```

---

## Troubleshooting Filters

### ❌ "No data found"
```
Problem: Filters too restrictive
Solution: Remove one filter at a time
Priority: Start by changing to "All":
  1. Team filter (most restrictive)
  2. Ground filter
  3. Venue type
  4. Keep season/innings
```

### ⚠️ Very Low Record Count
```
Problem: <20 records
Solution: Broaden filters
Action: 
  - Change multi-select to "All"
  - Use multiple seasons
  - Remove ground restriction
```

### 🐌 Slow Performance
```
Problem: Too many filters/data
Solution: Be more specific
Action:
  - Use single season
  - Limit ground/team selections
  - Apply filters once, analyze multiple aspects
```

---

## Real-World Examples

### Example 1: IPL Final Preparation
```
Scenario: CSK vs MI final at Wankhede
Filters: Season=[2025], Ground=[Wankhede], Team=[Mumbai Indians]
Analysis: Batsman vs Bowling Type (MI's key bowlers)
AI Question: "What are CSK batsmen weaknesses against MI bowlers at Wankhede?"
```

### Example 2: Death Overs Strategy
```
Scenario: Need finisher for chasing
Filters: Season=[2025], Innings=[2]
Analysis: Head-to-Head (potential finisher vs death bowlers)
Look for: High SR after over 15
AI Question: "Who are the best death overs finishers in 2025?"
```

### Example 3: Spin-Friendly Venue
```
Scenario: Match at Chepauk (spin-friendly)
Filters: Ground=[MA Chidambaram Stadium], Season=[2024,2025]
Analysis: Batsman vs Bowling Type (off break, leg break)
AI Question: "How to play spin at Chepauk effectively?"
```

---

**Remember**: Filters are powerful tools. Use them wisely to unlock insights hidden in your data! 🏏📊
