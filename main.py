import random
from tabulate import tabulate

configs = {
    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "groups": ["TK", "TTP1", "TTP2", "MI", "MI2"],
    "subjects": ["Algebra", "Math Anal.", "Geometry", "Programming", "Discrete Math",
           "Algorithms", "Data Str.", "Prob. Th.", "Data Analysis", "Num. Math."],
    "teachers": ["Jake", "Connor", "Callum", "Jacob", "Kyle", "Charlie", "Jacob", "Peter", "Rhys", "Oliver"],
    "lessons": ["1", "2", "3"],
    "rooms": ["18", "19", "20", "21", "22"]
}

class Schedule:

    NUMBER_SUBJECTS_PER_TEACHER = 5
    NUMBER_ROOMS_PER_TEACHER = 5
    NUMBER_SUBJECTS_PER_GROUP = 4

    groups = configs["groups"]
    teachers = configs["teachers"]
    lessons = configs["lessons"]
    rooms = configs["rooms"]
    days = configs["days"]
    subjects = configs["subjects"]

    n_groups = len(groups)
    n_lessons = len(lessons)
    n_teachers = len(teachers)
    n_rooms = len(rooms)
    n_days = len(days)    
    n_subjects = len(subjects)

    
    def __init__(self):

        self.group_table = {}

        for g_name in self.groups:
            self.group_table[g_name] = [[None] * 3 for i in range(self.n_days * self.n_lessons)]

        self.teacher_subject_specs = [set([(si ** 2 + ti ** 2) % self.n_subjects for si in range(self.NUMBER_SUBJECTS_PER_TEACHER)])
                              for ti in range(self.n_teachers)]

        self.subject_teacher_specs = [[] for s in self.subjects]
        for t_id, subs in enumerate(self.teacher_subject_specs):
            for s_idx in subs:
                self.subject_teacher_specs[s_idx].append(t_id)

        self.subject_teacher_specs = [set(arr) for arr in self.subject_teacher_specs]

        self.teacher_room_plan = [set([(si ** 2 +  ti) % self.n_rooms for si in range(self.NUMBER_ROOMS_PER_TEACHER)])
                              for  ti in range(self.n_teachers)]

        self.room_teacher_specs = [[] for s in self.subjects]
        for t_id, rms in enumerate(self.teacher_room_plan):
            for r_idx in rms:
                self.room_teacher_specs[r_idx].append(t_id)

        self.room_teacher_specs = [set(arr) for arr in self.room_teacher_specs]

        self.subject_per_groups = {self.groups[gi]: set(random.randint(0, self.n_subjects+1) for si in range(self.NUMBER_SUBJECTS_PER_GROUP))
                                    for  gi in range(self.n_groups)}

        self.conditions = [self.check_room_per_lesson, self.check_teacher_per_lesson]

    def check_teacher_per_lesson(self, lesson_i, teacher_idx):

        for g_name in self.groups:
            if self.group_table[g_name][lesson_i][0] == teacher_idx:
                return False
        return True

    
    def check_room_per_lesson(self, lesson_i, room_idx):

        for g_name in self.groups:
            if self.group_table[g_name][lesson_i][1] == room_idx:
                return False
        return True

    def check_table_subject(self):
        
        for g_name, table in self.group_table.items():
            all_subj = []
            for less in table:
                all_subj.append(less[2])
            all_subj = set(all_subj)
            print(self.subject_per_groups[g_name] - all_subj, all_subj)
            if len(self.subject_per_groups[g_name] - all_subj) != 0:
                return False
        return True
    
    def forward_checking_teacher(self, i):
        ds_idx = i % (self.n_days * self.n_lessons)
        teachers_used = set(t[ds_idx][0] for t in self.group_table.values())
        teachers = set(range(self.n_teachers))

        l = list(teachers - teachers_used)

        if heuristics["forward checking"]:
            return random.sample(l, len(l))
        else:
            return random.sample(list(teachers), self.n_teachers)

    def minimum_remaining_values_teacher(self, teachers, i):
        if not heuristics["minimum_remaining_values"]:
            return teachers

        ds_idx = i % (self.n_days * self.n_lessons)
        rooms_used = set(t[ds_idx][1] for t in self.group_table.values())
        teachers = [(t_idx, len(self.teacher_room_plan[t_idx] - rooms_used)) for t_idx in teachers]
        teachers = sorted(teachers, key=lambda x: x[1])
        teachers = [t_idx for t_idx, len_t in teachers]
        return teachers

    def degree_heuristic_subject(self, teachers, i):
        if not heuristics["degree_heuristic"]:
            return teachers

        ds_idx = i % (self.n_days * self.n_lessons)
        rooms_used = set(t[ds_idx][1] for t in self.group_table.values())
        teachers = [(t_idx, len(self.teacher_room_plan[t_idx] - rooms_used)) for t_idx in teachers]
        teachers = sorted(teachers, key=lambda x: x[1], reverse=True)
        teachers = [t_idx for t_idx, len_t in teachers]
        return teachers

    def least_constraining_value(self, subs, rooms):
        subjects_scores = []
        for s_idx in subs:
            subjects_scores.append([s_idx, 0])
            for r_idx in rooms:
                subjects_scores[-1][1] += len(self.room_teacher_specs[r_idx].intersection(self.subject_teacher_specs[s_idx]))
        if heuristics["least_constraining_value"]:
            for s, _ in sorted(subjects_scores, key=lambda sc: sc[1]):
                yield s
        else:
            for s in random.sample(subs, len(subs)):
                yield s

    def get_cell(self, i):
        teachers = self.forward_checking_teacher(i)
        teachers = self.degree_heuristic_subject(teachers, i)
        for t_id in teachers:
            subjects = self.teacher_subject_specs[t_id]
            rooms = self.teacher_room_plan[t_id]
            
            for r_idx in random.sample(rooms, len(rooms)):
                for s_id in self.least_constraining_value(subjects, rooms):                
                    yield t_id, s_id, r_idx


    def backtracking(self, i=0):
        if i == self.n_days * self.n_lessons * self.n_groups:           
            return True
        
        gen = self.get_cell(i)
        
        if gen is None:
            return True
        if not heuristics["minimum_remaining_values"]:
            ds_idx = i % (self.n_days * self.n_lessons)
            g_name = self.groups[i // (self.n_days * self.n_lessons)]
        else:
            ds_idx = i // self.n_groups
            g_name = self.groups[i % self.n_groups]

        for v in gen:
            t_id, s_id, r_idx = v

            if not self.check_teacher_per_lesson(ds_idx, t_id):
                return False

            if not self.check_room_per_lesson(ds_idx, r_idx):
                return False

            self.group_table[g_name][ds_idx][0] = t_id
            self.group_table[g_name][ds_idx][1] = r_idx
            self.group_table[g_name][ds_idx][2] = s_id

            if self.backtracking(i+1):
                return True

            self.group_table[g_name][ds_idx] = [None] * 3
        
        return False


    def print(self):
        table = dict(indices=["Day", "Group"] + self.lessons)
        for d_idx, d_name in enumerate(self.days):
            table[(d_idx, 0)] = [d_name]
            for g in range(1, self.n_groups):
                table[(d_idx, g)] = [""]
            for g_idx, g_name in enumerate(self.groups):
                table[(d_idx, g_idx)].append(g_name)
                for l in range(self.n_lessons):
                    l = d_idx * self.n_lessons + l
                    lesson = (f"{self.subjects[self.group_table[g_name][l][2]]}\n"
                              f"Room: {self.rooms[self.group_table[g_name][l][1]]}\n"
                              f"Prof.: {self.teachers[self.group_table[g_name][l][0]]}")
                    table[(d_idx, g_idx)].append(lesson)
            table[(d_idx, -1)] = [""] * (2 + self.n_lessons)
        print(tabulate(table, tablefmt="fancy_grid"))

heuristics = {
    "forward checking": False,
    "minimum_remaining_values": False,
    "degree_heuristic": False,
    "least_constraining_value": False,
}

if __name__ == "__main__":
    from datetime import datetime

    schedule = Schedule()
    t1 = datetime.now()
    schedule.backtracking()
    print("without heuristics", datetime.now() - t1)

    heuristics["forward checking"] = True
    schedule = Schedule()
    t1 = datetime.now()
    schedule.backtracking()
    print("forward checking heuristics", datetime.now() - t1)

    heuristics["forward checking"] = False
    heuristics["minimum_remaining_values"] = True
    schedule = Schedule()
    t1 = datetime.now()
    schedule.backtracking()
    print("minimum_remaining_values heuristics", datetime.now() - t1)

    heuristics["minimum_remaining_values"] = False
    heuristics["degree_heuristic"] = True
    schedule = Schedule()
    t1 = datetime.now()
    schedule.backtracking()
    print("degree_heuristic heuristics", datetime.now() - t1)


    heuristics["degree_heuristic"] = False
    heuristics["least_constraining_value"] = True
    schedule = Schedule()
    t1 = datetime.now()
    schedule.backtracking()
    
    print("least_constraining_value heuristics", datetime.now() - t1)


    # schedule.print()
