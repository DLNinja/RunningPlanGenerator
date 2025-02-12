from django.shortcuts import render, HttpResponse, redirect
from .models import TrainingPlan, TrainingPlanReq
from .forms import TrainingPlanForm
from .solver import Solver
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Get the authenticated user
            login(request, user)  # Log in the user
            return redirect("/")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# Create your views here.
def home(request):
    return render(request, "home.html")


def generate_training_plan(request):
    if request.user.is_authenticated:  # Ensure the user is logged in
        username = request.user.username  # Get the username
        user_id = request.user.id
        if request.method == 'POST':
            form = TrainingPlanForm(request.POST)
            if form.is_valid():
                # Get the inputs from the form
                # user = request.POST.get('user')
                goal_distance = int(request.POST.get('goal_distance'))
                current_longest_run = int(request.POST.get('current_longest_run'))
                num_weeks = int(request.POST.get('num_weeks'))

                if goal_distance <= 0 or current_longest_run < 0 or num_weeks <= 0:
                    return render(request, 'training_plan_form.html', {
                        'form': form,
                        'error': "You can't select a negative distance!",
                    })

                if num_weeks < 4:
                    return render(request, 'training_plan_form.html', {
                        'form': form,
                        'error': "Number of weeks should be 4 at minimum!",
                    })

                current_longest_run = max(current_longest_run, 5)

                long_run_day = int(request.POST.get('long_run_day'))

                selected_non_running_days = request.POST.getlist('non_running_days')
                if len(selected_non_running_days) > 3:
                    return render(request, 'training_plan_form.html', {
                        'form': form,
                        'error': "You can select a maximum of 3 non-running days.",
                    })

                non_running_days = [0 if str(i) in selected_non_running_days else 1 for i in range(7)]

                if non_running_days[long_run_day] == 0:
                    return render(request, 'training_plan_form.html', {
                        'form': form,
                        'error': "You can't put the long run on non-running days'.",
                    })

                req = TrainingPlanReq(goal_distance, current_longest_run, num_weeks, non_running_days, long_run_day)

                daily_distances, long_run_distances = Solver.generate_plan(req)

                if daily_distances is not None:

                    total_distances = [sum(daily_distance) for daily_distance in daily_distances]

                    training_plan = TrainingPlan(
                        user=username,
                        title=f"{username}'s Training Plan",
                        user_id=user_id,
                        goal_distance=goal_distance,
                        weekly_mileages=daily_distances,
                        long_run_distances=long_run_distances,
                        total_distance=total_distances,
                    )
                    training_plan.save()

                    #Redirect to result view with id
                    return redirect('training_plan_result', training_plan_id=training_plan.id)
                else:
                    return render(request, 'training_plan_form.html', {
                        'form': form,
                        'error': "No solution could be generated. Please adjust your inputs.",
                    })
        else:
            TrainingPlanForm()
        return render(request, 'training_plan_form.html')
    else:
        return redirect('login')


def training_plan_result(request, training_plan_id):
    if request.user.is_authenticated:  # Ensure the user is logged in
        username = request.user.username  # Get the username
        user_id = request.user.id
        try:
            training_plan = TrainingPlan.objects.get(id=training_plan_id)
            if training_plan.user_id != user_id:
                return redirect('')
        except TrainingPlan.DoesNotExist:
            return HttpResponse("Training plan not found.", status=404)

        # Prepare data for the template
        context = {
            "training_plan": training_plan,
            "weekly_mileages": [
                {"week_index": i + 1, "days": week, "total": sum(week)}
                for i, week in enumerate(training_plan.weekly_mileages)

            ],
            "long_run_distances": [
                {"week_index": i + 1, "distance": long_run}
                for i, long_run in enumerate(training_plan.long_run_distances)
            ],
            "error": None,
        }
        return render(request, "training_plan_result.html", context)
    else:
        return redirect('login')


def all_training_plans(request):
    if request.user.is_authenticated:  # Ensure the user is logged in
        username = request.user.username  # Get the username
        user_id = request.user.id

        training_plans = TrainingPlan.objects.filter(user=request.user)

        context = {
            'training_plans': training_plans,
        }

        return render(request, 'all_training_plans.html', context)
    return redirect('login')


@csrf_exempt
def update_plan_title(request, training_plan_id):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            training_plan = TrainingPlan.objects.get(id=training_plan_id, user=request.user)
            data = json.loads(request.body)
            new_title = data.get("title")
            if new_title:
                training_plan.title = new_title
                training_plan.save()
                return JsonResponse({"new_title": new_title})
            else:
                return JsonResponse({"error": "Invalid title"}, status=400)
        except TrainingPlan.DoesNotExist:
            return JsonResponse({"error": "Training plan not found"}, status=404)
    return JsonResponse({"error": "Unauthorized"}, status=401)


@csrf_exempt
def delete_training_plan(request, training_plan_id):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            training_plan = TrainingPlan.objects.get(id=training_plan_id, user=request.user)
            training_plan.delete()
            return JsonResponse({"message": "Training plan deleted successfully"})
        except TrainingPlan.DoesNotExist:
            return JsonResponse({"error": "Training plan not found"}, status=404)
    return JsonResponse({"error": "Unauthorized"}, status=401)