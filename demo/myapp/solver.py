from z3 import *
from .models import TrainingPlanReq


class Solver:

    @staticmethod
    def generate_plan(training_plan_req):
        # Inputs
        goal_distance = training_plan_req.goal_distance
        current_longest_run = training_plan_req.current_longest_run
        num_weeks = training_plan_req.num_weeks
        non_running_days = training_plan_req.non_running_days
        long_run_day = training_plan_req.long_run_day

        # Calculate weekly targets
        peak_week = num_weeks - 3
        peak_mileage = goal_distance * 1.5
        delta = (peak_mileage - current_longest_run) / peak_week  # Weekly increase
        taper = peak_mileage / 6  # Taper factor

        weekly_targets = []
        for w in range(num_weeks):
            if w <= peak_week:
                weekly_targets.append(current_longest_run + w * delta)
            else:
                weekly_targets.append(peak_mileage - (w - peak_week) * taper)

        # Z3 variables
        D = [[Int(f"D_{w}_{d}") for d in range(7)] for w in range(num_weeks)]  # Daily distances
        long_runs = [Int(f"L_{w}") for w in range(num_weeks)]  # Long run distances

        # Optimizer
        opt = Optimize()

        # Add constraints based on pre-calculated weekly targets
        for w in range(num_weeks):
            opt.add(Sum(D[w]) == int(weekly_targets[w]))  # Weekly mileage equals target
            #opt.add(long_runs[w] == z3_max([D[w][d] for d in range(7)]))  # Long run is the max run of the week
            opt.add(D[w][long_run_day] == long_runs[w])  # Long run on specified day
            for d in range(7):
                if non_running_days[d] == 0:  # Rest days
                    opt.add(D[w][d] == 0)
                else:  # Running days
                    opt.add(D[w][d] > 0)  # No negative distances

            # Long run constraints
            opt.add(long_runs[w] <= weekly_targets[w] / 2)  # Max 50% of weekly mileage
            if w > 0:
                opt.add(long_runs[w] >= long_runs[w - 1])  # Long runs should not decrease

        # Objective: Balance mileage across running days
        z3_abs = lambda x: If(x >= 0, x, -x)

        for w in range(num_weeks):
            opt.minimize(Sum([
                If(non_running_days[d] == 1,
                   z3_abs(D[w][d] - (weekly_targets[w] / 7)), 0)
                for d in range(7)
            ]))

        daily_distances = []  # List of lists to store distances for each week
        long_run_distances = []  # List to store long run distances for each week

        # Solve
        if opt.check() == sat:
            model = opt.model()

            for w in range(num_weeks):
                week_data = []
                for d in range(7):
                    # Evaluate and convert to Python integer
                    z3_value = model.eval(D[w][d])
                    python_value = z3_value.as_long() if z3_value is not None else 0
                    week_data.append(python_value)

                # Identify the maximum distance for the week and the corresponding day
                max_distance = max(week_data)
                max_day = week_data.index(max_distance)

                # If the max day is not the long run day, swap them
                if max_day != long_run_day:
                    week_data[max_day], week_data[long_run_day] = week_data[long_run_day], max_distance

                # Add corrected data to the results
                daily_distances.append(week_data)
                long_run_distances.append(week_data[long_run_day])

            return daily_distances, long_run_distances

        return None, None



