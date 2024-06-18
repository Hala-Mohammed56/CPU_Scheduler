# Hala Mohammed - 1210312 -Sec 1
#-------------------------------------------------------------


class Process:
    def __init__(self, process_id, arrival, burst, priority_level, comeback):
        # Define process attributes
        self.process_id = process_id
        self.arrival = arrival
        self.burst = burst
        self.priority_level = priority_level
        self.comeback = comeback
        self.remaining_burst = burst
        self.remaining_priority = priority_level
        self.total_ready_time = 0
        self.total_wait_time = 0
        self.current_ready_time = 0
        self.current_wait_time = 0
        self.execution_time = 0
        self.is_started = False


#-------------------------------------------------------------


def calculate_times(process_list, schedule):
    # Make a dictionary that associates process IDs with process objects for convenience of use.
    process_dict = {process.process_id: process for process in process_list}
    wait_times = {process.process_id: 0 for process in process_list}
    turnaround_times = {process.process_id: 0 for process in process_list}

    last_finish_time = {process.process_id: 0 for process in process_list}
    # Calculate wait and turnaround times by iterating through the schedule.
    for process_id, start_time, end_time in schedule:
        process = process_dict[process_id]
        if last_finish_time[process_id] < process.arrival:
            wait_times[process_id] += (start_time - process.arrival)
        else:
            wait_times[process_id] += (start_time - last_finish_time[process_id])
        turnaround_times[process_id] = end_time - process.arrival
        last_finish_time[process_id] = end_time

    total_waiting_time = sum(wait_times.values())
    total_turnaround_time = sum(turnaround_times.values())
    num_processes = len(process_list)

    average_waiting_time = total_waiting_time / num_processes
    average_turnaround_time = total_turnaround_time / num_processes

    # Provide the average turnaround time and average waiting time that were calculated.
    return average_waiting_time, average_turnaround_time


#-------------------------------------------------------------

#prints a Gantt chart that shows the specified processes.
def print_gantt_chart(processes, title, part_number):
    print(f"Part {part_number}: Gantt Chart for {title}:")
    for i, (process_id, start_time, end_time) in enumerate(processes):
        print(f"PID: {process_id}, Start Execution at: {start_time}, CPU Release at: {end_time}")
    print("\n")


#-------------------------------------------------------------


# Non-preemptive Priority Scheduling with Round Robin
def non_preemptive_priority_scheduling_with_round_robin(process_list, total_execution_time, time_quantum):
    current_time = 0
    execution_order = []
    time_stamps = []
    ready_queue = []
    wait_queue = {}
    #copy of the process list
    process_list_copy = [Process(p.process_id, p.arrival, p.burst, p.priority_level, p.comeback) for p in process_list]  # Make a copy of the process list

    while current_time < total_execution_time:
        # Verify if any new processes have arrived and add them to the queue that is ready.
        for process in process_list_copy:
            if process.arrival <= current_time and not process.is_started:
                ready_queue.append(process)
                process.is_started = True
        # Move any processes whose I/O time has finished from the wait queue to the ready queue.
        for process, comeback_time in list(wait_queue.items()):
            if comeback_time <= current_time:
                ready_queue.append(process)
                del wait_queue[process]

        ready_queue.sort(key=lambda x: x.priority_level)# Sort the ready queue

        if ready_queue:
            current_process = ready_queue.pop(0)
            execution_order.append(current_process.process_id)
            time_stamps.append(current_time)
            # Give on the procedure for the allotted amount of time or until it is finished.
            if current_process.remaining_burst <= time_quantum:
                current_time += current_process.remaining_burst
                current_process.remaining_burst = 0
            else:
                current_time += time_quantum
                current_process.remaining_burst -= time_quantum
                ready_queue.append(current_process)
            # After execution, schedule the process to wait for its I/O burst time.
            wait_queue[current_process] = current_time + current_process.comeback
        else:
            current_time += 1

    time_stamps.append(total_execution_time)
    return execution_order, time_stamps


#-------------------------------------------------------------


# Preemptive Priority Scheduling with Aging
def preemptive_priority_scheduling_with_aging(process_list, total_execution_time, time_quantum):
    current_time = 0
    active_process = None
    execution_order = []
    time_stamps = []
    ready_queue = []
    aging_counter = {}
    # Set up the aging counters in the process list for each process ID.
    for process in process_list:
        aging_counter[process.process_id] = 0

    while current_time < total_execution_time:
        # Verify if any new processes have arrived and add them to the queue that is ready.
        for process in process_list:
            if process.arrival <= current_time and not process.is_started:
                ready_queue.append(process)
                process.is_started = True
                aging_counter[process.process_id] = 0

        ready_queue.sort(key=lambda x: (x.remaining_priority, x.arrival))

        if ready_queue:
            # From the ready queue, pick the process with the highest priority.
            next_process = ready_queue[0]
            if not active_process or active_process.remaining_priority > next_process.remaining_priority:
                if active_process:
                    ready_queue.append(active_process)
                active_process = next_process
                ready_queue.remove(next_process)
                execution_order.append(active_process.process_id)
                time_stamps.append(current_time)
        # Age processes in the ready queue and, if they are left waiting too long, lower their priority.
        for process in ready_queue:
            aging_counter[process.process_id] += 1
            if aging_counter[process.process_id] >= 5:
                process.remaining_priority = max(process.remaining_priority - 1, 0)
                aging_counter[process.process_id] = 0
        # Process the ongoing task until it is finished or for the allotted amount of time.
        if active_process:
            if active_process.remaining_burst <= time_quantum:
                current_time += active_process.remaining_burst
                active_process.remaining_burst = 0
                active_process = None
            else:
                current_time += time_quantum
                active_process.remaining_burst -= time_quantum
                ready_queue.append(active_process)
                active_process = None
        else:
            current_time += 1

    time_stamps.append(total_execution_time)
    return execution_order, time_stamps


#-------------------------------------------------------------


# Multilevel Feedback Queue Scheduling
def multilevel_feedback_queue(process_list, total_execution_time):
    current_time = 0
    execution_order = []
    time_stamps = []
    feedback_queues = [[] for _ in range(3)]
    time_quantums = [8, 16, 32]
    process_list_copy = [Process(p.process_id, p.arrival, p.burst, p.priority_level, p.comeback) for p in process_list]  # Make a copy of the process list

    # Check recently received processes and add them to the queue for initial comments.
    while current_time < total_execution_time:
        for process in process_list_copy:
            if process.arrival <= current_time and not process.is_started:
                feedback_queues[0].append(process)
                process.is_started = True

        for i in range(3):
            if feedback_queues[i]:
                active_process = feedback_queues[i].pop(0)
                execution_order.append(active_process.process_id)
                time_stamps.append(current_time)

                # Run out the procedure for the entire allotted time or until it is finished.
                if active_process.remaining_burst <= time_quantums[i]:
                    current_time += active_process.remaining_burst
                    active_process.remaining_burst = 0
                else:
                    current_time += time_quantums[i]
                    active_process.remaining_burst -= time_quantums[i]
                    if i < 2:
                        feedback_queues[i + 1].append(active_process)
                    else:
                        feedback_queues[i].append(active_process)
                break
        else:
            current_time += 1 # No processes are prepared for execution; display the passing of time

    time_stamps.append(total_execution_time)
    return execution_order, time_stamps


#-------------------------------------------------------------


def main():
    process_list = [
        Process("P1", 0, 15, 3, 5),
        Process("P2", 1, 23, 2, 14),
        Process("P3", 3, 14, 3, 6),
        Process("P4", 4, 16, 1, 15),
        Process("P5", 6, 10, 0, 13),
        Process("P6", 7, 22, 1, 4),
        Process("P7", 8, 28, 2, 10),
    ]
    total_time = 300

    print("/////////////////////////////////// Welcome to My CPU Scheduler ///////////////////////////////////")

    # print the process information
    print("      ------------------------------------------------------------------------------------")
    print("       Process       Arrival Time        Burst Time       I/O Burst Time       Priority")
    print("      ------------------------------------------------------------------------------------")
    for proc in process_list:
        print(
            f"         {proc.process_id}                 {proc.arrival}                 {proc.burst}                   {proc.comeback}                  {proc.priority_level}")
    print("\n")

    # Non-preemptive Priority Scheduling with Round Robin
    np_pr_sch_rr_processes, np_pr_sch_rr_times = non_preemptive_priority_scheduling_with_round_robin(process_list, total_time, 2)
    print_gantt_chart(list(zip(np_pr_sch_rr_processes, np_pr_sch_rr_times[:-1], np_pr_sch_rr_times[1:])),
                      "Non-preemptive Priority Scheduling with Round Robin", 1)
    np_pr_sch_rr_schedule = list(zip(np_pr_sch_rr_processes, np_pr_sch_rr_times[:-1], np_pr_sch_rr_times[1:]))
    np_pr_sch_rr_avg_wt, np_pr_sch_rr_avg_tat = calculate_times(process_list, np_pr_sch_rr_schedule)
    print(f"Average Waiting Time: {np_pr_sch_rr_avg_wt:.2f}, Average Turnaround Time: {np_pr_sch_rr_avg_tat:.2f}")
    print("\n")
    print("------------------------------------------------------------------------------------")
    print("\n")

    # Preemptive Priority Scheduling with Aging
    pr_sch_age_processes, pr_sch_age_times = preemptive_priority_scheduling_with_aging(process_list, total_time, 2)
    print_gantt_chart(list(zip(pr_sch_age_processes, pr_sch_age_times[:-1], pr_sch_age_times[1:])), "Preemptive Priority Scheduling with Aging", 2)
    pr_sch_age_schedule = list(zip(pr_sch_age_processes, pr_sch_age_times[:-1], pr_sch_age_times[1:]))
    pr_sch_age_avg_wt, pr_sch_age_avg_tat = calculate_times(process_list, pr_sch_age_schedule)
    print(f"Average Waiting Time: {pr_sch_age_avg_wt:.2f}, Average Turnaround Time: {pr_sch_age_avg_tat:.2f}")
    print("\n")
    print("------------------------------------------------------------------------------------")
    print("\n")

    # Multilevel Feedback Queue Scheduling
    mlfq_processes, mlfq_times = multilevel_feedback_queue(process_list, total_time)
    print_gantt_chart(list(zip(mlfq_processes, mlfq_times[:-1], mlfq_times[1:])), "Multilevel Feedback Queue Scheduling", 3)
    mlfq_schedule = list(zip(mlfq_processes, mlfq_times[:-1], mlfq_times[1:]))
    mlfq_avg_wt, mlfq_avg_tat = calculate_times(process_list, mlfq_schedule)
    print(f"Average Waiting Time: {mlfq_avg_wt:.2f}, Average Turnaround Time: {mlfq_avg_tat:.2f}")
    print("\n")
    print("------------------------------------------------------------------------------------")
    print("\n")


#-------------------------------------------------------------


if __name__ == "__main__":
    main()


