import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('research_data/exit_questionnaire_15_users.csv')

df_15_users = df.head(15)


preference_counts = df_15_users['futurePreference'].value_counts()

approach_mapping = {
    'Task 1': 'Article-First',
    'Task 2': 'Model-First'
}

approaches = []
user_counts = []

for task in ['Task 1', 'Task 2']:
    approaches.append(approach_mapping[task])
    user_counts.append(preference_counts.get(task, 0))

print(f"Data analysis:")
print(f"Article-First (Task 1): {user_counts[0]} users")
print(f"Model-First (Task 2): {user_counts[1]} users")
print(f"Total users: {sum(user_counts)}")

plt.figure(figsize=(10, 6))
colors = ['#FF6B6B', '#4ECDC4'] 
bars = plt.bar(approaches, user_counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)

plt.title('User Preferences from Exit Questionnaire', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Approach', fontsize=12, fontweight='bold')
plt.ylabel('Number of Users', fontsize=12, fontweight='bold')

plt.ylim(0, max(user_counts) + 2)
plt.yticks(range(0, max(user_counts) + 3))

for bar, count in zip(bars, user_counts):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
             str(count), ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add grid for better readability
plt.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()

plt.savefig('dissertation_images/user_preferences_chart.png', dpi=300, bbox_inches='tight')
plt.savefig('dissertation_images/user_preferences_chart.jpg', dpi=300, bbox_inches='tight')

print(f"\nChart saved successfully to:")
print(f"- dissertation_images/user_preferences_chart.png")
print(f"- dissertation_images/user_preferences_chart.jpg")

plt.show()