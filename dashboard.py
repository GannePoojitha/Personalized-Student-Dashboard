# frontend/dashboard.py
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.gridspec import GridSpec

# API configuration
API_BASE_URL = "http://localhost:5000/api"


def fetch_student_data():
    """
    Fetch student data from the backend API
    Returns JSON data or None if failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/students")
        response.raise_for_status()  # Raise exception for bad status codes
        print("✅ Successfully fetched data from API!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from API: {e}")
        print("⚠️  Please make sure the backend server is running!")
        return None


def create_dashboard(students_data):
    """
    Create the student dashboard visualization
    """
    if students_data is None:
        print("Cannot create dashboard without data. Exiting.")
        return

    # Create dataframes for visualization
    student_list = []
    assignments_data = []
    semester_data = []
    
    # Sample data for assignments and semesters (since API doesn't provide them yet)
    sample_assignments = {
        "puttu001": {"Math": 90, "ML": 85, "Python": 95, "DBMS": 88, "Algorithms": 92},
        "arya002": {"DBMS": 80, "CN": 88, "Java": 92, "OS": 85, "Web Tech": 90},
        "rohit003": {"Math": 75, "ML": 92, "Python": 88, "DBMS": 82, "Algorithms": 85},
        "priya004": {"DBMS": 94, "CN": 91, "Java": 89, "OS": 93, "Web Tech": 92}
    }
    
    sample_semesters = {
        "puttu001": {1: 8.5, 2: 8.8, 3: 9.0, 4: 9.1, 5: 9.2},
        "arya002": {1: 8.2, 2: 8.5, 3: 8.6, 4: 8.7},
        "rohit003": {1: 7.8, 2: 8.0, 3: 8.0, 4: 8.1, 5: 8.1},
        "priya004": {1: 9.0, 2: 9.2, 3: 9.3, 4: 9.4, 5: 9.4, 6: 9.5}
    }
    
    # Process student data from API
    for student in students_data:
        student_list.append({
            "ID": student['id'],
            "Name": student['name'],
            "Course": student['course_name'],
            "Attendance": student['attendance_percentage'],
            "CGPA": student.get('avg_score', 0),
            "Semester": 5,  # Default value
            "Performance": student['performance']
        })
        
        # Add sample assignments data
        sid = student['id']
        if sid in sample_assignments:
            for subject, score in sample_assignments[sid].items():
                assignments_data.append({
                    "ID": sid,
                    "Name": student['name'],
                    "Subject": subject,
                    "Score": score
                })
        
        # Add sample semester data
        if sid in sample_semesters:
            for semester_num, cgpa in sample_semesters[sid].items():
                semester_data.append({
                    "ID": sid,
                    "Name": student['name'],
                    "Semester": semester_num,
                    "CGPA": cgpa
                })
    
    student_df = pd.DataFrame(student_list)
    assignments_df = pd.DataFrame(assignments_data)
    semester_df = pd.DataFrame(semester_data)

    # Set the style and color palette
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (14, 10)
    plt.rcParams['font.size'] = 10
    custom_palette = sns.color_palette("viridis", 10)
    sns.set_palette(custom_palette)

    # Create the enhanced dashboard
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(4, 3, figure=fig)

    # 1. Student CGPA Bar Chart (Top Left)
    ax1 = fig.add_subplot(gs[0, 0])
    sns.barplot(x="Name", y="CGPA", data=student_df, ax=ax1, palette="viridis")
    ax1.set_title("Student CGPA Comparison")
    ax1.set_ylim(0, 10)
    for i, v in enumerate(student_df["CGPA"]):
        ax1.text(i, v + 0.1, f"{v}", ha='center')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)

    # 2. Attendance Comparison (Top Middle)
    ax2 = fig.add_subplot(gs[0, 1])
    sns.barplot(x="Name", y="Attendance", data=student_df, ax=ax2, palette="rocket")
    ax2.set_title("Student Attendance (%)")
    ax2.set_ylim(0, 100)
    for i, v in enumerate(student_df["Attendance"]):
        ax2.text(i, v + 1, f"{v}%", ha='center')
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)

    # 3. Assignment Performance Heatmap (Top Right)
    pivot_df = assignments_df.pivot(index="Name", columns="Subject", values="Score")
    ax3 = fig.add_subplot(gs[0, 2])
    sns.heatmap(pivot_df, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Score'}, ax=ax3)
    ax3.set_title("Assignment Scores by Subject")

    # 4. CGPA vs Attendance Scatter (Middle Left)
    ax4 = fig.add_subplot(gs[1, 0])
    sns.scatterplot(x="CGPA", y="Attendance", data=student_df, s=100, ax=ax4)
    for i, row in student_df.iterrows():
        ax4.text(row["CGPA"] + 0.05, row["Attendance"], row["Name"])
    ax4.set_title("CGPA vs. Attendance")
    ax4.set_xlim(7, 10)
    ax4.set_ylim(70, 100)

    # 5. Course Distribution Pie Chart (Middle Middle)
    ax5 = fig.add_subplot(gs[1, 1])
    course_counts = student_df["Course"].value_counts()
    ax5.pie(course_counts, labels=course_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=sns.color_palette("Set3", len(course_counts)))
    ax5.set_title("Student Distribution by Course")

    # 6. Average Score by Subject (Middle Right)
    ax6 = fig.add_subplot(gs[1, 2])
    subject_avg = assignments_df.groupby("Subject")["Score"].mean().reset_index()
    sns.barplot(x="Subject", y="Score", data=subject_avg, ax=ax6, palette="mako")
    ax6.set_title("Average Score by Subject")
    ax6.set_ylim(0, 100)
    for i, v in enumerate(subject_avg["Score"]):
        ax6.text(i, v + 1, f"{v:.1f}", ha='center')
    ax6.tick_params(axis='x', rotation=45)

    # 7. Semester-wise CGPA Trend (Bottom Left)
    ax7 = fig.add_subplot(gs[2, 0])
    for name in semester_df['Name'].unique():
        student_data = semester_df[semester_df['Name'] == name]
        ax7.plot(student_data['Semester'], student_data['CGPA'], marker='o', label=name)

    ax7.set_xlabel("Semester")
    ax7.set_ylabel("CGPA")
    ax7.set_title("Semester-wise CGPA Trend")
    ax7.legend()
    ax7.grid(True)

    # 8. Performance Radar Chart (Bottom Middle)
    ax8 = fig.add_subplot(gs[2, 1], polar=True)
    student_name = "Puttu"
    student_subjects = assignments_df[assignments_df['Name'] == student_name]
    categories = list(student_subjects['Subject'].values)
    N = len(categories)

    # Values for the selected student
    values = list(student_subjects['Score'].values)

    # Repeat first value to close the circle
    values += values[:1]

    # Calculate angles for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Plot data
    ax8.plot(angles, values, linewidth=1, linestyle='solid', label=student_name)
    ax8.fill(angles, values, alpha=0.1)

    # Add labels
    ax8.set_xticks(angles[:-1])
    ax8.set_xticklabels(categories)
    ax8.set_title(f"Skills Radar Chart for {student_name}")
    ax8.set_ylim(0, 100)

    # 9. Peer Comparison Chart (Bottom Right)
    ax9 = fig.add_subplot(gs[2, 2])

    # Calculate average scores for each subject
    subject_avgs = assignments_df.groupby('Subject')['Score'].mean().reset_index()

    # Get individual student scores
    student_scores = assignments_df[assignments_df['Name'] == student_name]

    # Merge to compare
    comparison_df = pd.merge(student_scores, subject_avgs, on='Subject', suffixes=('_student', '_avg'))
    # Plot comparison
    x = np.arange(len(comparison_df['Subject']))
    
    width = 0.35

    ax9.bar(x - width / 2, comparison_df['Score_student'], width, label=student_name)
    ax9.bar(x + width / 2, comparison_df['Score_avg'], width, label='Class Average')
    ax9.set_xlabel('Subjects')
    ax9.set_ylabel('Scores')
    ax9.set_title(f'{student_name} Performance vs Class Average')
    ax9.set_xticks(x)
    ax9.set_xticklabels(comparison_df['Subject'], rotation=45)
    ax9.legend()

    # 10. Individual Student Performance Cards (Very Bottom)
    ax10 = fig.add_subplot(gs[3, :])
    ax10.axis('off')

    # Create text boxes for student cards
    cols = 2
    rows = int(np.ceil(len(students_data) / cols))
    cell_width = 1.0 / cols
    cell_height = 1.0 / rows

    for i, student in enumerate(students_data):
        # Get assignments for this student
        sid = student['id']
        student_assignments = sample_assignments.get(sid, {})
        assignments_str = ", ".join([f"{subj}: {score}" for subj, score in 
                                    student_assignments.items()])
        
        student_card = f"""
        {student['name']} ({sid})
        Course: {student['course_name']}
        Attendance: {student['attendance_percentage']}%
        CGPA: {student.get('avg_score', 0):.1f}
        Performance: {student['performance']}
        Assignments: {assignments_str}
        """
        
        col = i % cols
        row = i // cols
        
        ax10.text(
            col * cell_width + cell_width / 2,
            1 - (row * cell_height + cell_height / 2),
            student_card,
            transform=ax10.transAxes,
            ha='center',
            va='center',
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor=custom_palette[i],
                alpha=0.3
            )
        )

    plt.suptitle("Enhanced Student Dashboard Visualization (Live from API)", fontsize=20, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    # Generate a summary table
    print("\n===== STUDENT DASHBOARD SUMMARY =====")
    summary_df = student_df[["Name", "Course", "Attendance", "CGPA", "Performance"]]
    print(summary_df.to_string(index=False))

    # Calculate and print statistics
    print("\n===== PERFORMANCE STATISTICS =====")
    print(f"Average CGPA: {student_df['CGPA'].mean():.2f}")
    print(f"Average Attendance: {student_df['Attendance'].mean():.2f}%")
    print(f"Highest CGPA: {student_df['CGPA'].max():.2f} "
          f"({student_df.loc[student_df['CGPA'].idxmax()]['Name']})")
    print(f"Highest Attendance: {student_df['Attendance'].max()}% "
          f"({student_df.loc[student_df['Attendance'].idxmax()]['Name']})")

    # Add personalized recommendations
    print("\n===== PERSONALIZED RECOMMENDATIONS =====")
    for student in students_data:
        sid = student['id']
        if sid in sample_assignments:
            student_assignments = sample_assignments[sid]
            weakest_subject = min(student_assignments.items(), key=lambda x: x[1])
            strongest_subject = max(student_assignments.items(), key=lambda x: x[1])
            
            attendance = student['attendance_percentage']
            cgpa = student.get('avg_score', 0)
            
            print(f"\n{student['name']}:")
            print(f"  - Focus on improving {weakest_subject[0]} "
                  f"(score: {weakest_subject[1]})")
            print(f"  - Maintain strength in {strongest_subject[0]} "
                  f"(score: {strongest_subject[1]})")
            
            # Attendance recommendation
            if attendance < 85:
                print(f"  - Try to improve attendance (current: {attendance}%)")
            elif attendance > 95:
                print(f"  - Excellent attendance (current: {attendance}%) - keep it up!")
            
            # CGPA recommendation
            if cgpa < 8.0:
                print(f"  - Consider seeking academic guidance (CGPA: {cgpa:.1f})")
            elif cgpa > 9.0:
                print(f"  - Outstanding academic performance (CGPA: {cgpa:.1f})!")


def main():
    """Main function to run the dashboard"""
    print("📊 Student Dashboard Frontend")
    print("=============================")
    
    # Fetch data from backend
    students_data = fetch_student_data()
    
    if students_data:
        # Create and display the dashboard
        create_dashboard(students_data)
    else:
        print("Failed to load data. Exiting.")


if __name__ == '__main__':
    main()