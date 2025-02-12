from django.db import models

# Create your models here.

class Item(models.Model):
    content = models.CharField(max_length=100)


class TrainingPlan(models.Model):
    user_id = models.IntegerField()
    user = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    goal_distance = models.IntegerField()
    weekly_mileages = models.JSONField()
    long_run_distances = models.JSONField()
    total_distance = models.JSONField()

    def __str__(self):
        return f"Training Plan for {self.user} - Goal: {self.goal_distance} km"


class TrainingPlanReq:

    def __init__(self, goal_distance, current_longest_run, num_weeks, non_running_days, long_run_day):
        self.goal_distance = goal_distance
        self.current_longest_run = current_longest_run
        self.num_weeks = num_weeks
        self.non_running_days = non_running_days
        self.long_run_day = long_run_day
