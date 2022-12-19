from django.db import models, transaction
from scheduling.models.ScheduleModel import Schedule
from system.models.ClientModel import Client
from routing.models.RouteModel import Route
from nutrition.models.MenuModel import Menu


# The model representing a plan.
class Plan(models.Model):
    TODO = 'TODO'
    DONE = 'DONE'
    LOCK = 'LOCK'

    # The default progress status.
    DEFAULT_PROGRESS = {
        "general_info": TODO,
        "route_path": TODO,
        "general_team": TODO,
        "meals_schedule": LOCK,
        "meals_settings": TODO,
        "route_duration": LOCK,
        "meals_selection": LOCK,
        "assignments_options": LOCK,
        "assignments_schedule": LOCK,
        "assignments_settings": TODO
    }

    # The plan's name.
    name = models.CharField(max_length=200, null=False, blank=False)
    # The plan's description.
    description = models.TextField(max_length=100, null=False, blank=False)
    # The users assigned.
    assigned_users = models.ManyToManyField(Client, through='PlanAccess')
    # The plan information.
    plan_data = models.JSONField(default=dict, null=True, blank=True)

    # The plan information.
    plan_maker_progress = models.JSONField(default=None, null=True, blank=True)
    # The plan completion.
    plan_completion = models.BooleanField(default=False, null=False)
    # The sharing status.
    sharing_status = models.CharField(max_length=100, null=False, default='PUBLIC_END')


    # The meals plan.
    plan_meal = models.OneToOneField(Menu, on_delete=models.PROTECT, null=True, blank=True)

    # The plan's route.
    plan_route = models.OneToOneField(Route, on_delete=models.PROTECT, null=True, blank=True)

    # The plan's schedule.
    plan_schedule = models.OneToOneField(Schedule, on_delete=models.PROTECT, null=True, blank=True)

    # Override the on save.
    def save(self, *args, **kwargs):
        # Check if model is being created.
        if self.pk is None and self.plan_maker_progress is None:
            # Set the plan progress.
            self.plan_maker_progress = self.DEFAULT_PROGRESS.copy()
        # Check if all progress is "DONE".
        self.plan_completion = all(progress == Plan.DONE for progress in self.plan_maker_progress.values())
        # Call the super save.
        super(Plan, self).save(*args, **kwargs)

    # Completely delete a plan.
    def full_deletion(self):
        # Surround with a transaction.
        with transaction.atomic():
            # Delete the model.
            self.delete()
            # Check if section exists.
            if self.plan_schedule is not None:
                # Delete the schedule information.
                for task in self.plan_schedule.tasks.all():
                    # Delete all tasks.
                    task.delete()
                # Delete the schedule.
                self.plan_schedule.delete()
            # Check if section exists.
            if self.plan_meal is not None:
                # Delete the menu.
                self.plan_meal.delete()
            # Check if section exists.
            if self.plan_route is not None:
                # Delete the route information.
                for location in self.plan_route.stop_locations.all():
                    # Remove every location.
                    location.delete()
                # Remove the start and end location.
                self.plan_route.start_location.delete()
                self.plan_route.end_location.delete()
                # Delete the route.
                self.plan_route.delete()
