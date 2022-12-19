from django.db import models

from utils.new.Schedule import Schedule as ScheduleMaker


# The model representing a task schedule.
class Schedule(models.Model):
    # The total number of shifts.
    total_shift_amount = models.IntegerField(null=False)
    # The number of shifts per day.
    total_shifts_per_day = models.IntegerField(null=True)
    # The possible solutions.
    last_solutions = models.JSONField(null=True, default=dict, blank=True)

    # Generate a schedule.
    def reload_schedule(self):
        # The list of handlers.
        all_handlers = [handler.username for handler in self.plan.assigned_users.all()]
        # The schedule maker.
        schedule_maker = ScheduleMaker(
            num_of_shifts_total=self.total_shift_amount,
            num_of_shifts_per_day=self.total_shifts_per_day,
            list_of_people=all_handlers
        )
        # Iterate through each task.
        for task in self.tasks.all():
            # Add the tasks.
            schedule_maker.quick_add_task({
                # The task's name.
                'name': task.name,
                # The full list of people qualified for this task.
                'qualified_people': [handler.username for handler in task.qualified_members.filter(username__in=all_handlers)],
                # The tasks that this task overlaps with within a shift must not have the same person.
                'no_individual_with_tasks': [itask.name for itask in task.incompatible_person_tasks.all()],
                # The full list of shifts possible for this task to occur in.
                'valid_shifts': task.advanced_settings['valid_shifts'],
                # Minimum and maximum amount of people per task.
                'people_per_shift_task': task.advanced_settings['people_per_shift_task'],
                # This Tasks' cycle settings.
                'per_task_cycle_settings': task.advanced_settings['per_task_cycle_settings'],
                # The cycle settings.
                'per_person_cycle_settings': task.advanced_settings['per_person_cycle_settings'],
                # The sequential settings.
                'sequential_settings': task.advanced_settings['sequential_settings']
            })
        # Run the solver.
        self.last_solutions = schedule_maker.solve()
        # Save the model.
        self.save()
