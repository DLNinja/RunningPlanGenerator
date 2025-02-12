# Running Plan Generator 🏃‍♂️📅  

A web application that generates personalized running training plans using the **Z3 SMT Solver** to optimize weekly mileage distribution. Built with **Django**, it provides users with structured training schedules based on their current fitness level and race goals.  

---

## 🚀 Features  

✅ **User Authentication**: Signup, login, and manage accounts.  
✅ **Personalized Training Plans**: Generate structured running plans based on input goals.  
✅ **Z3 Solver Optimization**: Uses constraint solving to distribute weekly mileage effectively.  
✅ **Plan Management**: View, edit, and delete training plans.  

---

## 🏗️ Technologies Used  

- **Backend**: Django, Python  
- **Frontend**: HTML, CSS, JavaScript  
- **Database**: SQLite  
- **Optimization Engine**: Z3 SMT Solver  

---

## 🎯 How It Works  

1. **User Authentication**:  
   - Users can **sign up** or **log in** to access the training plan generator.  

2. **Creating a Training Plan**:  
   - Users enter:  
     - **Current longest run distance**  
     - **Goal distance** (e.g., 10K, Half Marathon, Marathon)  
     - **Training duration** (number of weeks)  
     - **Preferred long run day**  
     - **Rest days**  
   - The system processes the input using **Z3** and returns an optimized training schedule.  

3. **Viewing and Managing Plans**:  
   - Users can **view their generated plans**, select plans from a list, and manage their progress.  

---

## 🧠 The Z3 Solver Approach  

The **Z3 SMT Solver** is used to optimize weekly mileage while enforcing:  

- **Gradual weekly increase**: Ensuring steady progress without excessive jumps.  
- **Peak week strategy**: Reaching peak mileage **3 weeks before the goal race**.  
- **Tapering**: Reducing mileage in the final weeks to prevent overtraining.  
- **Long run constraints**: Ensuring long runs do not exceed **50% of weekly mileage**.  
- **Rest days enforcement**: Preventing runs on user-selected rest days.  

### 🔎 Example Constraints in Z3  
```python
opt.add(Sum(D[w]) == int(weekly_targets[w]))  # Ensure weekly mileage matches the target
opt.add(D[w][long_run_day] == long_runs[w])  # Assign long run to the specified day
opt.add(long_runs[w] <= weekly_targets[w] / 2)  # Long run <= 50% of total mileage
opt.add(D[w][d] == 0 if non_running_days[d] == 0 else D[w][d] >= 0)  # Enforce rest days
