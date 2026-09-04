---
name: add-student-crud-feature
description: Added a CRUD feature for managing students in the Users tab, inside a section labeled 'Add Student'
metadata:
  type: project
---

Added a CRUD (Create, Read, Update, Delete) feature for managing students in the Users tab. The feature is contained within a LabelFrame labeled 'Add Student' and includes:

- Input fields for student name, grade level, and section
- Buttons for adding, updating, and deleting students
- A Treeview to display the list of students
- Functionality to load students from the database and reflect changes in real-time

The feature uses the existing database connection and creates a 'students' table if it doesn't exist.

**How to apply:** This feature can be extended by adding validation or changing input types (e.g., using Combobox for grade level and section). It is located in the create_users_tab method and helper methods in ashscom_gui.py.