from django import forms


class TrainingPlanForm(forms.Form):
    goal_distance = forms.IntegerField()
    current_longest_run = forms.IntegerField()
    num_weeks = forms.IntegerField()
    non_running_days = forms.JSONField()
    long_run_day = forms.IntegerField()
